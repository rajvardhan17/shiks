from __future__ import annotations

from db.session import create_all_tables


def main() -> None:
    create_all_tables()
    print("Database tables created (check DATABASE_URL environment variable).")


if __name__ == "__main__":
    main()
