# -*- coding: utf-8 -*-
import tkinter as tk
from ..wizard_step import WizardStep


class SuccessCompletionStep(WizardStep):
    """Success completion step"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Installation Completed Successfully!", 
                        font=("Arial", 16, "bold"), fg="green")
        title.pack(pady=(0, 20))
        
        icon_label = tk.Label(content_frame, text="✓", 
                             font=("Arial", 48), fg="green")
        icon_label.pack(pady=20)
        
        message = tk.Label(content_frame, 
                          text="The program has been successfully installed on your computer.\n"
                               "Click 'Finish' to close the installation wizard.",
                          justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
        
        # Get selected configuration
        from .configuration_step import ConfigurationStep
        
        config_name = "Unknown"
        for step in self.wizard_app.steps:
            if isinstance(step, ConfigurationStep):
                configs = {
                    "standard": "Standard installation",
                    "minimal": "Minimal installation",
                    "full": "Full installation"
                }
                config_name = configs.get(step.config_choice.get(), "Unknown")
                break
        
        summary = tk.Label(content_frame, 
                          text="Selected configuration: {}".format(config_name),
                          justify=tk.CENTER, font=("Arial", 9), fg="gray")
        summary.pack(pady=(10, 0))
    
    def create_process(self):
        return None


