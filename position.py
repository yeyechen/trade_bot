import os
from datetime import datetime
import pandas as pd
import numpy as np

from order import Order
from position_constraint_decorators import PositionConstraint
from trade_args import TradeArgs


class StockPosition:

    # PATH = 'D:/trading_mid_file'
    PATH = os.getcwd()

    def __init__(self, capital_number: int, capital_type: int):
        time = datetime.now()  # the moment this position obj is instantiated

        self.capital_number = capital_number
        self.capital_type = capital_type
        self.position_time = time

        self.position_data = self.__read_position_file()

        self.available_asset = self.__read_available_asset()  # 可用资金

    def __get_position_filename(self) -> str:
        position_init_str = 'position'
        time_str = self.position_time.strftime('%Y%m%d')
        return f'{position_init_str}.{self.capital_number}_{self.capital_type}.{time_str}.csv'

    def __read_position_file(self) -> dict:
        position_filename = self.__get_position_filename()
        path = os.path.join(StockPosition.PATH, position_filename)
        df = pd.read_csv(path, encoding='GBK')
        # rename: [证券代码, 市场名称, 持仓数量, 可用数量, 在途股份, 卖出冻结, 成本价, 最新价, 昨夜拥股, 盈亏, 市值]
        columns_e = ['ticker', 'market', 'holding', 'available', 'in_transit', 'sell_frozen',
                     'cost_price', 'latest_price', 'yest_holding', 'profit_loss', 'market_value']
        df.columns = columns_e
        df['ticker'] = df['ticker'].astype(str)
        df.set_index(df.columns[0], inplace=True)
        df_dict = df.to_dict(orient='index')
        return df_dict

    def __read_available_asset(self) -> pd.DataFrame:
        asset_filename = self.__get_position_filename().replace('position', 'asset')
        path = os.path.join(StockPosition.PATH, asset_filename)
        df = pd.read_csv(path, encoding='GBK')
        return df.iloc[0, 1]

    @PositionConstraint.check_availability_long
    def single_ticker_long(self, ticker, order_volume, order_price, price_drift):

        order_args = {
            'invest_message': '',
            'order_type': TradeArgs.order_types.get('security_buy_in'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            'order_price': round(order_price + price_drift, 3),
            'ticker': ticker,
            'order_volume': order_volume,
            'strategy_name': '',
            'capital_number': self.capital_number,
            'capital_type': self.capital_type,
        }

        order = Order(**order_args)
        order.place_order()

    @PositionConstraint.check_availability_short
    def single_ticker_short(self, ticker, order_volume, order_price, price_drift):

        order_args = {
            'invest_message': '',
            'order_type': TradeArgs.order_types.get('security_sell_out'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            'order_price': round(order_price - price_drift, 3),
            'ticker': ticker,
            'order_volume': order_volume,
            'strategy_name': '',
            'capital_number': self.capital_number,
            'capital_type': self.capital_type,
        }

        order = Order(**order_args)
        order.place_order()

    def execute_target_positions(self, targets: dict):
        # ticker_str: SH510050
        # ticker: 510050
        for ticker_str, target_price_tuple in targets.items():
            ticker = ticker_str[2:]
            target_holding = target_price_tuple[0]
            order_price = target_price_tuple[1]
            price_drift = target_price_tuple[2]

            # target ticker is not in previous position, long
            if ticker not in self.position_data:
                self.single_ticker_long(ticker_str, target_holding, order_price, price_drift)
                continue

            ticker_data = self.position_data.get(ticker)
            curr_holding = ticker_data.get('holding')

            target_execute_mark = np.sign(target_holding - curr_holding)
            actions = {
                1: lambda: self.single_ticker_long(ticker_str, target_holding - curr_holding, order_price, price_drift),
                -1: lambda: self.single_ticker_short(ticker_str, curr_holding - target_holding, order_price, price_drift),
                0: lambda: print('target position has been executed')
            }
            action_chose = actions[target_execute_mark]
            action_chose()


class FuturePosition:

    def __init__(self, capital_number: int, capital_type: int):
        time = datetime.now()

        self.capital_number = capital_number
        self.capital_type = capital_type
        self.position_time = time

        self.position_data = self.__read_position_file()

        self.available_asset = self.__read_available_asset()

    def __get_position_filename(self) -> str:
        position_init_str = 'position'
        time_str = self.position_time.strftime('%Y%m%d')
        return f'{position_init_str}.{self.capital_number}_{self.capital_type}.{time_str}.csv'

    def __read_position_file(self):
        position_filename = self.__get_position_filename()
        path = os.path.join(StockPosition.PATH, position_filename)
        df = pd.read_csv(path, encoding='GBK')
        # rename: [合约代码,交易所代码,投保,买卖,成交日期,持仓量,占用保证金,开仓成本,开仓价,平仓量,平仓额,浮动盈亏,持仓成本,昨结算,成交号]
        columns_e = [
            'contract_code',
            'exchange_code',
            'insurance',
            'trading',
            'transaction_date',
            'holding',
            'margin_occupied',
            'open_position_cost',
            'opening_price',
            'closed_volume',
            'closing_amount',
            'profit_and_loss',
            'holding_cost',
            'previous_settlement',
            'transaction_number'
        ]
        df.columns = columns_e
        df.set_index(df.columns[0], inplace=True)
        df_dict = df.to_dict(orient='index')
        return df_dict

    def __read_available_asset(self) -> pd.DataFrame:
        asset_filename = self.__get_position_filename().replace('position', 'asset')
        path = os.path.join(StockPosition.PATH, asset_filename)
        df = pd.read_csv(path, encoding='GBK')
        return df.iloc[0, 2]

    def single_ticker_long(self, ticker, target_holding, order_price, price_drift):
        pass

    def single_ticker_short(self, ticker, target_holding, order_price, price_drift):
        pass

    def execute_target_positions(self, targets: dict):
        pass
