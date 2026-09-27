"""Verify that Python can reach PostgreSQL and see our schemas."""

from sqlalchemy import text

from db import get_engine


def main():
    engine = get_engine()

    with engine.connect() as conn:
        version = conn.execute(text("SELECT version();")).scalar()
        print("Connected to PostgreSQL")
        print(f"  {version.split(',')[0]}")

        schemas = conn.execute(
            text(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name IN ('raw', 'staging', 'marts')
                ORDER BY schema_name;
                """
            )
        ).scalars().all()

        print(f"\nSchemas found: {schemas}")

        if set(schemas) == {"raw", "staging", "marts"}:
            print("\nAll three schemas present. Foundation is ready.")
        else:
            print("\nSome schemas are missing. Re-check Step 6.")


if __name__ == "__main__":
    main()