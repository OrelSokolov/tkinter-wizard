# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from ..wizard_step import WizardStep


class ConfigurationStep(WizardStep):
    """Configuration step"""
    
    def __init__(self, wizard_app):
        super().__init__(wizard_app)
        self.config_choice = tk.StringVar(value="standard")
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Configuration", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Select installation type:",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        radio_frame = tk.Frame(content_frame)
        radio_frame.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        ttk.Radiobutton(radio_frame, text="Standard installation", 
                       variable=self.config_choice, value="standard").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Minimal installation", 
                       variable=self.config_choice, value="minimal").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Full installation", 
                       variable=self.config_choice, value="full").pack(anchor=tk.W, pady=5)
    
    def create_process(self):
        return None

