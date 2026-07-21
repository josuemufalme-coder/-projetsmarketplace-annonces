"""Limitation de débit — SRS §5.3.

Première ligne de défense contre les faux comptes et le spam (d'autant
plus importante que le MVP n'a pas de vérification SMS). Fenêtre fixe en
cache : au-delà du seuil, la requête POST reçoit une page 429.

Seuils configurables par variables d'environnement (RATELIMIT_*, format
« nombre/secondes »). L'identité est le compte connecté, sinon l'adresse
IP (en tenant compte du proxy Railway/Cloudflare).

Note d'échelle : le cache local convient au déploiement MVP (un seul
processus). Passer à un cache partagé (base ou Redis) si l'on augmente
le nombre de processus gunicorn.
"""

import time
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import render


def _identite(request):
    if request.user.is_authenticated:
        return f"u{request.user.pk}"
    transmis = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = transmis.split(",")[0].strip() if transmis else request.META.get("REMOTE_ADDR", "?")
    return f"ip{ip}"


def limiter_debit(cle):
    """Décorateur de vue : limite les POST selon RATE_LIMITS[cle]."""

    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            if request.method == "POST":
                limite, fenetre = settings.RATE_LIMITS[cle]
                creneau = int(time.time() // fenetre)
                cache_cle = f"rl:{cle}:{_identite(request)}:{creneau}"
                compteur = cache.get_or_set(cache_cle, 0, timeout=fenetre)
                if compteur >= limite:
                    return render(request, "429.html", status=429)
                try:
                    cache.incr(cache_cle)
                except ValueError:
                    cache.set(cache_cle, 1, timeout=fenetre)
            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur
