# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from .enums import StepStatus
from .wizard_config import WizardConfig


class WizardApp:
    """
    Main wizard class. Standard component that doesn't change.
    Built from WizardStep objects.
    """
    
    def __init__(self, root, steps=None, config=None):
        """
        Args:
            root: root Tkinter window
            steps: list of WizardStep objects (can be set later via set_steps)
            config: WizardConfig object (optional, creates default if not provided)
        """
        self.root = root
        self.config = config or WizardConfig()
        
        # Set window title from config
        title = self.config.wizard_name
        if self.config.short_description:
            title = "{} - {}".format(title, self.config.short_description)
        self.root.title(title)
        
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Configure styles using system theme
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        
        # Select Windows system theme if available
        if 'vista' in available_themes:
            self.style.theme_use('vista')
        elif 'winnative' in available_themes:
            self.style.theme_use('winnative')
        elif 'xpnative' in available_themes:
            self.style.theme_use('xpnative')
        else:
            if available_themes:
                self.style.theme_use(available_themes[0])
        
        # Default steps (can be overridden)
        self._welcome_step = None
        self._end_fail_step = None
        self._end_success_step = None
        
        # Initialize default steps
        self._init_default_steps()
        
        self.steps = []
        self.current_step_index = 0
        
        # Create container for steps
        self.content_frame = tk.Frame(self.root, padx=20, pady=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation buttons
        self.nav_frame = tk.Frame(self.root, padx=20, pady=10)
        self.nav_frame.pack(fill=tk.X)
        
        self.back_btn = ttk.Button(self.nav_frame, text="< Back", 
                                   command=self.prev_step, state="disabled")
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = ttk.Button(self.nav_frame, text="Next >", 
                                   command=self.next_step)
        self.next_btn.pack(side=tk.RIGHT)
        
        self.cancel_btn = ttk.Button(self.nav_frame, text="Cancel", 
                                     command=self.cancel_process)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Set steps if provided
        if steps:
            self.set_steps(steps)
    
    def _init_default_steps(self):
        """Initialize default welcome, end_fail, and end_success steps"""
        try:
            from .steps.welcome_step import WelcomeStep
            from .steps.end_with_fail_step import EndWithFailStep
            from .steps.end_success_step import EndSuccessStep
            
            self._welcome_step = WelcomeStep(self)
            self._end_fail_step = EndWithFailStep(self)
            self._end_success_step = EndSuccessStep(self)
        except ImportError:
            # If default steps not available, create minimal stubs
            from .wizard_step import WizardStep
            
            class DefaultWelcomeStep(WizardStep):
                def create_content(self, content_frame):
                    tk.Label(content_frame, text="Welcome", font=("Arial", 16, "bold")).pack()
                def create_process(self):
                    return None
            
            class DefaultEndFailStep(WizardStep):
                def create_content(self, content_frame):
                    tk.Label(content_frame, text="Error", font=("Arial", 16, "bold"), fg="red").pack()
                def create_process(self):
                    return None
            
            class DefaultEndSuccessStep(WizardStep):
                def create_content(self, content_frame):
                    tk.Label(content_frame, text="Success", font=("Arial", 16, "bold"), fg="green").pack()
                def create_process(self):
                    return None
            
            self._welcome_step = DefaultWelcomeStep(self)
            self._end_fail_step = DefaultEndFailStep(self)
            self._end_success_step = DefaultEndSuccessStep(self)
    
    def set_welcome_step(self, step):
        """Set custom welcome step"""
        self._welcome_step = step
    
    def set_end_failed_step(self, step):
        """Set custom end failed step"""
        self._end_fail_step = step
    
    def set_end_success_step(self, step):
        """Set custom end success step"""
        self._end_success_step = step
    
    def set_steps(self, steps):
        """Set wizard steps (automatically adds welcome and end_success steps)"""
        # Build final steps list: welcome + user steps + end_success
        final_steps = []
        
        # Add welcome step if not already present
        if self._welcome_step:
            final_steps.append(self._welcome_step)
        
        # Add user steps
        final_steps.extend(steps)
        
        # Add end_success step if not already present
        if self._end_success_step:
            # Check if end_success_step is already in steps
            has_end_success = False
            try:
                from .steps.end_success_step import EndSuccessStep
                has_end_success = any(isinstance(s, EndSuccessStep) for s in final_steps)
            except ImportError:
                has_end_success = any(s.__class__.__name__ == 'EndSuccessStep' for s in final_steps)
            
            if not has_end_success:
                final_steps.append(self._end_success_step)
        
        self.steps = final_steps
        self.current_step_index = 0
        if self.steps:
            self.show_current_step()
    
    def clear_content(self):
        """Clear current step content"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_current_step(self):
        """Show current step"""
        self.clear_content()
        
        if 0 <= self.current_step_index < len(self.steps):
            step = self.steps[self.current_step_index]
            step.render(self.content_frame)
        
        self.update_navigation()
    
    def update_navigation(self):
        """Update navigation button states"""
        current_step = None
        if 0 <= self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
        
        # Get completion step classes for checking
        try:
            from .steps.end_with_fail_step import EndWithFailStep
            from .steps.end_success_step import EndSuccessStep
        except ImportError:
            EndWithFailStep = None
            EndSuccessStep = None
        
        # Check if current step is end step
        is_end_fail = False
        is_end_success = False
        
        if EndWithFailStep and current_step and isinstance(current_step, EndWithFailStep):
            is_end_fail = True
        elif current_step and current_step.__class__.__name__ == 'EndWithFailStep':
            is_end_fail = True
        
        if EndSuccessStep and current_step and isinstance(current_step, EndSuccessStep):
            is_end_success = True
        elif current_step and current_step.__class__.__name__ == 'EndSuccessStep':
            is_end_success = True
        
        # Handle end fail step - show only Finish button
        if is_end_fail:
            self.back_btn.pack_forget()
            self.cancel_btn.pack_forget()
            # Make sure Next button is visible and configured as Finish
            try:
                self.next_btn.pack(side=tk.RIGHT)
            except:
                pass
            self.next_btn.config(text="Finish", command=self.root.quit)
            self.next_btn.config(state="normal")
            return
        
        # Handle end success step - show only Finish button
        if is_end_success:
            self.back_btn.pack_forget()
            self.cancel_btn.pack_forget()
            # Make sure Next button is visible and configured as Finish
            try:
                self.next_btn.pack(side=tk.RIGHT)
            except:
                pass
            self.next_btn.config(text="Finish", command=self.root.quit)
            self.next_btn.config(state="normal")
            return
        
        # Make sure buttons are visible (if they were hidden earlier)
        try:
            self.next_btn.pack(side=tk.RIGHT)
        except:
            pass
        try:
            self.cancel_btn.pack(side=tk.RIGHT, padx=(0, 10))
        except:
            pass
        
        # "Back" button - hide on first step, disable if process is running
        if self.current_step_index == 0:
            # Hide "Back" button on first step
            self.back_btn.pack_forget()
        else:
            # Show "Back" button on other steps
            try:
                self.back_btn.pack(side=tk.LEFT)
            except:
                pass
            
            if current_step and current_step.status == StepStatus.RUNNING:
                # Disable "Back" during process execution
                self.back_btn.config(state="disabled")
            else:
                self.back_btn.config(state="normal")
        
        # "Next" button
        if self.current_step_index >= len(self.steps) - 1:
            self.next_btn.config(text="Finish", command=self.root.quit)
            self.next_btn.config(state="normal")
        else:
            current_step = self.steps[self.current_step_index]
            
            # Check if process can proceed to next step
            if current_step.can_proceed():
                self.next_btn.config(text="Next >", command=self.next_step)
                self.next_btn.config(state="normal")
            else:
                # Process not yet completed, disable button
                self.next_btn.config(text="Next >", command=self.next_step)
                self.next_btn.config(state="disabled")
    
    def on_step_status_changed(self, step):
        """Called when step status changes"""
        # Check if step completed with error, show error
        if step.is_failed():
            # Use end_fail_step
            if self._end_fail_step:
                # Check if end_fail_step is already in steps
                has_end_fail = False
                try:
                    from .steps.end_with_fail_step import EndWithFailStep
                    has_end_fail = any(isinstance(s, EndWithFailStep) for s in self.steps)
                except ImportError:
                    has_end_fail = any(s.__class__.__name__ == 'EndWithFailStep' for s in self.steps)
                
                if not has_end_fail:
                    self.steps.append(self._end_fail_step)
                
                # Go to end fail step
                for i, s in enumerate(self.steps):
                    if s is self._end_fail_step:
                        self.current_step_index = i
                        self.show_current_step()
                        return
                    try:
                        from .steps.end_with_fail_step import EndWithFailStep
                        if isinstance(s, EndWithFailStep):
                            self.current_step_index = i
                            self.show_current_step()
                            return
                    except ImportError:
                        if s.__class__.__name__ == 'EndWithFailStep':
                            self.current_step_index = i
                            self.show_current_step()
                            return
        
        # Update navigation
        self.update_navigation()
    
    def cancel_process(self):
        """Cancel current process and exit wizard with error"""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Cancel Wizard",
            "Are you sure you want to cancel the wizard?",
            icon='question'
        )
        
        # If user clicked "No", don't cancel
        if not result:
            return
        
        current_step = None
        if 0 <= self.current_step_index < len(self.steps):
            current_step = self.steps[self.current_step_index]
        
        # Cancel current step's process if it's running
        if current_step and current_step.process:
            current_step.process.cancel()
        
        # Close wizard
        self.root.quit()
    
    def next_step(self):
        """Go to next step"""
        current_step = self.steps[self.current_step_index]
        
        # Check if can proceed
        if not current_step.can_proceed():
            return
        
        # If step completed with error, go to end_fail_step
        if current_step.is_failed():
            if self._end_fail_step:
                # Check if end_fail_step is already in steps
                has_end_fail = False
                try:
                    from .steps.end_with_fail_step import EndWithFailStep
                    has_end_fail = any(isinstance(s, EndWithFailStep) for s in self.steps)
                except ImportError:
                    has_end_fail = any(s.__class__.__name__ == 'EndWithFailStep' for s in self.steps)
                
                if not has_end_fail:
                    self.steps.append(self._end_fail_step)
                
                # Go to end fail step
                for i, s in enumerate(self.steps):
                    if s is self._end_fail_step:
                        self.current_step_index = i
                        self.show_current_step()
                        return
                    try:
                        from .steps.end_with_fail_step import EndWithFailStep
                        if isinstance(s, EndWithFailStep):
                            self.current_step_index = i
                            self.show_current_step()
                            return
                    except ImportError:
                        if s.__class__.__name__ == 'EndWithFailStep':
                            self.current_step_index = i
                            self.show_current_step()
                            return
        
        # Go to next step
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            self.show_current_step()
    
    def prev_step(self):
        """Go to previous step"""
        if self.current_step_index > 0:
            current_step = self.steps[self.current_step_index]
            if current_step and current_step.status == StepStatus.RUNNING:
                return  # Cannot go back during process execution
            
            self.current_step_index -= 1
            self.show_current_step()
