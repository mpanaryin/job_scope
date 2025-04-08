import bcrypt


def hash_password(password: str) -> str:
    """
    Generate a bcrypt hash from a plain text password.

    :param password: Plain text password.
    :return: Hashed password as a UTF-8 encoded string.
    """
    pw_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pw_bytes, salt)
    return hashed.decode("utf-8")


def check_password(password: str, password_in_db: str) -> bool:
    """
    Check if a plain password matches the hashed one stored in the database.

    :param password: Plain text password to check.
    :param password_in_db: Hashed password stored in the database.
    :return: True if the password matches, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), password_in_db.encode("utf-8"))
