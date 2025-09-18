import environ
import os
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent


# Initialize Django-environ
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Configure the DATABASES dictionary
DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://new:asdfasdf@localhost:5432/django")
}

def generate_sql(db_info):
    # Extract the necessary components
    db_user = db_info.get('USER')
    db_password = db_info.get('PASSWORD')
    db_name = db_info.get('NAME')

    # Generate SQL commands as a string
    sql_commands = f"""
    CREATE USER {db_user} WITH PASSWORD '{db_password}';
    CREATE DATABASE {db_name} OWNER {db_user};
    GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};
    ALTER ROLE {db_user} SET client_encoding TO 'utf8';
    ALTER ROLE {db_user} SET default_transaction_isolation TO 'read committed';
    ALTER ROLE {db_user} SET timezone TO 'UTC';
    ALTER ROLE {db_user} CREATEDB;
    """
    return sql_commands.strip()

def main():
    db_info = DATABASES["default"]
    
    # Validate essential keys
    required_keys = ['USER', 'PASSWORD', 'NAME']
    if not all(k in db_info for k in required_keys):
        raise ValueError(f"DATABASE config missing required keys: {required_keys}")
    
    # Generate and print the SQL script
    sql_script = generate_sql(db_info)
    print(sql_script)

if __name__ == "__main__":
    main()
