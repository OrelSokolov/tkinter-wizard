# Tkinter Wizard

Library for creating installer wizards based on Tkinter.

## Installation

```bash
pip install tkinter-wizard
```

## Quick Start

```python
import tkinter as tk
from wizard import WizardApp, WizardStep

class MyStep(WizardStep):
    def create_content(self, content_frame):
        # Create step content
        pass
    
    def create_process(self):
        # Return WizardProcess or None
        return None

root = tk.Tk()
wizard = WizardApp(root)

steps = [
    MyStep(wizard),
]

wizard.set_steps(steps)
root.mainloop()
```

## Examples

See `demo/example.py` for a complete usage example.

## License

MIT

