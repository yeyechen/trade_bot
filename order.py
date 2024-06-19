import os
from datetime import datetime


class Order:

    # 投资备注, 报单类型, 报价方式, 报单价格, 证券代码, 下单总量, 策略名称, 指令号, 投资组合
    def __init__(self, invest_message: str, order_type: int, bid_type: str, order_price: float, ticker: str,
                 order_volume: int, strategy_name: str,
                 order_txt_init: str, capital_number: int, capital_type: int,
                 command_num=None, invest_combination_name=None):

        time = datetime.now()  # the moment this order obj is instantiated

        # order attributes
        self.invest_message = invest_message
        self.order_type = order_type
        self.bid_type = bid_type
        self.order_price = order_price
        self.ticker = ticker
        self.order_volume = order_volume
        self.strategy_name = strategy_name

        # order info attributes
        self.order_txt_init = order_txt_init
        self.capital_number = capital_number
        self.capital_type = capital_type
        self.order_time = time

        # order optional attributes
        self.command_num = command_num
        self.invest_combination_name = invest_combination_name

    def to_string(self):
        attr = vars(self)
        return ','.join('' if v is None else str(v) for v in attr.values())

    def place_order(self, root_path):
        path = os.path.join(root_path, self.get_order_filename())
        content = self.to_string()
        with open(path, 'w') as file:
            file.write(content)
        print(f'order has been saved to {path}')

    def get_order_filename(self):
        order_time_str = self.order_time.strftime('%Y%m%d')
        return f'{self.order_txt_init}.{self.capital_number}_{self.capital_type}.{order_time_str}.txt'
