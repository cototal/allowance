import bcrypt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from werkzeug.security import check_password_hash

_argon2_hasher = PasswordHasher()


def verify_password(user, password):
    encoded = user.password
    valid = False

    if encoded.startswith(("$2a$", "$2b$", "$2y$")):
        compatible_hash = encoded.replace("$2y$", "$2b$", 1).encode("ascii")
        try:
            valid = bcrypt.checkpw(password.encode("utf-8"), compatible_hash)
        except (ValueError, TypeError):
            valid = False
    elif encoded.startswith("$argon2"):
        try:
            valid = _argon2_hasher.verify(encoded, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            valid = False
    else:
        try:
            valid = check_password_hash(encoded, password)
        except (ValueError, TypeError):
            valid = False

    if valid and encoded.startswith(("$2a$", "$2b$", "$2y$", "$argon2")):
        user.set_password(password)
    return valid
