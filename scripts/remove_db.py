import environ
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize Django-environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Configure DATABASES
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://new:asdfasdf@localhost:5432/django")
}

def generate_remove_sql(db_info):
    db_user = db_info.get('USER')
    db_name = db_info.get('NAME')

    return f"""
    -- WARNING: This script drops the database and user! Handle with care.
    REVOKE CONNECT ON DATABASE {db_name} FROM PUBLIC;
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = '{db_name}' AND pid <> pg_backend_pid();

    DROP DATABASE IF EXISTS {db_name};
    DROP USER IF EXISTS {db_user};
    """.strip()

def main():
    db_info = DATABASES["default"]

    required_keys = ['USER', 'NAME']
    if not all(k in db_info for k in required_keys):
        raise ValueError(f"DATABASE config missing required keys: {required_keys}")

    print(generate_remove_sql(db_info))

if __name__ == "__main__":
    main()
