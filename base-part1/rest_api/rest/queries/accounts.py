from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from api.authentication import token_expire_handler
from api.models import User
from logs import general_log
from logs.logs_decorator import log_operations_time, log_and_catch_query


@log_operations_time
@log_and_catch_query((Exception, "Erro ao logar utilizador!"))
def login(data):
    """
    :param data: Data from request
    :return: tuple with
        - dictionary with the user and session token
        - list of success messages
        - list of error messages
    """
    success, errors = [], []

    user = authenticate(
        username=data.get('email'),
        password=data.get('password')
    )

    if not user:
        errors.append("Credenciais para o login inválidas!")
        general_log.error(f"{__name__}->{login.__name__} {errors[-1]}")
        return [], success, errors

    token, _ = Token.objects.get_or_create(user=user)
    is_expired, token = token_expire_handler(token)

    success.append(f"{user.username} logado com sucesso!")
    general_log.debug(f"{__name__}->{login.__name__} {success[-1]}")

    return {'token': token.key, 'user': user}, success, errors


@log_operations_time
@log_and_catch_query((Exception, "Erro ao registar novo utilizador!"))
def register(user_data):
    """Function to query the database to add a new user
    :param user_data: Data from request
    :return: tuple with
        - empty dictionary
        - list of success messages
        - list of error messages
    """
    data, success, errors = {}, [], []
    email = user_data.get('email')

    if User.objects.filter(email=email).exists():
        errors.append("Já existe um utilizador com esse email! O utilizador não foi adicionado à base de dados!")
        general_log.error(f"{__name__}->{register.__name__} {errors[-1]}")

    else:
        user_data['username'] = email
        user = User.objects.create_user(**user_data)
        success.append("O utilizador foi criado com sucesso!")
        general_log.debug(f"{__name__}->{register.__name__} {success[-1]}")
        data = {
            'user': user,
            'token': Token.objects.create(user=user).key
        }

    return data, success, errors


@log_operations_time
@log_and_catch_query((Exception, "Erro ao editar o perfil do utilizador"))
def edit_profile(user, data):
    """
    PUT request to update an user
    :param user: User to be updated
    :param data: Data to insert
    :return: tuple with
        - empty dictionary
        - list of success messages
        - list of error messages
    """
    success, errors = [], []
    data.pop('password', None)  # Cant change password
    email = data.get('email')

    if email != user.email and User.objects.filter(email=email).exists():
        errors.append("Já existe um utilizador com esse email! O utlizador não foi editado!")
        general_log.error(f"{__name__}->{edit_profile.__name__} {errors[-1]}")

    else:
        if email:
            data['username'] = email

        user.__dict__.update(data)
        user.save()

        success.append("O utilizador foi editado com sucesso!")
        general_log.debug(f"{__name__}->{edit_profile.__name__} {success[-1]}")

    return {'user': user}, success, errors


@log_operations_time
@log_and_catch_query((Exception, "Erro ao editar a palavra passe do utilizador"))
def edit_password(user, data):
    """
    Update an user password and persist the changes
    :param user: User to be updated
    :param data: Dictionary with the current and new passwords
    :return: tuple with
        - empty dictionary
        - list of success messages
        - list of error messages
    """
    success, errors = [], []
    current_password = data.get('current_password')

    status = user.check_password(current_password)

    if status:
        new_password = data.get('new_password')
        user.set_password(new_password)
        user.save()

        success.append("Palavra passe atualizada com sucesso")
        general_log.debug(f"{__name__}->{edit_profile.__name__} {success[-1]}")

    else:
        errors.append("A palavra passe atual é inválida")
        general_log.error(f"{__name__}->{edit_profile.__name__} {errors[-1]}")

    return {}, success, errors


@log_operations_time
@log_and_catch_query((Exception, "Erro ao realizar logout do utilizador!"))
def logout(auth_token):
    """
    Deletes the token associated with that user.
    :param auth_token: Token to be deleted
    :return: Error or success messages and status code
    """
    Token.objects.get(key=auth_token).delete()

    success = ["Logout efetuado com sucesso!"]
    general_log.debug(f"{__name__}->{logout.__name__} {success[-1]}")

    return {}, success, []
