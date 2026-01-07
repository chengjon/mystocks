
import sys
import os
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root / "web" / "backend"))
sys.path.append(str(project_root))

from app.core.security import authenticate_user, get_user_from_database, verify_password, get_password_hash
from app.core.database import get_postgresql_session
from app.db import UserRepository

def check_auth():
    print("--- Checking Auth System ---")

    # 1. Check Mock/Default Admin
    print("\n[1] Testing Default Admin (admin/admin123)...")
    user = authenticate_user("admin", "admin123")
    if user:
        print("✅ Admin Login Successful")
    else:
        print("❌ Admin Login Failed")

    # 2. Check testuser
    print("\n[2] Checking 'testuser' in DB...")
    try:
        db_user = get_user_from_database("testuser")
        if db_user:
            print(f"✅ Found 'testuser' in DB. ID: {db_user.id}, Role: {db_user.role}")
            print(f"   Hashed Password in DB: {db_user.hashed_password}")

            # Test with common passwords
            passwords = ["testpass123", "password", "123456", "testuser"]
            found = False
            for p in passwords:
                if verify_password(p, db_user.hashed_password):
                    print(f"✅ Password match found: '{p}'")
                    found = True
                    break

            if not found:
                print("❌ No match for common passwords.")

                # Try to reset it to 'testpass123' if possible
                print("   Attempting to reset password to 'TestPass123' (meeting complexity requirements)...")
                try:
                    session = get_postgresql_session()
                    repo = UserRepository(session)

                    # Need to do a raw update or use repo method if available
                    # Repo probably doesn't have update_password exposed easily here without full object
                    # Let's just use the session directly
                    from sqlalchemy import text
                    new_hash = get_password_hash("TestPass123")
                    session.execute(
                        text("UPDATE users SET hashed_password = :h WHERE username = 'testuser'"),
                        {"h": new_hash}
                    )
                    session.commit()
                    print("✅ Password reset to 'TestPass123'.")
                    session.close()
                except Exception as e:
                    print(f"❌ Failed to reset password: {e}")

        else:
            print("❌ 'testuser' NOT found in DB.")

            # Create it
            print("   Creating 'testuser'...")
            try:
                session = get_postgresql_session()
                repo = UserRepository(session)
                repo.create_user(
                    username="testuser",
                    email="testuser@example.com",
                    hashed_password=get_password_hash("TestPass123"),
                    role="user",
                    is_active=True
                )
                print("✅ 'testuser' created with password 'TestPass123'")
                session.close()
            except Exception as e:
                print(f"❌ Failed to create user: {e}")

    except Exception as e:
        print(f"❌ Error checking DB: {e}")

if __name__ == "__main__":
    check_auth()
