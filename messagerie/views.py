from django.contrib import messages as notifications
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from annonces.models import Annonce

from .models import Conversation, Message
from .services import notifier_nouveau_message


@login_required
@require_POST
def contacter(request, pk):
    """Premier message d'un acheteur depuis la page d'une annonce."""
    annonce = get_object_or_404(Annonce, pk=pk)
    texte = request.POST.get("texte", "").strip()
    if (
        annonce.contact != Annonce.Contact.MESSAGERIE
        or annonce.statut != Annonce.Statut.PUBLIEE
        or request.user == annonce.vendeur
        or not texte
    ):
        return redirect(annonce.get_absolute_url())
    conversation, _cree = Conversation.objects.get_or_create(
        annonce=annonce, acheteur=request.user
    )
    message = Message.objects.create(
        conversation=conversation, expediteur=request.user, texte=texte
    )
    notifier_nouveau_message(message)
    notifications.success(request, _("Message envoyé au vendeur."))
    return redirect("messagerie:conversation", pk=conversation.pk)


@login_required
def boite(request):
    conversations = (
        Conversation.objects.filter(Q(acheteur=request.user) | Q(annonce__vendeur=request.user))
        .select_related("annonce", "annonce__vendeur", "acheteur")
        .annotate(
            dernier=Max("messages__date"),
            non_lus=Count(
                "messages",
                filter=Q(messages__lu=False) & ~Q(messages__expediteur=request.user),
            ),
        )
        .order_by("-dernier")
    )
    return render(request, "messagerie/boite.html", {"conversations": conversations})


@login_required
def conversation(request, pk):
    fil = get_object_or_404(
        Conversation.objects.select_related("annonce", "annonce__vendeur", "acheteur"), pk=pk
    )
    if request.user not in (fil.acheteur, fil.vendeur):
        return redirect("messagerie:boite")

    if request.method == "POST":
        texte = request.POST.get("texte", "").strip()
        if texte:
            message = Message.objects.create(
                conversation=fil, expediteur=request.user, texte=texte
            )
            notifier_nouveau_message(message)
            return redirect("messagerie:conversation", pk=fil.pk)

    fil.non_lus_pour(request.user).update(lu=True)
    return render(
        request,
        "messagerie/conversation.html",
        {"fil": fil, "interlocuteur": fil.interlocuteur(request.user)},
    )
