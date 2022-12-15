import sys

sys.path.append('.')

import json
import unittest
from common import ScaleManager, Configurations


class AdaptDesiredParallelismTest(unittest.TestCase):
    config: Configurations

    def __init__(self, methodName):
        super().__init__(methodName)
        self.config = Configurations()

    def test_adaptation(self):
        self.config.AVAILABLE_TASKMANAGERS = 50
        desired_parallelisms = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        scale_manager = ScaleManager(self.config, None)
        d = scale_manager._adaptScalingToExistingResources(desiredParallelisms=desired_parallelisms)
        print(json.dumps(d, indent=4))
        self.assertEqual(sum(d.values()), self.config.AVAILABLE_TASKMANAGERS)

    def __test_scaleOperations_unequalParallelism(self, currentParallelism, desiredParallelism):
            scale_manager = ScaleManager(self.config, None)
            with self.assertRaises(Exception) as context:
                scale_manager.performScaleOperations(currentParallelism, desiredParallelism)
            self.assertTrue("Parallelism keys do not match" in str(context.exception))

    def test_scaleOperations_missing_desired_parallelism(self):
        desiredParallelism = {"source": 10, "filter": 25, "sink": 20}
        currentParallelism = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        self.__test_scaleOperations_unequalParallelism(currentParallelism, desiredParallelism)

    def test_scaleOperations_missing_current_parallelism(self):
        desiredParallelism = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        currentParallelism = {"source": 10, "filter": 25, "map": 20}
        self.__test_scaleOperations_unequalParallelism(currentParallelism, desiredParallelism)

    def test_scaleOperations_misspelled_desired_parallelism(self):
        desiredParallelism = {"source": 10, "filter": 25, "mapa": 20, "sink": 20}
        currentParallelism = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        self.__test_scaleOperations_unequalParallelism(currentParallelism, desiredParallelism)

    def test_scaleOperations_equal_desired_and_current_parallelism(self):
        config: Configurations = Configurations()
        scale_manager = ScaleManager(config, None)
        desiredParallelism = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        currentParallelism = {"source": 10, "filter": 25, "map": 20, "sink": 20}
        try:
            scale_manager.performScaleOperations(currentParallelism, desiredParallelism)
        except Exception as e:
            self.assertFalse("Parallelism keys do not match" in str(e))

    def test_overprovisioning_factor_ensure_configuration_use(self):
        config: Configurations = Configurations()
        config.OVERPROVISIONING_FACTOR = 1.2
        scale_manager = ScaleManager(config, None)
        self.assertEqual(
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(5),
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(5, overprovisioning_factor=1.2)
        )

    def test_overprovisioning_factor_test_calculation(self):
        config: Configurations = Configurations()
        scale_manager = ScaleManager(config, None)
        self.assertEqual(
            100,
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(100, overprovisioning_factor=1)
        )
        self.assertEqual(
            5,
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(4, overprovisioning_factor=1.2)
        )
        self.assertEqual(
            6,
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(5, overprovisioning_factor=1.2)
        )
        self.assertEqual(
            8,
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(6, overprovisioning_factor=1.2)
        )
        self.assertEqual(
            201,
            scale_manager._calculateParallelismIncludingOverprovisioningFactor(100, overprovisioning_factor=2.000001)
        )

    def test_overprovisioning_factor_test_list_change(self):
        config: Configurations = Configurations()
        scale_manager = ScaleManager(config, None)
        desired_parallelisms = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7}
        scale_manager._addOverprovisioningFactorToDesiredParallelism(desired_parallelisms,
                                                                           overprovisioning_factor=1.25)
        expected_desired_parallelisms = {"a": 2, "b": 3, "c": 4, "d": 5, "e": 7, "f": 8, "g": 9}
        self.assertEqual(desired_parallelisms, expected_desired_parallelisms)


if __name__ == '__main__':
    unittest.main()
