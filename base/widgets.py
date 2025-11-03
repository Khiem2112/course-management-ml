from PyQt6.QtWidgets import QFrame, QApplication
from PyQt6.QtCore import pyqtSignal, Qt

class ClickableFrame(QFrame):
    """
    A custom QFrame that emits a 'clicked' signal when pressed.
    """
    # Define the signal
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Optional: Set the cursor to a hand to show it's clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """This event is triggered when the frame is clicked."""
        # Emit the signal
        self.clicked.emit()
        # Call the base class's event to ensure proper handling
        super().mousePressEvent(event)