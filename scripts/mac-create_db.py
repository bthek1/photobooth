import os
import dj_database_url
from dotenv import load_dotenv
import psycopg2.extensions  # for escaping passwords

# Load environment variables from .env file
load_dotenv()

def sql_escape_literal(value):
    """Escape string literals for SQL (like passwords)."""
    return psycopg2.extensions.adapt(value).getquoted().decode()

def generate_sql(database_url):
    db_info = dj_database_url.parse(database_url)

    db_user = db_info["USER"]
    db_password = db_info["PASSWORD"]
    db_name = db_info["NAME"]

    # Escape password only — wrap identifiers manually with quotes
    password_escaped = sql_escape_literal(db_password)

    return f"""
-- 🚀 Mac-safe SQL for creating user and DB

CREATE USER "{db_user}" WITH PASSWORD {password_escaped};
CREATE DATABASE "{db_name}" OWNER "{db_user}";
GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO "{db_user}";

ALTER ROLE "{db_user}" SET client_encoding TO 'utf8';
ALTER ROLE "{db_user}" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "{db_user}" SET timezone TO 'GMT';
ALTER ROLE "{db_user}" CREATEDB;
""".strip()

def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    print(generate_sql(database_url))

if __name__ == "__main__":
    main()
