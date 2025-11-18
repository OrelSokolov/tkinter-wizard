# -*- coding: utf-8 -*-
"""
Example usage of tkinter-wizard library
"""
import sys
import os
import tkinter as tk

# Add parent directory to path for development
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Add demo directory to path for imports
demo_dir = os.path.dirname(os.path.abspath(__file__))
if demo_dir not in sys.path:
    sys.path.insert(0, demo_dir)

from wizard import WizardApp
from steps.configuration_step import ConfigurationStep
from steps.progress_step import ProgressStep
from steps.checkbox_step import CheckboxStep
from steps.logs_step import LogsStep


def main():
    root = tk.Tk()
    
    # Create wizard first (without steps)
    wizard = WizardApp(root)
    
    # Create wizard steps (WelcomeStep and EndSuccessStep are added automatically)
    # Pass wizard_app to each step
    steps = [
        ConfigurationStep(wizard),
        ProgressStep(wizard),
        CheckboxStep(wizard),
        LogsStep(wizard),
    ]
    
    # Set steps in wizard (WelcomeStep and EndSuccessStep will be added automatically)
    wizard.set_steps(steps)
    
    root.mainloop()


if __name__ == "__main__":
    main()

