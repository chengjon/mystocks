"""
监控系统API模块
"""

# NOTE: This __init__.py should NOT be used for importing router
# The main monitoring.py file is at app/api/monitoring.py level
# routes.py in this directory has wrong prefix="/monitoring"
#
# We're just exporting a placeholder to avoid errors
# The actual router is imported from app.api.monitoring

from app.api.monitoring import router as main_router

__all__ = ["router"]

# Export of correct router (from parent monitoring.py)
router = main_router
