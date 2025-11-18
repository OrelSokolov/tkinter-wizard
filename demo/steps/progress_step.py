# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
from tkinter import ttk
import time

# Add src to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from wizard import WizardStep, WizardProcess, ProgressBarAdapter


class ProgressProcess(WizardProcess):
    """Process with progress bar"""
    
    def run(self):
        """Simulate process with progress (runs in separate thread)"""
        self.start_time = time.time()
        
        # Reset start time in progress_interface
        if self.progress_interface and hasattr(self.progress_interface, 'reset_start_time'):
            self.progress_interface.reset_start_time()
        
        # Simulate process with cancellation check
        while not self.is_cancelled():
            elapsed = time.time() - self.start_time
            percent = min((elapsed / 3.0) * 100, 100)  # 3 seconds for process
            
            # Calculate ETA
            if percent < 100 and percent > 0:
                # Calculate remaining time based on current speed
                remaining = (100 - percent) * (elapsed / percent)
            elif percent >= 100:
                remaining = 0
            else:
                # At start can use approximate time (3 seconds)
                remaining = 3.0
            
            self.update_progress(percent, remaining)
            
            if percent >= 100:
                # Complete successfully
                if not self.is_cancelled():
                    self.set_success(True)
                break
            
            # Sleep a bit before next iteration
            time.sleep(0.03)
        
        # If cancelled, complete with failure
        if self.is_cancelled():
            self.set_success(False)


class ProgressStep(WizardStep):
    """Step with progress bar"""
    
    def create_content(self, content_frame):
        title = tk.Label(content_frame, text="Preparing", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 20), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Please wait...",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 15))
        
        # Create progressbar and labels
        progress_frame = tk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, 
                                       variable=progress_var,
                                       maximum=100, length=500)
        progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        labels_frame = tk.Frame(progress_frame)
        labels_frame.pack(fill=tk.X)
        
        percent_label = tk.Label(labels_frame, text="0%", font=("Arial", 10))
        percent_label.pack(side=tk.LEFT)
        
        eta_label = tk.Label(labels_frame, text="Remaining: --:--", 
                            font=("Arial", 9), fg="gray")
        eta_label.pack(side=tk.LEFT, padx=(20, 0))
        
        elapsed_label = tk.Label(labels_frame, text="Elapsed: 0:00", 
                                font=("Arial", 9), fg="gray")
        elapsed_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Save references for use in process
        self.progress_bar = progress_bar
        self.progress_var = progress_var
        self.percent_label = percent_label
        self.eta_label = eta_label
        self.elapsed_label = elapsed_label
    
    def create_process(self):
        # Create adapter for progressbar
        progress_interface = ProgressBarAdapter(
            self.progress_bar,
            progress_var=self.progress_var,
            percent_label=self.percent_label,
            eta_label=self.eta_label,
            elapsed_label=self.elapsed_label
        )
        
        # Create process
        process = ProgressProcess(
            progress_interface=progress_interface,
            state_callback=self._on_process_complete
        )
        
        return process

