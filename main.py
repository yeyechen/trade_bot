import time
from datetime import datetime
from stock_data import StockData
from datetime import timedelta
from order import Order
from trade_args import TradeArgs
from signal_generator import c2c_volatility, correl, signal_generator
import pandas as pd
import numpy as np
import os

if __name__ == '__main__':
    # -------------------------order generation-------------------------
    order_txt_init_str = 'signal'
    capital_number = 2006683
    capital_type = 2
    order_time = datetime.now()
    order_time_str = order_time.strftime('%Y%m%d')
    file_name = f'{order_txt_init_str}.{capital_number}_{capital_type}.{order_time_str}.txt'

    order_from_calc = {
        'invest_message': TradeArgs.invest_message.get(1),
        'order_type': TradeArgs.order_types.get('security_buy_in'),
        'bid_type': TradeArgs.bid_types.get('latest'),
        'order_price': 2.55,
        'ticker': 'SH510050',
        'order_volume': 1000,
        'strategy_name': 'yuan',
    }

    order1 = Order(**order_from_calc)
    # order_path_name = 'D:/trading_mid_file'
    order_path_name = os.getcwd()
    path = os.path.join(order_path_name, file_name)
    order1.to_string()
    order1.save_txt(path)
    print(order1.to_string())

    # -------------------------data retrieve-------------------------
    # 周一节假日修改为timedelta为4
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
    time1 = datetime(today.year, today.month, today.day, 9, 30)
    time2 = datetime(today.year, today.month, today.day, 11, 30)
    time3 = datetime(today.year, today.month, today.day, 13, 00)
    time4 = datetime(today.year, today.month, today.day, 15, 1)
    now = datetime.now()
    time_cond = now <= time4

    # initial print
    stock_data()
    calculating_data = stock_data.total_data
    print('*' * 40)
    print(calculating_data)

    # outside trading time, exit immediately
    if not time_cond:
        exit(0)

    # shift the next data request time to a 5-minute time point, to ensure a 5-minute request cycle
    delay = 2  # microseconds
    time_shift = (klt - datetime.now().minute % klt) * 60 - datetime.now().second + delay
    time.sleep(time_shift)
    while time_cond:
        now = datetime.now()
        # sleep according to the time difference
        if (now > time2) and (now < time3):
            time_diff = time3 - now
            sleep_seconds = time_diff.total_seconds()
            time.sleep(sleep_seconds)
            now = datetime.now()

        stock_data()
        calculating_data = stock_data.total_data
        print('*' * 40)
        print(calculating_data)
        '''
        你的逻辑写在这！！！！！！！！！！！！！！！！！！！！！！！
        ----------------------------------------------------------------------------------------------------------------
        '''

        '''
        1. args input
        '''
        short_term_vol = c2c_volatility(calculating_data, 5, 5)
        mid_term_vol = c2c_volatility(calculating_data, 10, 5)
        long_term_vol = c2c_volatility(calculating_data, 24, 5)
        merge_col = ['date', 'time', 'code']
        append_col = ['shortvol', 'midvol', 'longvol']

        vol_structure = pd.merge(short_term_vol, mid_term_vol, left_on=merge_col,
                                 right_on=merge_col, how='inner')
        vol_structure = pd.merge(vol_structure, long_term_vol, left_on=merge_col,
                                 right_on=merge_col, how='inner')
        # columns_rename = ['date', 'time', 'code', 'shortvol', 'midvol', 'longvol']
        columns_rename = merge_col + append_col
        vol_structure.columns = columns_rename
        vol_structure = pd.merge(calculating_data, vol_structure, left_on=merge_col,
                                 right_on=merge_col)
        vol_structure['shortvol_return'] = [0] + list(
            vol_structure['shortvol'].values[1:] / vol_structure['shortvol'].values[:-1] - 1)
        vol_structure['midvol_return'] = [0] + list(
            vol_structure['midvol'].values[1:] / vol_structure['midvol'].values[:-1] - 1)
        vol_structure['longvol_return'] = [0] + list(
            vol_structure['longvol'].values[1:] / vol_structure['longvol'].values[:-1] - 1)

        vol_structure['shortvol_correl'] = correl(vol_structure[['date', 'time', 'return']],
                                                  vol_structure['shortvol_return'], 7)
        vol_structure['longvol_correl'] = correl(vol_structure[['date', 'time', 'return']],
                                                 vol_structure['longvol_return'], 15)

        vol_structure.loc[:, 'signal'] = vol_structure.apply(signal_generator, threshold=10, axis=1)
        vol_structure.loc[:, 'signal'] = vol_structure.loc[:, 'signal'].apply(lambda x: np.nan if x == 0 else x)
        vol_structure.loc[:, 'signal'] = (vol_structure.loc[:, 'signal'].fillna(method='ffill')).fillna(0)
        # signal = []
        # for i in range(0, vol_structure.shape[0]):
        #     tem_vol_structure = vol_structure.iloc[i]
        #     signal.append(signal_generator(tem_vol_structure, 10))

        signal_new = int(vol_structure['signal'].iloc[-2])
        print(signal_new)

        '''
        ----------------------------------------------------------------------------------------------------------------
        for chen yuan!!!!!!!!!
        '''
        # remove code delay before 15:00
        if not (now.hour >= 15 and now.minute >= 0):
            next_target_time = (now + timedelta(minutes=klt)).replace(second=2, microsecond=0)
            sleep_seconds = (next_target_time - now).total_seconds()
            time.sleep(sleep_seconds)

        now = datetime.now()
        time_cond = (now >= time1) and (now <= time4)
