# -*- coding: utf-8 -*-
import tkinter as tk
import time
from abc import ABC, abstractmethod


class ProgressInterface(ABC):
    """Interface for working with progress bar"""
    
    @abstractmethod
    def set_percent(self, percent):
        """Set completion percentage (0-100)"""
        pass
    
    @abstractmethod
    def set_eta(self, seconds):
        """Set remaining time (in seconds)"""
        pass
    
    @abstractmethod
    def set_elapsed_time(self, seconds):
        """Set elapsed time (in seconds)"""
        pass


class ProgressBarAdapter(ProgressInterface):
    """Adapter for ttk.Progressbar with additional information"""
    
    def __init__(self, progressbar, progress_var=None, percent_label=None, eta_label=None, elapsed_label=None):
        self.progressbar = progressbar
        self.progress_var = progress_var
        self.percent_label = percent_label
        self.eta_label = eta_label
        self.elapsed_label = elapsed_label
        self.start_time = time.time()
    
    def reset_start_time(self):
        """Reset start time (called at process start)"""
        self.start_time = time.time()
    
    def set_percent(self, percent):
        """Set completion percentage"""
        try:
            if self.progress_var:
                self.progress_var.set(percent)
            elif self.progressbar:
                try:
                    self.progressbar['value'] = percent
                except tk.TclError:
                    pass  # Widget destroyed
            
            if self.percent_label:
                try:
                    self.percent_label.config(text="{}%".format(int(percent)))
                except tk.TclError:
                    pass  # Widget destroyed
        except:
            pass  # Widgets may have been destroyed
    
    def set_eta(self, seconds):
        """Set remaining time"""
        if self.eta_label:
            try:
                if seconds is not None and seconds > 0:
                    minutes = int(seconds // 60)
                    secs = int(seconds % 60)
                    self.eta_label.config(text="Remaining: {:02d}:{:02d}".format(minutes, secs))
                else:
                    self.eta_label.config(text="Remaining: --:--")
            except tk.TclError:
                pass  # Widget destroyed
    
    def set_elapsed_time(self, seconds):
        """Set elapsed time"""
        if self.elapsed_label:
            try:
                minutes = int(seconds // 60)
                secs = int(seconds % 60)
                self.elapsed_label.config(text="Elapsed: {}:{}".format(minutes, secs))
            except tk.TclError:
                pass  # Widget destroyed
    
    def get_elapsed(self):
        """Get elapsed time from start"""
        return time.time() - self.start_time

