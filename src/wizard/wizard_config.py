# -*- coding: utf-8 -*-
"""
Wizard configuration class
"""


class WizardConfig:
    """Base configuration class for wizard"""
    
    def __init__(self, wizard_name="Wizard", wizard_version="1.0.0", 
                 short_description="", long_description=""):
        """
        Args:
            wizard_name: Name of the wizard
            wizard_version: Version of the wizard
            short_description: Short description of the wizard
            long_description: Long description of the wizard
        """
        self.wizard_name = wizard_name
        self.wizard_version = wizard_version
        self.short_description = short_description
        self.long_description = long_description

