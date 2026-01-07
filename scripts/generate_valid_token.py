import os
import sys
from datetime import timedelta
from typing import Optional

# 添加项目根目录到路径
sys.path.append("/opt/claude/mystocks_spec")
sys.path.append("/opt/claude/mystocks_spec/web/backend")

from app.core.config import settings
from app.core.security import create_access_token

def generate_admin_token():
    """Generates a valid JWT token for the admin user."""
    # Ensure JWT_SECRET_KEY is available
    if not settings.jwt_secret_key:
        print("Error: JWT_SECRET_KEY not set in environment or config.")
        sys.exit(1)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)

    # Create token for 'admin' user with necessary claims
    token_data = {
        "sub": "admin",
        "user_id": 1,
        "role": "admin"
    }

    access_token = create_access_token(
        data=token_data,
        expires_delta=access_token_expires
    )

    print(f"Bearer {access_token}")

if __name__ == "__main__":
    generate_admin_token()
