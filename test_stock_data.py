import unittest
from stock_data import StockData
from datetime import timedelta
from datetime import datetime


class TestStockData(unittest.TestCase):

    def setUp(self):
        last_trading_day = datetime.today() - timedelta(days=1)
        # if Sunday, shift back to Friday
        if last_trading_day.weekday() == 6:
            last_trading_day = last_trading_day - timedelta(days=2)

        StockDataArgs = {
            'stock_code': '510050',
            'start_date': last_trading_day.strftime('%Y%m%d'),
            'klt': 5,
        }

        self.stock_data = StockData(**StockDataArgs)

    def test_get_today_data(self):
        self.stock_data.get_today_data()
        self.assertTrue(not self.stock_data.today_data.empty)

    def test_get_prev_data(self):
        self.stock_data.get_prev_data()
        self.assertTrue(not self.stock_data.prev_data.empty)

    def test_combine_data(self):
        self.stock_data()
        self.assertEqual(len(self.stock_data.total_data), len(self.stock_data.prev_data)+len(self.stock_data.today_data))