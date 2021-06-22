from typing import List

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import (
    QFormLayout, QVBoxLayout, QLineEdit, QCheckBox, QWidget, QComboBox, QDoubleSpinBox, QSpinBox, QFrame, QPushButton, QScrollArea, QLayout, )


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class MySpinbox(QSpinBox):
    def __init__(self, parent=None):
        super(MySpinbox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super(MySpinbox, self).wheelEvent(event)
        else:
            event.ignore()


class MyDoubleSpinbox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super(MyDoubleSpinbox, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super(MyDoubleSpinbox, self).wheelEvent(event)
        else:
            event.ignore()


class MyComboBox(QComboBox):
    clicked = pyqtSignal()

    def showPopup(self):
        self.clicked.emit()
        super(MyComboBox, self).showPopup()

    def wheelEvent(self, event: QWheelEvent) -> None:
        if self.hasFocus():
            super(MyComboBox, self).wheelEvent(event)
        else:
            event.ignore()


def create_pushbutton(text, color="", tooltip="") -> QPushButton:
    btn = QPushButton(text)
    btn.setStyleSheet(f"background-color: {color}; font-weight: bold; font-family: Microsoft YaHei")
    btn.setToolTip(tooltip)

    return btn


def create_checkbox(val=False, name="") -> QCheckBox:
    checkbox = QCheckBox(name)

    checkbox.setChecked(val)

    return checkbox


def create_spin_box(value: int, maximum: int = 99999, minimum: int = 0) -> MySpinbox:
    spinbox = MySpinbox()
    spinbox.setMaximum(maximum)
    spinbox.setMinimum(minimum)

    spinbox.setValue(value)

    return spinbox


def create_double_spin_box(value: float, maximum: float = 1.0, minimum: float = 0.0) -> MyDoubleSpinbox:
    spinbox = MyDoubleSpinbox()
    spinbox.setMaximum(maximum)
    spinbox.setMinimum(minimum)

    spinbox.setValue(value)

    return spinbox


def create_combobox(current_val: str, values: List[str] = None) -> MyComboBox:
    combobox = MyComboBox()

    combobox.setFocusPolicy(Qt.StrongFocus)

    if values is not None:
        combobox.addItems(values)
    combobox.setCurrentText(current_val)

    return combobox


def create_lineedit(current_text: str, placeholder_text="") -> QLineEdit:
    lineedit = QLineEdit(current_text)

    lineedit.setPlaceholderText(placeholder_text)

    return lineedit


def add_form_seperator(form_layout: QFormLayout, title: str):
    form_layout.addRow(f"=== {title} ===", QHLine())


def make_scroll_layout(inner_layout: QLayout):
    widget = QWidget()
    widget.setLayout(inner_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(widget)

    scroll_layout = QVBoxLayout()
    scroll_layout.addWidget(scroll)

    return scroll_layout
