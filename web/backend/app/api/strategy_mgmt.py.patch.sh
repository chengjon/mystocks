#!/usr/bin/env python3
"""修复 M1d cherry-pick 中 strategy_mgmt.py 的 import 冲突"""
import sys
with open(sys.argv[1], 'r') as f:
    content = f.read()

old = """<<<<<<< HEAD
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query, Header
=======
from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path, Query, Header
from sqlalchemy import text
>>>>>>> 8785486d5 (B4.014-M1d: fix strategy health SQLAlchemy probe)"""

new = """from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path, Query, Header
from sqlalchemy import text"""

content = content.replace(old, new)
with open(sys.argv[1], 'w') as f:
    f.write(content)
print('done')
