from qtpy.QtWidgets import QProgressBar
from qtpy.QtGui import QIcon

from .utilities.table_handler import TableHandler
from . import MICRO, LAMBDA, ANGSTROMS
from . import combine_image, bin_image, auto_image, manual_image


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.statusbar()
        self.splitter()
        self.table()
        self.labels()
        self.tab()

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

    def splitter(self):
        self.parent.ui.combine_horizontal_splitter.setSizes([200, 500])
        self.parent.ui.bin_horizontal_splitter.setSizes([50, 800])

    def table(self):
        # bin manual table
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        column_sizes = [50, 60, 60]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def labels(self):
        self.parent.ui.combine_detector_offset_units.setText(MICRO + "s")
        self.parent.ui.bin_tof_radioButton.setText("TOF (" + MICRO + "s)")
        self.parent.ui.bin_lambda_radioButton.setText(LAMBDA + " (" + ANGSTROMS + ")")

    def tab(self):
        self.parent.ui.combine_bin_tabWidget.setTabIcon(0, QIcon(combine_image))
        self.parent.ui.combine_bin_tabWidget.setTabIcon(1, QIcon(bin_image))
        self.parent.ui.bin_tabWidget.setTabIcon(0, QIcon(auto_image))
        self.parent.ui.bin_tabWidget.setTabIcon(1, QIcon(manual_image))
