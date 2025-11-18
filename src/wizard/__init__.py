# -*- coding: utf-8 -*-
"""
Tkinter Wizard Library

Library for creating installer wizards based on Tkinter.
"""

from .enums import StepStatus
from .progress_interface import ProgressInterface, ProgressBarAdapter
from .wizard_process import WizardProcess
from .wizard_step import WizardStep
from .wizard_app import WizardApp

__all__ = [
    'StepStatus',
    'ProgressInterface',
    'ProgressBarAdapter',
    'WizardProcess',
    'WizardStep',
    'WizardApp',
]

__version__ = '0.1.0'

