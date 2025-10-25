#!/usr/bin/env python3
"""Debug script to test strategy list endpoint"""
import os
import sys

# Set environment variables
os.environ['POSTGRESQL_HOST'] = '192.168.123.104'
os.environ['POSTGRESQL_PORT'] = '5438'
os.environ['POSTGRESQL_USER'] = 'postgres'
os.environ['POSTGRESQL_PASSWORD'] = 'c790414J'
os.environ['POSTGRESQL_DATABASE'] = 'mystocks'
os.environ['MYSQL_HOST'] = '192.168.123.104'
os.environ['MYSQL_PORT'] = '5438'
os.environ['MYSQL_USER'] = 'postgres'
os.environ['MYSQL_PASSWORD'] = 'c790414J'
os.environ['MYSQL_DATABASE'] = 'mystocks'
os.environ['TDENGINE_HOST'] = 'localhost'
os.environ['TDENGINE_PORT'] = '6041'
os.environ['TDENGINE_USER'] = 'root'
os.environ['TDENGINE_PASSWORD'] = 'taosdata'
os.environ['TDENGINE_DATABASE'] = 'market_data'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PORT'] = '6379'
os.environ['REDIS_PASSWORD'] = ''
os.environ['REDIS_DB'] = '1'

# Add project root to path
sys.path.insert(0, '/opt/claude/mystocks_spec')
sys.path.insert(0, '/opt/claude/mystocks_spec/web/backend')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=True)

print("Testing GET /api/v1/strategy/strategies...")
try:
    response = client.get('/api/v1/strategy/strategies')
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        print(f'Success! Got {len(data.get("items", []))} items')
        print(f'Total: {data.get("total")}')
    else:
        print(f'Error Response: {response.text[:500]}')
except Exception as e:
    print(f'Exception: {type(e).__name__}: {str(e)[:500]}')
    import traceback
    traceback.print_exc()
