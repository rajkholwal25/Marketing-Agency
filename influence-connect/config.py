import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def _normalize_database_url(url: str) -> str:
    """Convert Supabase/Heroku postgres URLs for SQLAlchemy + psycopg2."""
    if not url:
        return url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def _get_database_uri() -> str:
    url = os.environ.get("DATABASE_URL")
    if url and any(p in url for p in ("[YOUR-PASSWORD]", "[PASSWORD]")):
        url = None
    if url:
        return _normalize_database_url(url)
    return f"sqlite:///{os.path.join(BASE_DIR, 'influence_connect.db')}"


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "influence-connect-dev-secret-key")

    # Supabase project (REST / Auth API — optional for future features)
    SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

    SQLALCHEMY_DATABASE_URI = _get_database_uri()

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
