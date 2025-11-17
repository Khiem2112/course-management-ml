from PyQt6.QtWidgets import QFrame, QApplication, QVBoxLayout, QLabel
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6 import QtWidgets

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
        
class ClusterPaperWidget(QFrame):
    """
    A custom widget that looks like a 'paper' with a colored tag.
    It supports text wrapping and clicking.
    """
    # Define a custom signal so we can connect it just like a button
    clicked = pyqtSignal()

    def __init__(self, text, color, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # --- 1. CSS Styling ---
        # We use ID selector '#' to apply styles specifically to this frame
        self.setObjectName("ClusterPaper")
        self.setStyleSheet(f"""
            #ClusterPaper {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                border-left: 12px solid {color}; /* The Color Tag */
            }}
            #ClusterPaper:hover {{
                background-color: #fcfcfc;
                border: 1px solid #b0b0b0;
                border-left: 12px solid {color};
            }}
        """)

        # --- 2. Layout & Content ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 10, 12) # Padding around text
        
        # The Label handles the text wrapping
        self.label = QLabel(text)
        self.label.setWordWrap(True) # <--- THIS ENABLES WRAPPING
        self.label.setStyleSheet("border: none; background: transparent; font-weight: bold; font-size: 11pt; color: #333;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        layout.addWidget(self.label)
        
        # Set a fixed height if you want uniformity, or let it grow with text
        # self.setMinimumHeight(70) 
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Preferred, 
            QtWidgets.QSizePolicy.Policy.Minimum
        )

    def mousePressEvent(self, event):
        """Capture mouse click and emit signal."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)