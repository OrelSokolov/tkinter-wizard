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


class ThemeStep(WizardStep):
    """Step for selecting theme"""
    
    def __init__(self, wizard_app):
        super().__init__(wizard_app)
        # Get current theme and available themes
        available_themes = wizard_app.style.theme_names()
        current_theme = wizard_app.style.theme_use()
        # Set initial value to current theme
        self.theme_choice = tk.StringVar(value=current_theme if current_theme in available_themes else available_themes[0] if available_themes else "")
        self.available_themes = available_themes
    
    def create_content(self, content_frame):
        title = ttk.Label(content_frame, text="Theme Selection", 
                         font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = ttk.Label(content_frame, 
                        text="Select a theme for the wizard interface. The theme will be applied immediately:",
                        justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        # Show current theme info at the top
        current_theme = self.wizard_app.style.theme_use()
        current_info = ttk.Label(content_frame, 
                                text=f"Current theme: {current_theme}",
                                font=("Arial", 10, "bold"),
                                foreground="blue")
        current_info.pack(anchor=tk.W, pady=(0, 15))
        
        # Create frame for radio buttons with scrollable area if many themes
        theme_container = ttk.Frame(content_frame)
        theme_container.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        
        # Create frame for radio buttons
        theme_frame = ttk.Frame(theme_container, padding=(20, 0))
        theme_frame.pack(anchor=tk.W, fill=tk.BOTH, expand=True)
        
        # Create radio buttons for each available theme (sorted alphabetically)
        sorted_themes = sorted(self.available_themes)
        for theme in sorted_themes:
            radio = ttk.Radiobutton(theme_frame, 
                                   text=theme,
                                   variable=self.theme_choice, 
                                   value=theme,
                                   command=self._on_theme_changed)
            radio.pack(anchor=tk.W, pady=2)
    
    def _on_theme_changed(self):
        """Called when theme selection changes"""
        selected_theme = self.theme_choice.get()
        if selected_theme and selected_theme in self.available_themes:
            # Apply theme immediately when selected
            self.wizard_app.style.theme_use(selected_theme)
    
    def create_process(self):
        return None

