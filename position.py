import os
from datetime import datetime
import pandas as pd
from trade_args import TradeArgs


class Position:

    # PATH = 'D:/trading_mid_file'
    PATH = os.getcwd()

    def __init__(self, account_info: list):
        self.account_info = account_info

        self.stock_capital_num = (
            next((tup[0] for tup in self.account_info if tup[1] == TradeArgs.account_types.get('stock')), None))
        self.future_capital_num = (
            next((tup[0] for tup in self.account_info if tup[1] == TradeArgs.account_types.get('future')), None))
        self.option_capital_num = (
            next((tup[0] for tup in self.account_info if tup[1] == TradeArgs.account_types.get('option')), None))

        self.position_time = datetime.now()

        self.stock_position_data: dict = {}
        self.stock_available_asset: dict = {}

        self.future_position_data: dict = {}
        self.future_available_asset: dict = {}

        # init reading
        self.__read_position_file()
        self.__read_asset_file()

    def __get_position_filename(self, capital_num, capital_type) -> str:
        position_init_str = 'position'
        time_str = self.position_time.strftime('%Y%m%d')
        return f'{position_init_str}.{capital_num}_{capital_type}.{time_str}.csv'

    def __read_asset_file(self):
        for account in self.account_info:
            capital_num = account[0]
            capital_type = account[1]
            asset_info = self.__read_available_asset(capital_num, capital_type)
            column_rename = ['total_asset', 'available_asset']
            if capital_type == 1:
                info = asset_info.loc[0, ['动态权益', '可用资金']]
                info.index = column_rename
                info_dict = info.to_dict()
                self.future_available_asset.update({(capital_num, capital_type): info_dict})
            elif capital_type == 2:
                info = asset_info.loc[0, ['总资产', '可用资金']]
                info.index = column_rename
                info_dict = info.to_dict()
                self.stock_available_asset.update({(capital_num, capital_type): info_dict})

    def __read_available_asset(self, capital_num, capital_type) -> pd.DataFrame:
        asset_filename = self.__get_position_filename(capital_num, capital_type).replace('position', 'asset')
        path = os.path.join(Position.PATH, asset_filename)
        df = pd.read_csv(path, encoding='GBK')
        return df

    def __read_position_file(self):
        for account in self.account_info:
            capital_num = account[0]
            capital_type = account[1]

            read_position_choices = {
                1: self.__read_future_position_file,
                2: self.__read_stock_position_file
            }

            read_position = read_position_choices[capital_type]
            read_position(capital_num, capital_type)

    def __read_stock_position_file(self, capital_num, capital_type):
        position_filename = self.__get_position_filename(capital_num, capital_type)
        path = os.path.join(Position.PATH, position_filename)
        df = pd.read_csv(path, encoding='GBK')
        # rename: [证券代码, 市场名称, 持仓数量, 可用数量, 在途股份, 卖出冻结, 成本价, 最新价, 昨夜拥股, 盈亏, 市值]
        columns_e = [
            'ticker',
            'market',
            'holding',
            'available',
            'in_transit',
            'sell_frozen',
            'cost_price',
            'latest_price',
            'yest_holding',
            'profit_loss',
            'market_value'
        ]
        df.columns = columns_e
        df['ticker'] = df['ticker'].astype(str)
        df['ticker'] = df['market'] + df['ticker']
        useful_columns = ['holding', 'available']
        df.set_index(df.columns[0], inplace=True)
        df = df[useful_columns]
        df_dict = df.to_dict(orient='index')
        self.stock_position_data.update(df_dict)

    def __read_future_position_file(self, capital_num, capital_type):
        position_filename = self.__get_position_filename(capital_num, capital_type)
        path = os.path.join(Position.PATH, position_filename)
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
        df['trading'].replace(48, 1, inplace=True)
        df['trading'].replace(49, -1, inplace=True)
        df['adj_holding'] = df['trading'] * df['holding']
        grouped = df.groupby('contract_code')
        net_holding = grouped['adj_holding'].sum()
        df_dict = net_holding.to_dict()
        self.future_position_data.update(df_dict)
