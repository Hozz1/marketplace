from .models import UserProfile


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return None
    except AttributeError:
        return None


def user_has_role(user, role):
    return get_user_role(user) == role


def is_buyer_user(user):
    return user_has_role(user, UserProfile.Role.BUYER)


def is_seller_user(user):
    return user_has_role(user, UserProfile.Role.SELLER)


def is_admin_user(user):
    return user_has_role(user, UserProfile.Role.ADMIN)
