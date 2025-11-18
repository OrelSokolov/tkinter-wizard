# -*- coding: utf-8 -*-
import tkinter as tk
from ..wizard_step import WizardStep


class WelcomeStep(WizardStep):
    """Welcome step"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Welcome!", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        message = tk.Label(content_frame, 
                          text="This wizard will help you install the program.\n\n"
                               "Click 'Next' to continue.",
                          justify=tk.LEFT, font=("Arial", 10))
        message.pack(pady=10)
        
        icon_label = tk.Label(content_frame, text="☺", font=("Arial", 48))
        icon_label.pack(pady=30)
    
    def create_process(self):
        # No process, can proceed immediately
        return None

