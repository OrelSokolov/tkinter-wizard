# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ..wizard_step import WizardStep


class WelcomeStep(WizardStep):
    """Welcome step"""
    
    def create_content(self, content_frame):
        title = ttk.Label(content_frame, text="Welcome!", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20))
        
        wizard_name = self.wizard_app.config.wizard_name if self.wizard_app.config else "Wizard"
        message_text = "Welcome to {}!\n\n".format(wizard_name)
        if self.wizard_app.config and self.wizard_app.config.short_description:
            message_text += "{}\n\n".format(self.wizard_app.config.short_description)
        message_text += "Click 'Next' to continue."
        
        message = ttk.Label(content_frame, 
                           text=message_text,
                           justify=tk.LEFT, font=("Arial", 10))
        message.pack(pady=10)
        
        icon_label = ttk.Label(content_frame, text="☺", font=("Arial", 48))
        icon_label.pack(pady=30)
    
    def create_process(self):
        # No process, can proceed immediately
        return None

