#!/usr/bin/env python3
"""从 OpenStock ANNOUNCEMENTS 拉取公告数据写入本地 PostgreSQL"""
import os
import sys
from datetime import date, datetime

import requests

sys.path.insert(0, "/opt/claude/mystocks_spec/web/backend")
sys.path.insert(0, "/opt/claude/mystocks_spec")

OPENSTOCK = os.environ.get("OPENSTOCK_BASE_URL", "http://192.168.123.104:8040")
KEY = os.environ.get("OPENSTOCK_SECURITY_API_KEY")
if not KEY:
    print("[import_announcements] OPENSTOCK_SECURITY_API_KEY not set — exiting")
    sys.exit(1)
HEADERS = {"X-API-Key": KEY, "Content-Type": "application/json"}

# 1. 拉取数据
today = date.today()
print(f"Fetching announcements for {today}...")
resp = requests.post(
    f"{OPENSTOCK}/data/fetch",
    headers=HEADERS,
    json={"data_category": "ANNOUNCEMENTS", "params": {"date": today.isoformat()}},
    timeout=30,
)
if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}: {resp.text[:200]}")
    sys.exit(1)

data = resp.json()
rows = data.get("data", [])
print(f"Got {len(rows)} announcements from OpenStock (source: {data.get('source')})")

if not rows:
    print("No data returned")
    sys.exit(0)

# 2. 写入本地 DB
from app.models.announcement import Announcement
from app.core.database import get_postgresql_session

session = get_postgresql_session()
saved = 0
try:
    for row in rows[:100]:  # 限制 100 条
        stock_code = str(row.get("symbol", row.get("code", row.get("代码", ""))))
        if not stock_code:
            continue
        title = str(row.get("title", row.get("公告标题", "")))
        url = str(row.get("url", row.get("网址", "")))
        # 用 URL 检查重复（OpenStock 无 source_id 字段）
        existing = (
            session.query(Announcement)
            .filter(Announcement.url == url)
            .first()
        )
        if existing:
            continue

        ann_type = str(row.get("notice_type", row.get("公告类型", "")))
        ann = Announcement(
            stock_code=stock_code,
            stock_name=str(row.get("name", row.get("名称", ""))),
            announcement_title=title,
            announcement_type=ann_type,
            publish_date=today,
            publish_time=datetime.now(),
            url=url,
            data_source="openstock",
            source_id=url[-32:],  # URL 末尾作为 source_id
            importance_level=1,
            sentiment="neutral",
        )
        session.add(ann)
        saved += 1

    session.commit()
    print(f"Saved {saved} new announcements to DB")
except Exception as e:
    session.rollback()
    print(f"ERROR: {e}")
    sys.exit(1)
finally:
    session.close()
