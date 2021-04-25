from datetime import timedelta

from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from constants import TOKEN_EXPIRED_AFTER_SECONDS


# this return left time
def expires_in(token):
	time_elapsed = timezone.now() - token.created
	left_time = timedelta(seconds=TOKEN_EXPIRED_AFTER_SECONDS) - time_elapsed
	return left_time


# token checker if token expired or not
def is_token_expired(token):
	return expires_in(token) < timedelta(seconds=0)


# If token is expired new token will be established:
# If token is expired then it will be removed
# and new one with different key will be created
def token_expire_handler(token):
	is_expired = is_token_expired(token)
	if is_expired:
		token.delete()
		token = Token.objects.create(user=token.user)
	return is_expired, token


class ExpiringTokenAuthentication(TokenAuthentication):
	"""
	If token is expired then it will be removed
	and new one with different key will be created,
	this new one will be given to the user only the 1st time
	"""

	def authenticate_credentials(self, key):
		try:
			token = Token.objects.get(key=key)
		except Token.DoesNotExist:
			raise AuthenticationFailed("Invalid Token")

		if not token.user.is_active:
			raise AuthenticationFailed("User is not active")

		is_expired, token = token_expire_handler(token)

		return token.user, token
