import numpy as np

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

        # combine using algorithm defined
        if combine_algorithm == CombineAlgorithm.mean:
            combine_arrays = np.mean(list_array_to_combine, axis=0)
        elif combine_algorithm == CombineAlgorithm.median:
            combine_arrays = np.median(list_array_to_combine, axis=0)
        else:
            raise NotImplementedError("Algorithm not implemented!")

        # display integrated

        # initialize ROI if first time, otherwise use same region

        # display profile