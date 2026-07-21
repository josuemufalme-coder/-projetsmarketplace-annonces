from django import template

register = template.Library()


@register.filter
def etoiles(note):
    """Affiche une note 1–5 en étoiles pleines et vides (ex. ★★★★☆)."""
    try:
        pleine = max(0, min(5, int(round(float(note)))))
    except (TypeError, ValueError):
        return ""
    return "★" * pleine + "☆" * (5 - pleine)
