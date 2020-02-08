import sys
from contextlib import contextmanager
from enum import Enum
from typing import Any, Callable, Dict, NamedTuple, Sequence, Type

from qtpy.QtCore import Signal, SignalInstance
from qtpy.QtWidgets import (
    QAbstractButton,
    QAbstractSlider,
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


@contextmanager
def event_loop():
    """Start a Qt event loop in which to run the application."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield
    app.exec_()


WidgetType = QWidget
ButtonType = QPushButton
SignalType = Signal


class GetSetOnChange(NamedTuple):
    getter: Callable[[], Any]
    setter: Callable[[Any], None]
    onchange: SignalInstance


def type2widget(type_: type) -> Type[WidgetType]:
    simple: Dict[type, Type[WidgetType]] = {
        bool: QCheckBox,
        int: QSpinBox,
        float: QDoubleSpinBox,
        str: QLineEdit,
        type(None): QLineEdit,
    }
    if type_ in simple:
        return simple[type_]
    elif issubclass(type_, Enum):
        return QComboBox


class Layout(Enum):
    vertical = QVBoxLayout
    horizontal = QHBoxLayout
    grid = QGridLayout
    form = QFormLayout

    @classmethod
    def _missing_(cls, value: object) -> Any:
        options = cls._member_names_
        raise ValueError(f"'{value}' is not a valid Layout. Options include: {options}")


def getter_setter_onchange(widget: WidgetType) -> GetSetOnChange:
    if isinstance(widget, QComboBox):
        return GetSetOnChange(
            widget.currentText,
            lambda x: widget.setCurrentText(
                str(x.name) if isinstance(x, Enum) else str(x)
            ),
            widget.currentTextChanged,
        )
    elif isinstance(widget, QStatusBar):
        return GetSetOnChange(
            widget.currentMessage, widget.showMessage, widget.messageChanged
        )
    elif isinstance(widget, QLineEdit):
        return GetSetOnChange(widget.text, widget.setText, widget.textChanged)
    elif isinstance(widget, (QAbstractButton, QGroupBox)):
        return GetSetOnChange(widget.isChecked, widget.setChecked, widget.toggled)
    elif isinstance(widget, QDateTimeEdit):
        return GetSetOnChange(
            widget.dateTime, widget.setDateTime, widget.dateTimeChanged
        )
    elif isinstance(widget, (QAbstractSpinBox, QAbstractSlider)):
        return GetSetOnChange(widget.value, widget.setValue, widget.valueChanged)
    elif isinstance(widget, QTabWidget):
        return GetSetOnChange(
            widget.currentIndex, widget.setCurrentIndex, widget.currentChanged
        )
    elif isinstance(widget, QSplitter):
        return GetSetOnChange(widget.sizes, widget.setSizes, widget.splitterMoved)
    raise ValueError(f"Unrecognized widget Type: {widget}")


def set_combo_choices(widget: WidgetType, choices: Sequence):
    widget.addItems(map(str, choices))
