"""
Promote an existing user to admin (or demote back to citizen).

Run with: python -m scripts.make_admin someone@example.com
Demote with: python -m scripts.make_admin someone@example.com --revoke

There is deliberately no API endpoint for this: the first admin has to be
created by someone with server access.
"""
import argparse
import sys

from app.database import SessionLocal
from app.models.user import User, ROLE_ADMIN, ROLE_CITIZEN


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("email")
    parser.add_argument("--revoke", action="store_true", help="Demote the user back to citizen")
    args = parser.parse_args()

    with SessionLocal() as db:
        user = db.query(User).filter(User.email == args.email).first()
        if not user:
            print(f"No user with email {args.email}. Register in the app first.")
            sys.exit(1)

        user.role = ROLE_CITIZEN if args.revoke else ROLE_ADMIN
        db.commit()
        print(f"{user.email} is now '{user.role}'.")


if __name__ == "__main__":
    main()
