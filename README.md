# Tkinter Wizard

Library for creating general wizards based on Tkinter.

## Installation

### Установка из PyPI

```bash
pip install tkinter-wizard
```

### Установка из исходников

1. Клонируйте репозиторий или скачайте исходный код:
```bash
git clone https://github.com/OrelSokolov/tkinter-wizard.git
cd tkinter-wizard
```

2. Установите проект в режиме разработки:
```bash
pip install -e .
```

Или установите обычным способом:
```bash
pip install .
```

### Требования

- Python >= 3.7
- tkinter (обычно входит в стандартную поставку Python)

### Установка с зависимостями для разработки

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
import tkinter as tk
from wizard import WizardApp, WizardStep, WizardConfig

# Create configuration (optional)
config = WizardConfig(
    wizard_name="My Wizard",
    wizard_version="1.0.0",
    short_description="Setup Wizard",
    long_description="This wizard helps you configure the application."
)

class MyStep(WizardStep):
    def create_content(self, content_frame):
        # Create step content
        pass
    
    def create_process(self):
        # Return WizardProcess or None
        return None

root = tk.Tk()
wizard = WizardApp(root, config=config)

steps = [
    MyStep(wizard),
]

wizard.set_steps(steps)
root.mainloop()
```

## Examples

See `demo/example.py` for a complete usage example.

## License

Apache 2.0

