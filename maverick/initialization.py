from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QWidget
from qtpy.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from .utilities.table_handler import TableHandler
from . import MICRO, LAMBDA, ANGSTROMS, DELTA
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
        self.pyqtgraph()

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
        # combine tab
        self.parent.ui.combine_detector_offset_units.setText(MICRO + "s")
        self.parent.ui.bin_tof_radioButton.setText("TOF (" + MICRO + "s)")
        self.parent.ui.bin_lambda_radioButton.setText(LAMBDA + " (" + ANGSTROMS + ")")
        # bin tab
        self.parent.ui.auto_delta_t_units_label.setText("File index")
        self.parent.ui.bin_auto_delta_t_over_t_radioButton.setText(DELTA + "t/t")
        self.parent.ui.bin_auto_delta_t_radioButton.setText(DELTA + "t")

    def tab(self):
        self.parent.ui.combine_bin_tabWidget.setTabIcon(0, QIcon(combine_image))
        self.parent.ui.combine_bin_tabWidget.setTabIcon(1, QIcon(bin_image))
        self.parent.ui.bin_tabWidget.setTabIcon(0, QIcon(auto_image))
        self.parent.ui.bin_tabWidget.setTabIcon(1, QIcon(manual_image))

    def pyqtgraph(self):
        area = DockArea()
        self.parent.ui.area = area
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("ROI profile", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        combine_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)  # this improve display

        # preview
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.combine_image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_combine_image_preview)
        d1.addWidget(image_view)

        vertical_layout = QVBoxLayout()

        # combine_widget.setLayout(vertical_layout)
        vertical_layout.addWidget(area)
        self.parent.ui.combine_widget.setLayout(vertical_layout)
