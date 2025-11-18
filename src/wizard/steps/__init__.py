# -*- coding: utf-8 -*-
"""
Example steps for wizard (optional)
"""

from .welcome_step import WelcomeStep
from .configuration_step import ConfigurationStep
from .progress_step import ProgressStep, ProgressProcess
from .checkbox_step import CheckboxStep
from .logs_step import LogsStep, LogsProcess
from .end_with_fail_step import EndWithFailStep
from .end_success_step import EndSuccessStep

__all__ = [
    'WelcomeStep',
    'ConfigurationStep',
    'ProgressStep',
    'ProgressProcess',
    'CheckboxStep',
    'LogsStep',
    'LogsProcess',
    'EndWithFailStep',
    'EndSuccessStep',
]

