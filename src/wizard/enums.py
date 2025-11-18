# -*- coding: utf-8 -*-
from enum import Enum


class StepStatus(Enum):
    """Step status"""
    PENDING = "pending"  # Waiting for execution
    RUNNING = "running"  # Process is running
    SUCCESS = "success"  # Successfully completed
    FAILED = "failed"    # Completed with error

