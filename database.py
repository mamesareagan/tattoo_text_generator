import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def setup_database():
    # Connect to PostgreSQL server as superuser
    try:
        # First connect to default 'postgres' database to perform admin operations
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="ww",  # Replace with your postgres superuser password
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Database configuration
        DB_NAME = "tattoo_db"
        DB_USER = "tatoogenerator"
        DB_PASSWORD = "tatoo"
        
        # Create database if it doesn't exist
        print(f"Creating database {DB_NAME}...")
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database {DB_NAME} created successfully!")
        else:
            print(f"Database {DB_NAME} already exists.")
        
        # Create user if it doesn't exist
        print(f"\nCreating user {DB_USER}...")
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
        exists = cur.fetchone()
        if not exists:
            cur.execute(f"CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}'")
            print(f"User {DB_USER} created successfully!")
        else:
            print(f"User {DB_USER} already exists.")
            
        # Grant privileges
        print("\nGranting privileges...")
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER}")
        
        # Connect to the new database to grant schema privileges
        cur.close()
        conn.close()
        
        # Connect to the new database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user="postgres",
            password="ww",  # Replace with your postgres superuser password
            host="localhost",
            port="5432"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Grant additional privileges
        cur.execute(f"GRANT ALL ON SCHEMA public TO {DB_USER}")
        cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO {DB_USER}")
        cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO {DB_USER}")
        cur.execute(f"ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO {DB_USER}")
        
        print("\nAll privileges granted successfully!")
        
        # Close database connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting database setup...")
    if setup_database():
        print("\nDatabase setup completed successfully!")
    else:
        print("\nDatabase setup failed!")