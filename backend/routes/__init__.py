# /forge/backend/routes/__init__.py

from .core import core
from .auth import auth
from .tasks import tasks
from .forge_ai import forge_ai
from .calendar import calendar_bp

# Expose blueprints for use in create_app()
__all__ = ["core", "auth", "tasks", "forge_ai", "calendar_bp"]