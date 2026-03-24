"""
IntelliLearn AI - AI-Driven Employee Skill Development Platform
"""

__version__ = "1.0.0"
__author__ = "IntelliLearn Team"

# Ensure models are registered with SQLAlchemy metadata when imported
try:
    from . import database  # noqa: F401
    from .models import base as _models_base  # noqa: F401
except Exception:
    # Import side-effects are not critical at package import time
    pass
