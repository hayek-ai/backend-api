from passlib.context import CryptContext
import re

from app.main.libs.strings import gettext

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def encrypt_password(password: str) -> str:
    return pwd_context.hash(password)


def check_encrypted_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def is_email_valid(address_to_verify: str) -> bool:
    """Returns True if email is valid. Otherwise False."""

    regex = '^[_a-z0-9-]+(.[_a-z0-9-]+)*@[a-z0-9-]+(.[a-z0-9-]+)*(.[a-z]{2,})$'

    match = re.match(regex, address_to_verify)

    if match:
        return True

    return False


def is_username_valid(username: str) -> bool:
    """Returns True if username is valid. Otherwise False."""

    special_sym = [' ', '{', '}', '(', ')', '[', ']', '#', ':', ';', '^', ',', '.', '?', '!', '|', '&', '`', '~', '@',
                   '$', '%', '/', '\\', '=', '+', '-', '*', "'", '"']
    if len(username) > 20:
        return False

    if any(char in special_sym for char in username):
        return False

    return True


def is_empty(string: str) -> bool:
    if string.strip() == "": return True
    return False


def validate_signup_data(user: dict) -> dict:
    valid_dict = {"errors": []}

    if is_empty(user["email"]):
        valid_dict["errors"].append({
            "status": 400,
            "detail": gettext("empty"),
            "field": "email"
        })
    elif not is_email_valid(user["email"]):
        valid_dict["errors"].append({
            "status": 400,
            "detail": gettext("email_invalid"),
            "field": "email"
        })

    if is_empty(user["username"]):
        valid_dict["errors"].append({
            "status": 400,
            "detail": gettext("empty"),
            "field": "username"
        })
    elif not is_username_valid(user["username"]):
        valid_dict["errors"].append({
            "status": 400,
            "detail": gettext("username_invalid"),
            "field": "username"
        })

    if is_empty(user["password"]):
        valid_dict["errors"].append({
            "status": 400,
            "detail": gettext("empty"),
            "field": "password"
        })

    valid_dict["valid"] = len(valid_dict["errors"]) == 0
    return valid_dict
