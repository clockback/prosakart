"""
Tests Georgian vocabulary.
"""

# Import builtins.

# __future__ is needed for specific type hinting (must precede others).
from __future__ import annotations

# Import local files.
from sql_handle import SQLHandler
from interfaces import MainWidget


# Runs the application.
if __name__ == '__main__':
    handler: SQLHandler = SQLHandler()
    widget: MainWidget = MainWidget(handler)
    widget.top.mainloop()
    handler.close()
