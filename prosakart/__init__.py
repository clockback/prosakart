"""
Tests Georgian vocabulary.
"""

# Import builtins.

# Import local files.
from . sql_handle import SQLHandler
from . interfaces import MainWidget

__version__ = '0.1.0.2'

# Runs the application.
handler: SQLHandler = SQLHandler()
widget: MainWidget = MainWidget(handler)
widget.top.mainloop()
handler.close()
