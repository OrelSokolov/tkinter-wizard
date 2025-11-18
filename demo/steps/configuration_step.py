# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
from tkinter import ttk

# Add src to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from wizard import WizardStep


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
                       text="Select configuration type:",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        radio_frame = tk.Frame(content_frame)
        radio_frame.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        ttk.Radiobutton(radio_frame, text="Standard", 
                       variable=self.config_choice, value="standard").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Minimal", 
                       variable=self.config_choice, value="minimal").pack(anchor=tk.W, pady=5)
        
        ttk.Radiobutton(radio_frame, text="Full", 
                       variable=self.config_choice, value="full").pack(anchor=tk.W, pady=5)
    
    def create_process(self):
        return None

