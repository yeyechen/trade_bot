import pandas as pd
import efinance as ef
from datetime import datetime
from datetime import timedelta


class StockData:

    def __init__(self, stock_code, start_date, klt):
        self.stock_code = stock_code
        self.start_date = start_date
        self.klt = klt
        self.today_data = None
        self.prev_data = None
        self.total_data = None
        self.columns_i = [0, 1, 2, 4, 10]
        self.columns_c = ['股票名称', '股票代码', '日期', '收盘', '涨跌幅']
        self.columns_e = ['name', 'code', 'datetime', 'close', 'return']

    def __call__(self):
        self.get_today_data()
        self.get_prev_data()
        self.combine_data()

    def get_today_data(self):
        today = datetime.today()
        today_str = today.strftime('%Y%m%d')
        today_data = ef.stock.get_quote_history(self.stock_code, beg=today_str, klt=self.klt)
        today_data = today_data.iloc[:, self.columns_i]
        today_data.columns = self.columns_e
        self.today_data = today_data

    def get_prev_data(self):
        # 1. get by csv file
        # 2. get by efinance
        # 3. get by mysql

        # get previous trading day data using efinance
        last_trading_day = datetime.today() - timedelta(days=1)
        # if Sunday, shift back to Friday
        if last_trading_day.weekday() == 6:
            last_trading_day = last_trading_day - timedelta(days=2)
        last_trading_day = last_trading_day.strftime('%Y%m%d')
        prev_data = ef.stock.get_quote_history(self.stock_code, beg=self.start_date, end=last_trading_day, klt=self.klt)
        prev_data = prev_data.iloc[:, self.columns_i]
        prev_data.columns = self.columns_e
        self.prev_data = prev_data

    def combine_data(self):
        total_data = pd.concat([self.prev_data, self.today_data], ignore_index=True)

        # separate 'datetime'
        total_data['datetime'] = pd.to_datetime(total_data['datetime'])
        total_data['date'] = total_data['datetime'].dt.date
        total_data['time'] = total_data['datetime'].dt.time
        total_data = total_data.drop(columns=['datetime'])
        column_reshape = ['date', 'time', 'name', 'code', 'close', 'return']
        total_data = total_data[column_reshape]
        self.total_data = total_data
