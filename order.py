
class Order:

    # 投资备注, 报单类型, 报价方式, 报单价格, 证券代码, 下单总量, 策略名称, 指令号, 投资组合
    def __init__(self, invest_message: str, order_type: int, bid_type: str, order_price: float, ticker: str,
                 order_volume: int, strategy_name: str, command_num=None, invest_combination_name=None):
        self.invest_message = invest_message
        self.order_type = order_type
        self.bid_type = bid_type
        self.order_price = order_price
        self.ticker = ticker
        self.order_volume = order_volume
        self.strategy_name = strategy_name
        self.command_num = command_num
        self.invest_combination_name = invest_combination_name

    def to_string(self):
        attr = vars(self)
        return ','.join('' if v is None else str(v) for v in attr.values())

    def save_txt(self, path):
        content = self.to_string()
        with open(path, 'w') as file:
            file.write(content)
        print(f'order has been saved to {path}')
