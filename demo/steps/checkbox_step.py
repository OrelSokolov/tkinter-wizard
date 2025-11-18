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


class CheckboxStep(WizardStep):
    """Step with checkbox for error selection"""
    
    def __init__(self, wizard_app):
        super().__init__(wizard_app)
        self.error_checkbox = tk.BooleanVar(value=False)
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="System Check", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Check the option below to simulate an error:",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        checkbox_frame = tk.Frame(content_frame)
        checkbox_frame.pack(anchor=tk.W, fill=tk.X, padx=20)
        
        ttk.Checkbutton(checkbox_frame, 
                       text="Trigger wizard error", 
                       variable=self.error_checkbox).pack(anchor=tk.W, pady=5)
        
        warning = tk.Label(content_frame, 
                          text="(If unchecked, wizard will complete successfully)",
                          font=("Arial", 9), fg="gray")
        warning.pack(anchor=tk.W, padx=20, pady=(5, 0))
    
    def create_process(self):
        return None

