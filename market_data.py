import pandas as pd
import efinance as ef
from datetime import datetime
from datetime import timedelta


class MarketData:
    """ This class is used to retrieve market data using the efinance module.
        Currently, this class only supports stocks data and futures data.

    Attributes:
        code: A string representing the stock code, or the future name
        is_future: A boolean indicating if to retrieve futures data or not. If false, retrieve stocks data.
        start_date: An optional string value from which the data starts from. e.g. '20240624'
    """

    def __init__(self, code: str,  is_future=False, start_date=None):
        self.code = self.__get_future_id(code) if is_future else code  # switch to potential future id
        self.is_future = is_future  # boolean indicator for either stock or future data
        self.start_date = start_date  # optional

        self.today_data = None
        self.prev_data = None
        self.total_data = None

        self.klt = 5
        self.columns_i = [0, 1, 2, 4, 10]
        self.columns_c = ['股票名称', '股票代码', '日期', '收盘', '涨跌幅']
        self.columns_e = ['name', 'code', 'datetime', 'close', 'return']

        # function choices depends on future or stock data
        self.data_func_choices = {
            True: ef.futures.get_quote_history,
            False: ef.stock.get_quote_history
        }

    def __call__(self):
        self.get_today_data()
        self.get_prev_data()
        self.combine_data()

    @staticmethod
    def __get_future_id(future_name):
        future_info_base = ef.futures.get_futures_base_info()
        future_target_id = future_info_base[future_info_base['期货名称'] == future_name]['行情ID'].values[0]
        return future_target_id

    @staticmethod
    def __get_last_trading_day():
        # get the last trading day in a normal week, holidays ignored
        last_trading_day = datetime.today() - timedelta(days=1)
        # if Sunday, shift back to Friday
        if last_trading_day.weekday() == 6:
            last_trading_day = last_trading_day - timedelta(days=2)
        last_trading_day = last_trading_day.strftime('%Y%m%d')
        return last_trading_day

    def get_today_data(self):
        today_str = datetime.today().strftime('%Y%m%d')
        data_func = self.data_func_choices[self.is_future]
        today_data = data_func(self.code, beg=today_str, klt=self.klt)
        # filter out unnecessary columns
        today_data = today_data.iloc[:, self.columns_i]
        today_data.columns = self.columns_e
        self.today_data = today_data

    def get_prev_data(self):
        last_trading_day = self.__get_last_trading_day()
        # default behaviour: begin_date is last trading day unless start date is specified
        begin_date = last_trading_day if self.start_date is None else self.start_date
        data_func = self.data_func_choices[self.is_future]
        prev_data = data_func(self.code, beg=begin_date, end=last_trading_day, klt=self.klt)
        # filter out unnecessary columns
        prev_data = prev_data.iloc[:, self.columns_i]
        prev_data.columns = self.columns_e
        self.prev_data = prev_data

    def combine_data(self):
        total_data = pd.concat([self.prev_data, self.today_data], ignore_index=True)

        # separate 'datetime' to 'date' and 'time'
        total_data['datetime'] = pd.to_datetime(total_data['datetime'])
        total_data['date'] = total_data['datetime'].dt.date
        total_data['time'] = total_data['datetime'].dt.time
        total_data = total_data.drop(columns=['datetime'])
        column_reshape = ['date', 'time', 'name', 'code', 'close', 'return']
        total_data = total_data[column_reshape]
        self.total_data = total_data
