from functools import wraps
from .db import SessionLocal  # or wherever you define SessionLocal


def with_db_session(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with SessionLocal() as session:
            return func(session, *args, **kwargs)

    return wrapper
