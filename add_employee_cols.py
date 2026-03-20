import psycopg2

DB_URL = "postgresql://postgres.agmsxhesjtvkdjhysqni:Azizbek0085%40@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"

def update_schema():
    print("Connecting to PostgreSQL database...")
    try:
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        commands = [
            "ALTER TABLE employees ADD COLUMN phone VARCHAR;",
            "ALTER TABLE employees ADD COLUMN \"passportSeries\" VARCHAR;",
            "ALTER TABLE employees ADD COLUMN \"faceIdImage\" VARCHAR;"
        ]

        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                cursor.execute(cmd)
                print("Success!")
            except psycopg2.errors.DuplicateColumn:
                print("Column already exists, skipping.")
            except Exception as e:
                print(f"Error: {e}")

        cursor.close()
        conn.close()
        print("Database schema update completed.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    update_schema()
