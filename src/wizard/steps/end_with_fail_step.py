# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ..wizard_step import WizardStep


class EndWithFailStep(WizardStep):
    """End with fail step"""
    
    def create_content(self, content_frame):
        title = ttk.Label(content_frame, text="Wizard Completed with Errors", 
                         font=("Arial", 16, "bold"), foreground="red")
        title.pack(pady=(0, 20))
        
        icon_label = ttk.Label(content_frame, text="✗", 
                              font=("Arial", 48), foreground="red")
        icon_label.pack(pady=20)
        
        message = ttk.Label(content_frame, 
                           text="An error occurred during wizard execution.\n"
                                "The wizard was not completed successfully.",
                           justify=tk.CENTER, font=("Arial", 10))
        message.pack(pady=10)
    
    def create_process(self):
        return None

