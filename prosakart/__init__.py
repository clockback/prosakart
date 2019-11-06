"""
Tests Georgian vocabulary.
"""

# Import builtins.

# Import local files.
from . sql_handle import SQLHandler
from . interfaces import MainWidget


# Runs the application.
handler: SQLHandler = SQLHandler()
widget: MainWidget = MainWidget(handler)
widget.top.mainloop()
handler.close()
