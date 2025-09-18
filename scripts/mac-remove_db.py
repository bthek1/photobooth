import os

import dj_database_url
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def generate_remove_sql(database_url):
    # Parse the DATABASE_URL
    db_info = dj_database_url.parse(database_url)

    db_user = db_info.get("USER")
    db_name = db_info.get("NAME")

    if not db_user or not db_name:
        raise ValueError("Could not parse database name or user from DATABASE_URL.")

    sql_commands = f"""
-- 🛑 WARNING: This script drops the database and user! Handle with care.

-- Disconnect active connections (PostgreSQL-specific)
REVOKE CONNECT ON DATABASE "{db_name}" FROM PUBLIC;
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '{db_name}' AND pid <> pg_backend_pid();

-- Drop the database
DROP DATABASE IF EXISTS "{db_name}";

-- Drop the user
DROP USER IF EXISTS "{db_user}";
"""

    return sql_commands.strip()


def main():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in the environment variables.")

    print("🛡️  This operation will DROP your database and user. Are you sure?")
    confirm = input("Type 'yes' to proceed: ")

    if confirm.lower() != "yes":
        print("Aborted.")
        return

    sql_script = generate_remove_sql(database_url)

    print("\n📄 Run the following SQL in psql (or redirect it to a file):\n")
    print(sql_script)

    print("\nExample (macOS Homebrew PostgreSQL):")
    print("  psql -U postgres -h localhost -f drop_db.sql")


if __name__ == "__main__":
    main()
