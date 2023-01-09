import sys

sys.path.append('.')

import json
import unittest
from common import ExperimentData


class AdaptDesiredParallelismTest(unittest.TestCase):

    experiment_data: ExperimentData

    def __init__(self, methodName):
        super().__init__(methodName)
        self.experiment_data = ExperimentData()

    def test_get_source_operator(self):
        topology = [("BidsSource", "a"), ("AuctionSource", "b"), ("b", "c"), ("a", "c"), ("c", "d"), ("d", "e"), ("c", "f"), ("e", "g"), ("f", "g"), ("h", "i")]
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("BidsSource", topology), ["BidsSource"])
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("AuctionSource", topology), ["AuctionSource"])
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("a", topology), ["BidsSource"])
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("b", topology), ["AuctionSource"])
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("c", topology).sort(), ["AuctionSource", "BidsSource"].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("d", topology).sort(), ["AuctionSource", "BidsSource"].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("e", topology).sort(), ["AuctionSource", "BidsSource"].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("f", topology).sort(), ["AuctionSource", "BidsSource"].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("g", topology).sort(), ["AuctionSource", "BidsSource"].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("h", topology).sort(), [].sort())
        self.assertEqual(self.experiment_data.gather_source_operators_of_operator("i", topology).sort(), [].sort())


if __name__ == '__main__':
    unittest.main()
