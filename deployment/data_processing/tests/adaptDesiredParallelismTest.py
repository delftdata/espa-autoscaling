import sys

sys.path.append('.')

import unittest
from data_processing import DataScraper


class DataScraperTestsTests(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

    def testDataScraper(self):
        data_scraper = DataScraper("", 140)
        data_scraper.fetchDataFromPrometheus("")


if __name__ == '__main__':
    unittest.main()
