"""Run: python test_db.py — checks Supabase connection locally."""
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine, text

from config import Config


def main():
    uri = Config.SQLALCHEMY_DATABASE_URI
    if "@" in uri:
        host = uri.split("@", 1)[1]
        print(f"Connecting to: ...@{host}")
    else:
        print("Using local SQLite (DATABASE_URL not set)")

    engine = create_engine(uri)
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        rows = conn.execute(
            text(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' ORDER BY tablename"
            )
        ).fetchall()

    print("Connection: SUCCESS")
    print(f"Postgres: {version[:60]}...")
    print("Tables:", [r[0] for r in rows] if rows else "(none — run python run.py once to create)")


if __name__ == "__main__":
    main()
