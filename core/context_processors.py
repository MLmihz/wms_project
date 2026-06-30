from .views import get_user_role
from .models import Notification


def unread_notifications_count(request):
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}

    role, profile = get_user_role(request.user)
    if role is None or profile is None:
        return {'unread_notifications_count': 0}

    if hasattr(profile, 'is_active') and not profile.is_active:
        return {'unread_notifications_count': 0}

    count = Notification.objects.filter(
        recipient_type=role,
        recipient_id=profile.id,
        is_read=False,
    ).count()

    return {'unread_notifications_count': count}
