from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QWidget,
)

from .config import get_settings
from .olson import build_fuel_curve_plot, get_fuel_loads

settings = get_settings()


class InputForm(QFormLayout):
    def __init__(self, parent):
        super(InputForm, self).__init__()
        self.parent = parent

        # Initialise UI elements
        self.pre_fuel_load_label = QLabel("Pre-fire fuel load (t/ha):")
        self.pre_fuel_load = QLineEdit()

        self.decay_const_label = QLabel("Decay constant (0-1):")
        self.decay_const = QLineEdit()

        self.fuel_remaining_label = QLabel("Fuel remaining after last fire (0-1):")
        self.fuel_remaining = QLineEdit()

        self.years_since_label = QLabel("Years since last fire:")
        self.years_since = QLineEdit()

        self.calc_button = QPushButton("Calculate")

        self.pre_fuel_load.setText(str(settings.DEFAULT_PRE_FIRE_FUEL_LOAD))
        self.decay_const.setText(str(settings.DEFAULT_DECAY_CONST))
        self.fuel_remaining.setText(str(settings.DEFAULT_FUEL_REMAINING))
        self.years_since.setText(str(settings.DEFAULT_YEARS_SINCE_FIRE))

        # Create event for button click
        self.calc_button.clicked.connect(self.calculate)

        # Add all the elements to the UI
        self.addRow(self.pre_fuel_load_label)
        self.addRow(self.pre_fuel_load)
        self.addRow(self.decay_const_label)
        self.addRow(self.decay_const)
        self.addRow(self.fuel_remaining_label)
        self.addRow(self.fuel_remaining)
        self.addRow(self.years_since_label)
        self.addRow(self.years_since)
        self.addRow(self.calc_button)

    def _show_error_box(self, e: str) -> None:
        QMessageBox.critical(
            self.parent,
            "Error",
            "Could not calculte fuel load as an invalid value was given.\n\n - " + e,
            QMessageBox.Ok,
        )

    def _process_inputs(
        self,
        fuel_ss: str,
        k: str,
        p: str,
        t: str,
    ) -> tuple[Optional[float], Optional[float], Optional[float], Optional[int]]:
        try:
            fuel_ss = float(fuel_ss)
            k = float(k)
            p = float(p)
            t = int(t)

            if fuel_ss <= 0:
                raise ValueError("Pre-fire fuel load must be a positive number.")
            if t <= 0:
                raise ValueError("Time must be a positive integer.")
            if not (0 < k < 1):
                raise ValueError("Decay constant must be between 0 and 1.")
            if not (0 < p < 1):
                raise ValueError("Proportion of remaing fuel must be between 0 and 1.")

            return fuel_ss, k, p, t

        except ValueError as e:
            self._show_error_box(str(e))
            return None, None, None, None

    def calculate(self) -> None:
        fuel_ss = self.pre_fuel_load.text()
        k = self.decay_const.text()
        p = self.fuel_remaining.text()
        t = self.years_since.text()

        fuel_ss, k, p, t = self._process_inputs(fuel_ss, k, p, t)

        if (not fuel_ss) or (not k) or (not p) or (not t):
            return

        fuel_load_df = get_fuel_loads(fuel_ss, k, p, t)
        self.parent.replace_figure(fuel_load_df)


class MainWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        outer_layout = QHBoxLayout()
        left_layout = InputForm(self)

        # Initialise the figure
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        build_fuel_curve_plot(self.ax, pd.DataFrame({"year": [], "fuel_load": []}))
        self.canvas = FigureCanvas(self.fig)

        # Add elements to the app layout
        outer_layout.addLayout(left_layout)
        outer_layout.addWidget(self.canvas)

        # Set the layout for the application
        self.setLayout(outer_layout)

    def replace_figure(self, fuel_load_df: pd.DataFrame) -> None:
        self.fig.clear()

        ax = self.fig.add_subplot(111)

        build_fuel_curve_plot(ax, fuel_load_df)

        # Refresh canvas
        self.canvas.draw()


class MainWindow(QMainWindow):
    """
    This class handles the creation of the main window.
    The creation of the main elements is handled in 'MainWidget'.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Olson fuel load calculator")
        self.setMinimumSize(600, 450)

        central = MainWidget()
        self.setCentralWidget(central)
