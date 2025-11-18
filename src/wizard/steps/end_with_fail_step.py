# -*- coding: utf-8 -*-
import tkinter as tk
from ..wizard_step import WizardStep


class EndWithFailStep(WizardStep):
    """End with fail step"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Installation Completed with Errors", 
                        font=("Arial", 16, "bold"), fg="red")
        title.pack(pady=(0, 20))
        
        icon_label = tk.Label(content_frame, text="✗", 
                             font=("Arial", 48), fg="red")
        icon_label.pack(pady=20)
        
        message = tk.Label(content_frame, 
                          text="An error occurred during installation.\n"
                               "Installation was not completed successfully.",
                          justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
    
    def create_process(self):
        return None

