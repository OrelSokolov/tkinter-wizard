# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sys
import platform
from .enums import StepStatus
from .wizard_config import WizardConfig

# Try to import ttkthemes for additional themes
try:
    from ttkthemes import ThemedStyle
    TTKTHEMES_AVAILABLE = True
except ImportError:
    TTKTHEMES_AVAILABLE = False
    ThemedStyle = None


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
        
        # Set window size and constraints
        # On Linux, we need to set minsize and use update_idletasks for proper sizing
        # We'll calculate optimal size based on content dynamically
        self.root.minsize(800, 600)
        
        # Get screen dimensions to limit max size and center window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Set maxsize to 90% of screen size to leave some margin
        self.root.maxsize(int(screen_width * 0.9), int(screen_height * 0.9))
        
        # Initial geometry (will be adjusted based on content)
        initial_width = 900
        initial_height = 650
        self.root.geometry(f"{initial_width}x{initial_height}")
        
        # Center window on screen
        self._center_window(initial_width, initial_height)
        
        self.root.resizable(True, True)  # Allow resizing and maximizing window
        
        # Track if we've already adjusted size once (to avoid jumping on every step change)
        self._size_adjusted = False
        
        # Configure styles using system theme or ttkthemes if available
        if TTKTHEMES_AVAILABLE:
            # Use ThemedStyle from ttkthemes for better theme support
            self.style = ThemedStyle(self.root)
            available_themes = self.style.theme_names()
        else:
            # Fallback to standard ttk.Style
            self.style = ttk.Style()
            available_themes = self.style.theme_names()
        
        # Select appropriate theme based on platform
        selected_theme = None
        if platform.system() == 'Windows':
            # Select Windows system theme if available
            if 'vista' in available_themes:
                selected_theme = 'vista'
            elif 'winnative' in available_themes:
                selected_theme = 'winnative'
            elif 'xpnative' in available_themes:
                selected_theme = 'xpnative'
            elif available_themes:
                selected_theme = available_themes[0]
        else:
            # On Linux/Unix, prefer modern themes from ttkthemes if available
            if TTKTHEMES_AVAILABLE:
                # Preferred modern themes from ttkthemes
                preferred_themes = ['arc', 'equilux', 'adapta', 'clearlooks', 'elegance']
                for theme in preferred_themes:
                    if theme in available_themes:
                        selected_theme = theme
                        break
                # If no preferred theme found, use 'clam' or any available
                if not selected_theme:
                    if 'clam' in available_themes:
                        selected_theme = 'clam'
                    elif available_themes:
                        selected_theme = available_themes[0]
            else:
                # Fallback to built-in themes
                if 'clam' in available_themes:
                    selected_theme = 'clam'
                elif 'alt' in available_themes:
                    selected_theme = 'alt'
                elif available_themes:
                    selected_theme = available_themes[0]
        
        # Default steps (can be overridden)
        self._welcome_step = None
        self._end_fail_step = None
        self._end_success_step = None
        
        # Initialize default steps
        self._init_default_steps()
        
        self.steps = []
        self.current_step_index = 0
        
        # Create container for steps (use ttk.Frame to respect theme colors)
        self.content_frame = ttk.Frame(self.root, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Navigation buttons (use ttk.Frame to respect theme colors)
        self.nav_frame = ttk.Frame(self.root, padding=(20, 10))
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
        
        # Apply system theme (styles will be from the theme)
        if selected_theme:
            self.style.theme_use(selected_theme)
        
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
                    ttk.Label(content_frame, text="Welcome", font=("Arial", 16, "bold")).pack()
                def create_process(self):
                    return None
            
            class DefaultEndFailStep(WizardStep):
                def create_content(self, content_frame):
                    ttk.Label(content_frame, text="Error", font=("Arial", 16, "bold"), foreground="red").pack()
                def create_process(self):
                    return None
            
            class DefaultEndSuccessStep(WizardStep):
                def create_content(self, content_frame):
                    ttk.Label(content_frame, text="Success", font=("Arial", 16, "bold"), foreground="green").pack()
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
    
    def _center_window(self, width=None, height=None):
        """Center window on screen"""
        if width is None:
            width = self.root.winfo_width()
        if height is None:
            height = self.root.winfo_height()
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate center position
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set window position
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _calculate_optimal_size(self):
        """Calculate optimal window size based on current content"""
        # Update to get real widget sizes
        self.root.update_idletasks()
        
        # Calculate required width and height based on content
        max_width = 800  # Minimum width
        max_height = 600  # Minimum height
        
        # Helper to get widget dimensions (actual or requested)
        def get_widget_size(widget):
            """Get widget size, preferring actual size if available"""
            try:
                # Try actual size first (works for mapped widgets)
                width = widget.winfo_width()
                height = widget.winfo_height()
                
                # If width/height is 1, widget might not be mapped yet, use reqwidth/reqheight
                if width <= 1 or height <= 1:
                    width = widget.winfo_reqwidth()
                    height = widget.winfo_reqheight()
                
                # For text widgets with character-based sizing, convert to pixels
                # Text widgets: width/height in characters, need to convert
                if hasattr(widget, 'cget'):
                    try:
                        text_width = widget.cget('width')
                        text_height = widget.cget('height')
                        if isinstance(text_width, int) and text_width > 0:
                            # Approximate: 1 char ≈ 8-10 pixels (depends on font)
                            # Use a more conservative estimate
                            font = widget.cget('font') if widget.cget('font') else ('Arial', 9)
                            # Estimate pixel width: chars * 7 pixels (conservative)
                            width = max(width, text_width * 7)
                        if isinstance(text_height, int) and text_height > 0:
                            # Estimate pixel height: lines * 20 pixels (conservative for line height)
                            height = max(height, text_height * 20)
                    except:
                        pass
                
                return width, height
            except:
                return 0, 0
        
        # Iterate through all widgets in content_frame to find maximum dimensions
        def get_widget_requirements(widget, parent_x=0, parent_y=0):
            """Recursively get size requirements from widgets"""
            nonlocal max_width, max_height
            
            try:
                # Get widget dimensions
                width, height = get_widget_size(widget)
                
                if width <= 0 or height <= 0:
                    width = widget.winfo_reqwidth()
                    height = widget.winfo_reqheight()
                
                # Get widget position relative to parent
                x = widget.winfo_x()
                y = widget.winfo_y()
                
                # Calculate absolute position within content_frame
                abs_x = parent_x + x
                abs_y = parent_y + y
                
                # Update max dimensions
                widget_total_width = abs_x + width
                widget_total_height = abs_y + height
                
                if widget_total_width > max_width:
                    max_width = widget_total_width
                if widget_total_height > max_height:
                    max_height = widget_total_height
                
                # Recursively check children
                for child in widget.winfo_children():
                    get_widget_requirements(child, abs_x, abs_y)
            except:
                # Widget might be destroyed or not yet mapped, skip it
                pass
        
        # Check all widgets in content_frame
        for widget in self.content_frame.winfo_children():
            get_widget_requirements(widget)
        
        # Add padding and navigation frame
        # content_frame has padx=20, pady=20 (40 total horizontal, 40 total vertical)
        # nav_frame height (approximately 60-70px with padding and buttons)
        nav_height = 70
        
        required_width = max_width + 40  # content padding (20*2)
        required_height = max_height + 40 + nav_height  # content padding (20*2) + nav
        
        # Add some extra margin for window decorations and rounding
        required_width += 10
        required_height += 50  # Title bar + extra margin
        
        # Ensure we don't exceed maxsize
        max_width_allowed = self.root.winfo_screenwidth() * 0.9
        max_height_allowed = self.root.winfo_screenheight() * 0.9
        
        required_width = min(required_width, max_width_allowed)
        required_height = min(required_height, max_height_allowed)
        
        # Ensure minimum size
        required_width = max(required_width, 800)
        required_height = max(required_height, 600)
        
        return int(required_width), int(required_height)
    
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
        
        # On Linux/Ubuntu, ensure window geometry is properly applied after content is rendered
        # Calculate optimal size based on content to ensure everything fits
        self.root.update_idletasks()
        
        # Only adjust size on first step or if window is too small
        # This prevents window jumping on every step change
        current_width = self.root.winfo_width()
        current_height = self.root.winfo_height()
        
        # Calculate optimal size but only resize if necessary
        optimal_width, optimal_height = self._calculate_optimal_size()
        
        # Resize only if:
        # 1. First time showing content (size not adjusted yet), OR
        # 2. Current size is too small (below minimum or below optimal)
        should_resize = False
        new_width = current_width
        new_height = current_height
        
        if not self._size_adjusted:
            # First time - set optimal size
            should_resize = True
            new_width = optimal_width
            new_height = optimal_height
            self._size_adjusted = True
        elif current_width < 800 or current_height < 600:
            # Window is below minimum - enforce minimum
            should_resize = True
            new_width = max(800, optimal_width)
            new_height = max(600, optimal_height)
        elif current_width < optimal_width or current_height < optimal_height:
            # Window is smaller than optimal but above minimum
            # Only resize if significantly smaller (more than 50px difference) to avoid jitter
            if (optimal_width - current_width > 50) or (optimal_height - current_height > 50):
                should_resize = True
                new_width = optimal_width
                new_height = optimal_height
        
        if should_resize:
            # Get current window position to preserve it
            try:
                current_x = self.root.winfo_x()
                current_y = self.root.winfo_y()
                # Center if this is the first resize, otherwise preserve position
                if not self._size_adjusted or (current_x == 0 and current_y == 0):
                    # First resize or window at origin (0,0) - center it
                    self._center_window(new_width, new_height)
                else:
                    # Preserve current position
                    self.root.geometry(f"{new_width}x{new_height}+{current_x}+{current_y}")
            except:
                # Fallback to center if getting position fails
                self._center_window(new_width, new_height)
        
        # Ensure resizable is enabled for maximization
        self.root.resizable(True, True)
        self.root.update_idletasks()  # Final update to ensure changes are applied
    
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
