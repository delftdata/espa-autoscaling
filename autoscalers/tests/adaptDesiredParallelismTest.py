import sys
sys.path.append('.')

import json
import unittest
from common import ScaleManager


class AdaptDesiredParallelismTest(unittest.TestCase):
    class TestConfigurations:
        def __init__(self):
            self.MAX_PARALLELISM = 50

    def test_adaptation(self):
        config = self.TestConfigurations()
        desired_parallelisms = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        scale_manager = ScaleManager(config, None)
        d = scale_manager._adaptScalingToExistingResources(desiredParallelisms=desired_parallelisms)
        print(json.dumps(d, indent=4))
        self.assertEqual(sum(d.values()), config.MAX_PARALLELISM)

if __name__ == '__main__':
    unittest.main()
