"""
Gold Tier AI Employee - Scheduler Module

Handles scheduled tasks like daily briefings and weekly audits.
"""

from .scheduler import TaskScheduler
from .tasks import (
    generate_daily_briefing,
    generate_weekly_audit,
    check_email,
    update_dashboard,
)

__all__ = [
    'TaskScheduler',
    'generate_daily_briefing',
    'generate_weekly_audit',
    'check_email',
    'update_dashboard',
]
