from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from core.ratelimit import limiter_debit
from geo.models import Commune

from .forms import AnnonceForm
from .models import Annonce, Categorie, ClicAffichageNumero


def liste(request):
    """Recherche et filtres — SRS §3.4 (mots-clés, catégorie, commune, prix par devise)."""
    annonces = (
        Annonce.objects.actives()
        .select_related("categorie", "commune", "vendeur")
        .prefetch_related("photos")
    )

    q = request.GET.get("q", "").strip()
    if q:
        annonces = annonces.filter(Q(titre__icontains=q) | Q(description__icontains=q))

    categorie_active = None
    slug_categorie = request.GET.get("categorie", "")
    if slug_categorie:
        categorie_active = Categorie.objects.filter(slug=slug_categorie, actif=True).first()
        if categorie_active:
            annonces = annonces.filter(categorie=categorie_active)

    slug_commune = request.GET.get("commune", "")
    if slug_commune:
        annonces = annonces.filter(commune__slug=slug_commune)

    # Décision Q4 : fourchette de prix uniquement au sein d'une devise.
    devise = request.GET.get("devise", "")
    if devise in dict(Annonce.Devise.choices):
        annonces = annonces.filter(devise=devise)
        for parametre, filtre in (("prix_min", "prix__gte"), ("prix_max", "prix__lte")):
            valeur = request.GET.get(parametre, "")
            try:
                annonces = annonces.filter(**{filtre: float(valeur)}) if valeur else annonces
            except ValueError:
                pass

    tri = request.GET.get("tri", "")
    if tri in ("prix", "-prix") and devise:
        annonces = annonces.order_by(tri, "-date_publication")

    page = Paginator(annonces, 20).get_page(request.GET.get("page"))
    contexte = {
        "page": page,
        "q": q,
        "categorie_active": categorie_active,
        "categories": Categorie.objects.filter(actif=True),
        "communes": Commune.objects.filter(actif=True, ville__actif=True),
        "slug_commune": slug_commune,
        "devise": devise,
        "prix_min": request.GET.get("prix_min", ""),
        "prix_max": request.GET.get("prix_max", ""),
        "tri": tri,
    }
    return render(request, "annonces/liste.html", contexte)


def detail(request, pk, slug):
    annonce = get_object_or_404(
        Annonce.objects.select_related("categorie", "commune", "vendeur").prefetch_related("photos"),
        pk=pk,
    )
    visible = annonce.statut == Annonce.Statut.PUBLIEE and not annonce.est_expiree
    est_vendeur = request.user.is_authenticated and request.user == annonce.vendeur
    if not visible and not est_vendeur and not request.user.is_staff:
        return render(request, "annonces/indisponible.html", status=404)
    return render(
        request,
        "annonces/detail.html",
        {"annonce": annonce, "est_vendeur": est_vendeur, "numero_visible": False},
    )


@login_required
@require_POST
@limiter_debit("numero")
def afficher_numero(request, pk):
    """Décision Q9 : le numéro n'apparaît qu'après un clic authentifié et journalisé."""
    annonce = get_object_or_404(
        Annonce.objects.select_related("categorie", "commune", "vendeur"), pk=pk
    )
    if annonce.contact != Annonce.Contact.TELEPHONE:
        return redirect(annonce.get_absolute_url())
    ClicAffichageNumero.objects.get_or_create(annonce=annonce, utilisateur=request.user)
    return render(
        request,
        "annonces/detail.html",
        {
            "annonce": annonce,
            "est_vendeur": request.user == annonce.vendeur,
            "numero_visible": True,
        },
    )


@login_required
def choisir_categorie(request):
    return render(
        request,
        "annonces/publier_categorie.html",
        {"categories": Categorie.objects.filter(actif=True)},
    )


@login_required
@limiter_debit("publication")
def publier(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug, actif=True)
    form = AnnonceForm(
        request.POST or None,
        request.FILES or None,
        categorie=categorie,
        utilisateur=request.user,
    )
    if request.method == "POST" and form.is_valid():
        annonce = form.save()
        messages.success(request, _("Votre annonce est publiée !"))
        return redirect(annonce.get_absolute_url())
    return render(request, "annonces/publier.html", {"form": form, "categorie": categorie})


@login_required
def mes_annonces(request):
    annonces = (
        request.user.annonces.select_related("categorie", "commune")
        .prefetch_related("photos")
        .order_by("-date_publication")
    )
    return render(request, "annonces/mes_annonces.html", {"annonces": annonces})


@login_required
@require_POST
def renouveler(request, pk):
    """Décision Q10 : renouvellement en un clic, limité (7 jours), remonte l'annonce."""
    annonce = get_object_or_404(Annonce, pk=pk, vendeur=request.user)
    if annonce.peut_renouveler:
        annonce.date_publication = timezone.now()
        annonce.save(update_fields=["date_publication"])
        messages.success(request, _("Annonce renouvelée : elle repart en tête pour 30 jours."))
    else:
        messages.error(request, _("Cette annonce ne peut pas encore être renouvelée."))
    return redirect("annonces:mes_annonces")


@login_required
@require_POST
def retirer(request, pk):
    annonce = get_object_or_404(Annonce, pk=pk, vendeur=request.user)
    annonce.statut = Annonce.Statut.RETIREE
    annonce.save(update_fields=["statut"])
    messages.success(request, _("Annonce retirée."))
    return redirect("annonces:mes_annonces")
