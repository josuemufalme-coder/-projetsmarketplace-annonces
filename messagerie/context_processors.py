def messages_non_lus(request):
    """Compteur de messages non lus affiché dans l'en-tête du site."""
    if not request.user.is_authenticated:
        return {"nb_messages_non_lus": 0}
    from django.db.models import Q

    from .models import Message

    total = (
        Message.objects.filter(lu=False)
        .exclude(expediteur=request.user)
        .filter(
            Q(conversation__acheteur=request.user)
            | Q(conversation__annonce__vendeur=request.user)
        )
        .count()
    )
    return {"nb_messages_non_lus": total}
