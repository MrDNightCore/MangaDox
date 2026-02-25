from users.models import UserProfile


def user_context(request):
    """Provide current user and admin status to all templates."""
    user_id = request.session.get('user_id')
    current_user = None
    is_admin = False
    if user_id:
        try:
            current_user = UserProfile.objects.get(id=user_id)
            is_admin = getattr(current_user, 'is_admin', False)
        except UserProfile.DoesNotExist:
            pass
    return {
        'current_user': current_user,
        'is_admin': is_admin,
    }
