import shortuuid
from django.db.models import Max
from rest_framework.authtoken.models import Token


# noinspection PyBroadException
def get_token(user):
    try:
        return Token.objects.get(user=user).key
    except Exception:
        return None


def generate_random_id(length=6):
    return shortuuid.ShortUUID().random(length=length)
