import numpy as np
import pyqtgraph as pg

from ..utilities import CombineAlgorithm
from ..session import SessionKeys
from ..utilities.get import Get


class Combine:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        combine_algorithm = self.parent.session[SessionKeys.combine_algorithm]

        # get list of data to combine
        o_get = Get(parent=self.parent)
        list_array_to_combine = o_get.list_array_to_combine()
        if list_array_to_combine == []:
            self.parent.combine_image_view.clear()
        else:
            # combine using algorithm defined
            if combine_algorithm == CombineAlgorithm.mean:
                combine_arrays = np.mean(list_array_to_combine, axis=0)
            elif combine_algorithm == CombineAlgorithm.median:
                combine_arrays = np.median(list_array_to_combine, axis=0)
            else:
                raise NotImplementedError("Algorithm not implemented!")

            integrated_arrays = np.mean(combine_arrays, axis=0)
            integrated_arrays = np.transpose(integrated_arrays)
            # display integrated
            self.parent.combine_image_view.setImage(integrated_arrays)

        # initialize ROI if first time, otherwise use same region
        [x0, y0, width, height] = self.parent.session[SessionKeys.combine_roi]
        if self.parent.combine_roi_item_id:
            self.parent.combine_image_view.removeItem(self.parent.combine_roi_item_id)

        roi_item = pg.ROI([x0, y0],
                          [width, height])
        roi_item.addScaleHandle([1, 1], [0, 0])
        self.parent.combine_image_view.addItem(roi_item)
        roi_item.sigRegionChanged.connect(self.parent.combine_roi_changed)
