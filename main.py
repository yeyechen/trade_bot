import os

from stock_data import StockData
from order import Order
from time_decorator import TimeDecorator
from trade_args import TradeArgs


@TimeDecorator
def request_data(stock_data_obj):
    stock_data_obj()
    print('*' * 40)
    print(stock_data_obj.total_data)
    return stock_data_obj.total_data


if __name__ == '__main__':
    # -------------------------order generation-------------------------
    order_args = {
        'invest_message': TradeArgs.invest_message.get(1),
        'order_type': TradeArgs.order_types.get('security_buy_in'),
        'bid_type': TradeArgs.bid_types.get('latest'),
        'order_price': 2.55,
        'ticker': 'SH510050',
        'order_volume': 1000,
        'strategy_name': 'yuan',
        'order_txt_init': 'signal',
        'capital_number': 2006683,
        'capital_type': 2,
    }

    order1 = Order(**order_args)

    # root_path = 'D:/trading_mid_file'
    root_path = os.getcwd()
    order1.place_order(root_path)

    # -------------------------data retrieve-------------------------

    stock_data = StockData(stock_code='510050')

    while True:

        calculating_data = request_data(stock_data)


