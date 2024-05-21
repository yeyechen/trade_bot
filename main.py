import time
from datetime import datetime
from stock_data import StockData
from datetime import timedelta
from order_args import OrderArgs
from order import Order
import os

if __name__ == '__main__':
    # -------------------------order generation-------------------------
    order_txt_init_str = 'signal'
    capital_number = 1006105
    capital_type = 2
    order_time = datetime.now()
    date_time_str = order_time.strftime('%Y%m%d')
    file_name = (f'{order_txt_init_str}.{capital_number}_{capital_type}.{date_time_str}_{order_time.hour}'
                 f'{order_time.minute}_{order_time.second}.txt')

    order_from_calc = {
        'invest_message': OrderArgs.invest_message.get(1),
        'order_type': OrderArgs.order_types.get('security_buy_in'),
        'bid_type': OrderArgs.bid_types.get('latest'),
        'order_price': 2.47,
        'ticker': 'SH510050',
        'order_volume': 1000,
        'strategy_name': 'yuan',
        'invest_combination_name': 'hello'
    }

    order1 = Order(**order_from_calc)
    # order_path_name = 'D:/trading_mid_file'
    path = os.path.join(os.getcwd(), file_name)
    order1.to_string()
    order1.save_txt(path)
    print(order1.to_string())

    # -------------------------data retrieve-------------------------
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
    time_cond = True
    time1 = datetime(today.year, today.month, today.day, 9, 30)
    time2 = datetime(today.year, today.month, today.day, 11, 30)
    time3 = datetime(today.year, today.month, today.day, 13, 00)
    time4 = datetime(today.year, today.month, today.day, 15, 1)

    # shift the next data request time to a 5-minute time point, to ensure a 5-minute request cycle
    delay = 2
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
        print('*'*40)
        print(stock_data.total_data)

        # remove code delay
        next_target_time = (now + timedelta(minutes=klt)).replace(second=2, microsecond=0)
        sleep_seconds = (next_target_time - now).total_seconds()
        time.sleep(sleep_seconds)

        now = datetime.now()
        time_cond = (now >= time1) and (now <= time4)
