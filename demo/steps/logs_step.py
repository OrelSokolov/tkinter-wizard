# -*- coding: utf-8 -*-
import sys
import os
import tkinter as tk
from tkinter import scrolledtext
import time

# Add src to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.join(parent_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from wizard import WizardStep, WizardProcess


class LogsProcess(WizardProcess):
    """Process with logging"""
    
    def __init__(self, logger, state_callback, should_fail=False):
        super().__init__(logger=logger, state_callback=state_callback)
        self.should_fail = should_fail
        self.logs = [
            "[INFO] Initializing wizard...",
            "[INFO] Checking system requirements...",
            "[OK] System requirements met",
            "[INFO] Preparing files...",
            "[INFO] Copying files to target directory...",
            "[OK] Files copied successfully",
            "[INFO] Creating registry entries...",
            "[OK] Registry updated",
            "[INFO] Registering services...",
            "[OK] Services registered",
            "[INFO] Creating shortcuts...",
            "[OK] Shortcuts created",
            "[INFO] Updating environment variables...",
            "[OK] Environment variables updated",
            "[INFO] Finalizing wizard...",
        ]
    
    def run(self):
        """Stream logs (runs in separate thread)"""
        self.start_time = time.time()
        
        # If should fail and no logger, complete with error immediately
        if self.should_fail and not self.logger:
            time.sleep(0.1)  # Small delay
            if not self.is_cancelled():
                self.set_success(False)
            return
        
        # Output logs line by line with cancellation check
        for log in self.logs:
            if self.is_cancelled():
                break
            
            self.log(log)
            time.sleep(0.5)  # Delay between logs
        
        # All logs added
        if not self.is_cancelled():
            if self.should_fail:
                self.log("[ERROR] Wizard completed with error!")
                self.set_success(False)
            else:
                self.log("[SUCCESS] Wizard completed successfully!")
                self.set_success(True)
        
        # If cancelled, complete with failure
        if self.is_cancelled():
            self.set_success(False)


class LogsStep(WizardStep):
    """Step with logs"""
    
    def create_content(self, content_frame):
        # Check if error was selected in previous step BEFORE creating content
        from .checkbox_step import CheckboxStep
        
        checkbox_step = None
        for step in self.wizard_app.steps:
            if isinstance(step, CheckboxStep):
                checkbox_step = step
                break
        
        self.should_fail = checkbox_step and checkbox_step.error_checkbox.get()
        
        # If should fail, don't show console, process will complete immediately
        if self.should_fail:
            title = tk.Label(content_frame, text="Checking Status", 
                            font=("Arial", 16, "bold"))
            title.pack(pady=(0, 20), anchor=tk.W)
            
            info = tk.Label(content_frame, 
                           text="Checking wizard status...",
                           justify=tk.LEFT, font=("Arial", 10))
            info.pack(anchor=tk.W, pady=(0, 15))
            return
        
        title = tk.Label(content_frame, text="Processing", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=(0, 15), anchor=tk.W)
        
        info = tk.Label(content_frame, 
                       text="Processing...",
                       justify=tk.LEFT, font=("Arial", 10))
        info.pack(anchor=tk.W, pady=(0, 10))
        
        # Text field for logs
        self.log_text = scrolledtext.ScrolledText(content_frame, 
                                                  height=15, 
                                                  width=70,
                                                  font=("Consolas", 9),
                                                  bg="white",
                                                  fg="black",
                                                  insertbackground="black")
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def create_process(self):
        # If should fail, create process that completes with error immediately
        if self.should_fail:
            process = LogsProcess(
                logger=None,  # No logger, as console is not shown
                state_callback=self._on_process_complete,
                should_fail=True
            )
            return process
        
        # Create logging process
        process = LogsProcess(
            logger=self.log_text,
            state_callback=self._on_process_complete,
            should_fail=False
        )
        
        return process

