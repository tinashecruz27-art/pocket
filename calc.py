"""Simple PySide6 calculator to test that PySide6 is working."""

import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QGridLayout, QVBoxLayout
)


class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 Calculator")
        self.setFixedSize(300, 400)

        # Display
        self.display = QLineEdit("0")
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(60)
        self.display.setStyleSheet("font-size: 28px; padding: 6px;")

        # Buttons: (label, row, column, column span)
        buttons = [
            ("C", 0, 0, 1), ("(", 0, 1, 1), (")", 0, 2, 1), ("/", 0, 3, 1),
            ("7", 1, 0, 1), ("8", 1, 1, 1), ("9", 1, 2, 1), ("*", 1, 3, 1),
            ("4", 2, 0, 1), ("5", 2, 1, 1), ("6", 2, 2, 1), ("-", 2, 3, 1),
            ("1", 3, 0, 1), ("2", 3, 1, 1), ("3", 3, 2, 1), ("+", 3, 3, 1),
            ("0", 4, 0, 2), (".", 4, 2, 1), ("=", 4, 3, 1),
        ]

        grid = QGridLayout()
        for label, row, col, span in buttons:
            button = QPushButton(label)
            button.setFixedHeight(55)
            button.setStyleSheet("font-size: 20px;")
            if label == "=":
                button.setStyleSheet(
                    "font-size: 20px; background-color: #2d7ff9; color: white;"
                )
            button.clicked.connect(lambda checked=False, text=label: self.on_click(text))
            grid.addWidget(button, row, col, 1, span)

        layout = QVBoxLayout(self)
        layout.addWidget(self.display)
        layout.addLayout(grid)

    def on_click(self, text):
        current = self.display.text()

        if text == "C":
            self.display.setText("0")
        elif text == "=":
            try:
                # Only digits, operators, brackets and dots can reach here,
                # because the display is read-only and fed by the buttons.
                result = eval(current)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)
                self.display.setText(str(result))
            except ZeroDivisionError:
                self.display.setText("Cannot divide by 0")
            except Exception:
                self.display.setText("Error")
        else:
            if current in ("0", "Error", "Cannot divide by 0"):
                current = ""
            self.display.setText(current + text)

    def keyPressEvent(self, event):
        """Let the keyboard work too."""
        key = event.text()
        if key in "0123456789+-*/().":
            self.on_click(key)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.on_click("=")
        elif event.key() == Qt.Key_Escape:
            self.on_click("C")
        elif event.key() == Qt.Key_Backspace:
            text = self.display.text()[:-1]
            self.display.setText(text if text else "0")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())