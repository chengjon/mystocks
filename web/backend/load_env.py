#!/usr/bin/env python
"""Load environment variables before starting the app"""

from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env file from project root
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Debug: verify environment variables are loaded
print(f"Loading env from: {env_path}")
print(f"File exists: {env_path.exists()}")

# Verify specific variables
pg_password = os.getenv("POSTGRESQL_PASSWORD")
jwt_secret = os.getenv("JWT_SECRET_KEY")
print(f"POSTGRESQL_PASSWORD loaded: {'✅' if pg_password else '❌'}")
print(f"JWT_SECRET_KEY loaded: {'✅' if jwt_secret else '❌'}")

# Now import and run the app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
