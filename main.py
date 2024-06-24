from market_data import MarketData
from time_decorator import TimeDecorator
from logic_calc import logic_calculator
from position import StockPosition, FuturePosition


@TimeDecorator
def request_data(stock_data_obj):
    stock_data_obj()
    print('*' * 40)
    print(stock_data_obj.total_data)
    return stock_data_obj.total_data


if __name__ == '__main__':

    stock_data = MarketData(code='510050')
    stock_data()
    future_data = MarketData(code='IM2407', is_future=True)
    future_data()

    while True:

        # ------------------------position constraint-----------------------
        stock_position = StockPosition(2006683, 2)
        future_position = FuturePosition(1006107, 1)

        # --------------------------data retrieve---------------------------
        calculating_data = request_data(stock_data)
        latest_price = calculating_data.iloc[-1]['close']

        # -------------------------order generation-------------------------
        signal = logic_calculator(calculating_data)
        future_target_positions = {'IF2407': (1, 5000, 0.4)}
        future_position.execute_target_positions(future_target_positions)

        target_positions = {'SH510050': (500, latest_price, 0.02)}
        stock_position.execute_target_positions(target_positions)
