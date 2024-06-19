import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from freezegun import freeze_time
from time_decorator import TimeDecorator
from stock_data import StockData


class TestTimeDecorator(unittest.TestCase):
    @patch('time.sleep', return_value=None)
    @freeze_time(datetime(2000, 10, 31, 9, 0))
    def test_before_trading_hours(self, mock_sleep):
        @TimeDecorator
        def test_func():
            return 'executed'

        result = test_func()
        self.assertEqual(result, 'executed')
        self.assertEqual(mock_sleep.call_count, 2)

        expected_calls = [(1800,), (300,)]
        actual_calls = [call[0] for call in mock_sleep.call_args_list]
        self.assertEqual(expected_calls, actual_calls)

    @patch('time.sleep', return_value=None)
    @freeze_time(datetime(2000, 10, 31, 12, 0))
    def test_during_lunch_break(self, mock_sleep):
        @TimeDecorator
        def test_func():
            return 'executed'

        result = test_func()
        self.assertEqual(result, 'executed')
        self.assertEqual(mock_sleep.call_count, 2)

        expected_calls = [(3600,), (300,)]
        actual_calls = [call[0] for call in mock_sleep.call_args_list]
        self.assertEqual(expected_calls, actual_calls)

    @patch('time.sleep', return_value=None)
    @freeze_time(datetime(2000, 10, 31, 14, 30, 30))
    def test_during_trading_hours(self, mock_sleep):
        @TimeDecorator
        def test_func():
            return 'executed'

        result = test_func()
        self.assertEqual(result, 'executed')

        expected_sleep_seconds = (5 - 30 % 5) * 60 - 30
        mock_sleep.assert_called_once_with(expected_sleep_seconds)

    @patch('time.sleep', return_value=None)
    @freeze_time(datetime(2000, 10, 31, 15, 0, 30))
    def test_after_trading_hours(self, mock_sleep):
        @TimeDecorator
        def test_func():
            return 'executed'

        with self.assertRaises(SystemExit):
            test_func()

        mock_sleep.assert_not_called()

    @patch('time.sleep', return_value=None)
    @freeze_time(datetime(2000, 10, 31, 9, 0, 0))
    def test_all_day(self, mock_sleep):
        @TimeDecorator
        def test_func():
            # sleep simulation according to the implementation in time_decorator
            advance_seconds = sum(call[0][0] for call in mock_sleep.call_args_list if call[0][0] > 1)
            mock_sleep.call_args_list.clear()
            frozen_time.tick(delta=timedelta(seconds=advance_seconds))
            print(str(datetime.now()) + ' data retrieved' + '\n')

        init_time = datetime(2000, 10, 31, 9, 0, 0)
        with freeze_time(init_time) as frozen_time:
            with self.assertRaises(SystemExit):
                while True:
                    test_func()

    def test_realtime(self):
        """
        example code
        """

        today = datetime.today()
        last_trading_day = datetime.today() - timedelta(days=1)
        # if Sunday, shift back to Friday
        if last_trading_day.weekday() == 6:
            last_trading_day = last_trading_day - timedelta(days=2)

        klt = 5
        StockDataArgs = {
            'stock_code': '510050',
            'start_date': last_trading_day.strftime('%Y%m%d'),
            'klt': klt,
        }
        stock_data = StockData(**StockDataArgs)

        @TimeDecorator
        def func(stock):
            stock()
            print('*' * 40)
            print(stock_data.total_data)
            return stock_data.total_data

        while True:
            calculating_data = func(stock_data)
