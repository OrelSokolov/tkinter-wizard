# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from .enums import StepStatus


class WizardStep(ABC):
    """
    Abstract class for a wizard step.
    Developers create subclasses of this class for their steps.
    """
    
    def __init__(self, wizard_app):
        self.wizard_app = wizard_app
        self.content_frame = None
        self.status = StepStatus.PENDING
        self.process = None
    
    @abstractmethod
    def create_content(self, content_frame):
        """
        Create step content. Overridden by developer.
        
        Args:
            content_frame: frame to place step widgets in
        """
        pass
    
    @abstractmethod
    def create_process(self):
        """
        Create process for this step. Overridden by developer.
        
        Returns:
            WizardProcess or None if no process needed
        """
        pass
    
    def render(self, content_frame):
        """Render step (called by WizardApp)"""
        self.content_frame = content_frame
        self.create_content(content_frame)
        
        # Create process if it exists
        self.process = self.create_process()
        if self.process:
            # Set root for process if not already set
            if not self.process.root:
                self.process.root = self.wizard_app.root
            # Start process in separate thread
            self.status = StepStatus.RUNNING
            self.process.start()
    
    def _on_process_complete(self, success):
        """Callback called when process completes"""
        if success:
            self.status = StepStatus.SUCCESS
        else:
            self.status = StepStatus.FAILED
        
        # Notify wizard_app of status change
        self.wizard_app.on_step_status_changed(self)
    
    def can_proceed(self):
        """Whether can proceed to next step"""
        # If no process, can proceed immediately
        if not self.process:
            return True
        
        # If process completed successfully, can proceed
        return self.status == StepStatus.SUCCESS
    
    def is_failed(self):
        """Whether step completed with error"""
        return self.status == StepStatus.FAILED

