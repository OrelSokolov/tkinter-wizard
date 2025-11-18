# -*- coding: utf-8 -*-
import tkinter as tk
from ..wizard_step import WizardStep


class EndSuccessStep(WizardStep):
    """End success step"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Wizard Completed Successfully!", 
                        font=("Arial", 16, "bold"), fg="green")
        title.pack(pady=(0, 20))
        
        icon_label = tk.Label(content_frame, text="✓", 
                             font=("Arial", 48), fg="green")
        icon_label.pack(pady=20)
        
        wizard_name = self.wizard_app.config.wizard_name if self.wizard_app.config else "Wizard"
        message = tk.Label(content_frame, 
                          text="The wizard has completed successfully.\n"
                               "Click 'Finish' to close the wizard.",
                          justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
    
    def create_process(self):
        return None


