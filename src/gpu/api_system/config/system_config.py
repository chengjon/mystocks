"""
System Configuration Module
"""

import os
from typing import Dict, Any

class SystemConfig:
    """System Configuration"""

    def __init__(self):
        self.redis_config = {
            "host": os.getenv("REDIS_HOST", "localhost"),
            "port": int(os.getenv("REDIS_PORT", 6379)),
            "db": int(os.getenv("REDIS_DB", 0)),
        }
        
        self.grpc_config = {
            "host": os.getenv("GRPC_HOST", "[::]"),
            "port": int(os.getenv("GRPC_PORT", 50051)),
            "max_workers": int(os.getenv("GRPC_MAX_WORKERS", 10)),
            "max_message_size": int(os.getenv("GRPC_MAX_MESSAGE_SIZE", 1024 * 1024 * 50)), # 50MB
        }
