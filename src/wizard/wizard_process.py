# -*- coding: utf-8 -*-
import tkinter as tk
import time
import threading


class WizardProcess:
    """
    Abstraction for a process that runs in a wizard step.
    
    Accepts either ProgressInterface for displaying progress,
    or an IO object (e.g., TextArea) for logging.
    
    The process runs in a separate thread and can be cancelled.
    """
    
    def __init__(self, progress_interface=None, logger=None, state_callback=None, root=None):
        """
        Args:
            progress_interface: object implementing ProgressInterface
            logger: object for logging (e.g., ScrolledText)
            state_callback: function to update state (allows transition)
            root: root Tkinter window (for root.after)
        """
        self.progress_interface = progress_interface
        self.logger = logger
        self.state_callback = state_callback
        self.root = root
        self.success = True  # Success by default
        self.start_time = None
        self._cancelled = False
        self._thread = None
        self._lock = threading.Lock()
    
    def is_cancelled(self):
        """Check if the process was cancelled"""
        with self._lock:
            return self._cancelled
    
    def cancel(self):
        """Cancel process execution"""
        with self._lock:
            self._cancelled = True
        # If process completed with cancellation, set failure
        if self.state_callback:
            self.state_callback(False)
    
    def log(self, message):
        """Output message to log"""
        if self.logger and not self.is_cancelled():
            try:
                self.logger.insert(tk.END, message + "\n")
                self.logger.see(tk.END)
                self.logger.update()
            except:
                pass  # Widget may have been destroyed
    
    def update_progress(self, percent, eta=None):
        """Update progress (called from process thread)"""
        if self.is_cancelled():
            return
        
        if self.progress_interface:
            # Update UI through root.after in main thread
            if self.root:
                def update_ui():
                    if not self.is_cancelled() and self.progress_interface:
                        try:
                            self.progress_interface.set_percent(percent)
                            
                            # Always update ETA (if provided or calculate automatically)
                            if eta is not None:
                                self.progress_interface.set_eta(eta)
                            elif percent > 0 and percent < 100:
                                # Calculate ETA automatically if not provided
                                if hasattr(self.progress_interface, 'get_elapsed'):
                                    elapsed = self.progress_interface.get_elapsed()
                                    if elapsed > 0:
                                        total_time = (elapsed / percent) * 100
                                        remaining = total_time - elapsed
                                        self.progress_interface.set_eta(remaining)
                            
                            # Update elapsed time
                            if hasattr(self.progress_interface, 'get_elapsed'):
                                elapsed = self.progress_interface.get_elapsed()
                                self.progress_interface.set_elapsed_time(elapsed)
                        except:
                            pass  # Widgets may have been destroyed
                
                self.root.after(0, update_ui)
    
    def run(self):
        """
        Run the process. Should be overridden in subclasses.
        By default completes successfully without action.
        
        This method runs in a separate thread.
        """
        self.start_time = time.time()
        # By default do nothing, complete successfully
        if not self.is_cancelled() and self.state_callback:
            if self.root:
                self.root.after(0, lambda: self.state_callback(self.success))
            else:
                self.state_callback(self.success)
    
    def start(self):
        """Start the process in a separate thread"""
        if self._thread is not None and self._thread.is_alive():
            return  # Thread already started
        
        self._cancelled = False
        self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
        self._thread.start()
    
    def _run_wrapper(self):
        """Wrapper for executing run() in thread"""
        try:
            self.run()
        except:
            # On error, complete with failure
            if not self.is_cancelled() and self.state_callback:
                if self.root:
                    self.root.after(0, lambda: self.state_callback(False))
                else:
                    self.state_callback(False)
    
    def wait(self, timeout=None):
        """Wait for process completion"""
        if self._thread:
            self._thread.join(timeout)
    
    def set_success(self, success):
        """Set execution status and notify callback"""
        if self.is_cancelled():
            return  # If cancelled, don't change status
        
        self.success = success
        if self.state_callback:
            if self.root:
                self.root.after(0, lambda: self.state_callback(success))
            else:
                self.state_callback(success)

