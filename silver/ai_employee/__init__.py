"""
AI Employee - Silver Tier Orchestration

Multi-watcher orchestration, structured planning, human-in-the-loop approval,
MCP server for external actions, scheduling, and skill chaining.
"""

__version__ = "0.1.0"
__author__ = "AI Employee Project"

from .watchers import Watcher, GmailWatcher, FilesystemWatcher
from .scheduler import CronRunner, ScheduledTask
from .services import PlanGenerator, Plan, ApprovalRequest, Orchestrator

__all__ = [
    # Watchers
    "Watcher",
    "GmailWatcher",
    "FilesystemWatcher",
    # Scheduler
    "CronRunner",
    "ScheduledTask",
    # Services
    "PlanGenerator",
    "Plan",
    "ApprovalRequest",
    "Orchestrator",
]
