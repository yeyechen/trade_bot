import unittest
from market_data import MarketData


class TestMarketData(unittest.TestCase):
    """
    This test class is used to test MarketData behaviours.
    """
    def setUp(self):
        self.stock_data = MarketData('510050')
        self.future_data = MarketData('IM2407', is_future=True)

    def test_get_today_data(self):
        self.stock_data.get_today_data()
        self.assertTrue(not self.stock_data.today_data.empty)
        self.future_data.get_today_data()
        self.assertTrue(not self.future_data.today_data.empty)

    def test_get_prev_data(self):
        self.stock_data.get_prev_data()
        self.assertTrue(not self.stock_data.prev_data.empty)
        self.future_data.get_prev_data()
        self.assertTrue(not self.future_data.prev_data.empty)

    def test_combine_data(self):
        self.stock_data()
        self.assertEqual(len(self.stock_data.total_data),
                         len(self.stock_data.prev_data)+len(self.stock_data.today_data))
        self.future_data()
        self.assertEqual(len(self.future_data.total_data),
                         len(self.future_data.prev_data) + len(self.future_data.today_data))