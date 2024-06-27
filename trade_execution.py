import numpy as np

from order import Order
from position import Position
from trade_args import TradeArgs


class TradeExecution:

    ETF_SIZE_WEIGHT = 300000
    FUTURE_MULTIPLIER = 300

    def __init__(self, account_obj: Position, trade_info, trade_mode):
        self.account_obj = account_obj
        self.trade_info = trade_info
        self.trade_mode = trade_mode

        self.long_truth_func = None
        self.short_truth_func = None

    def __call__(self, *args, **kwargs):
        self.trade_encoding_mode()
        self.signal_order_execution()

    def single_ticker_long(self, size):
        ticker = self.trade_info.get('ticker')

        order_price = self.trade_info.get('ticker_latest_price')
        price_drift = self.trade_info.get('ticker_drift')
        order_volume = TradeExecution.ETF_SIZE_WEIGHT * size

        order_args = {
            'invest_message': 'stock_long',
            'order_type': TradeArgs.order_types.get('security_buy_in'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            # 'bid_type': TradeArgs.bid_types.get('smart_trade'),
            'order_price': round(order_price + price_drift, 3),
            'ticker': ticker,
            'order_volume': int(order_volume),
            'strategy_name': self.trade_mode,
            'capital_number': self.account_obj.stock_capital_num,
            'capital_type': 2,
        }

        order = Order(**order_args)
        order.place_order()

    def single_ticker_short(self, size):
        ticker = self.trade_info.get('ticker')

        order_price = self.trade_info.get('ticker_latest_price')
        price_drift = self.trade_info.get('ticker_drift')
        order_volume = TradeExecution.ETF_SIZE_WEIGHT * size

        order_args = {
            'invest_message': 'stock_short',
            'order_type': TradeArgs.order_types.get('security_sell_out'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            # 'bid_type': TradeArgs.bid_types.get('smart_trade'),
            'order_price': round(order_price - price_drift, 3),
            'ticker': ticker,
            'order_volume': int(order_volume),
            'strategy_name': self.trade_mode,
            'capital_number': self.account_obj.stock_capital_num,
            'capital_type': 2,
        }

        order = Order(**order_args)
        order.place_order()

    def single_future_long(self, size):
        future_volume_trans = 300000

        ticker = self.trade_info.get('ticker')
        order_price = self.trade_info.get('ticker_latest_price')
        price_drift = self.trade_info.get('ticker_drift')
        order_volume = TradeExecution.ETF_SIZE_WEIGHT * size / future_volume_trans

        order_args = {
            'invest_message': 'future_long',
            'order_type': TradeArgs.order_types.get('future_buy_in'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            'order_price': round(order_price - price_drift, 1),
            'ticker': ticker,
            'order_volume': int(order_volume),
            'strategy_name': self.trade_mode,
            'capital_number': self.account_obj.future_capital_num,
            'capital_type': 1
        }
        order = Order(**order_args)
        order.place_order()

    def single_future_short(self, size):
        future_volume_trans = 300000

        if self.trade_mode != 'ETF_replace':
            ticker = self.trade_info.get('ticker')
            order_price = self.trade_info.get('ticker_latest_price')
            price_drift = self.trade_info.get('ticker_drift')
        else:
            ticker = self.trade_info.get('ticker_pair')
            order_price = self.trade_info.get('pair_latest')
            price_drift = self.trade_info.get('pair_drift')

        order_volume = TradeExecution.ETF_SIZE_WEIGHT * size / future_volume_trans

        order_args = {
            'invest_message': 'future_short',
            'order_type': TradeArgs.order_types.get('future_sell_out'),
            'bid_type': TradeArgs.bid_types.get('specified'),
            'order_price': round(order_price - price_drift, 1),
            'ticker': ticker,
            'order_volume': int(order_volume),
            'strategy_name': self.trade_mode,
            'capital_number': self.account_obj.future_capital_num,
            'capital_type': 1,
        }

        order = Order(**order_args)
        order.place_order()

    def single_option_long(self):
        pass

    def single_option_short(self):
        pass

    def executing_mode_confirm(self, account_info_):
        pass

    def trade_encoding_mode(self):
        mode_info = {
            'single_future_trade': self.single_future_trade,
            'single_security_trade': self.single_security_trade,
            'ETF_replace': self.security_replace_trade,
            'arb_trade': self.arb_trade,
         }

        mode_execution = mode_info[self.trade_mode]
        mode_execution()

    def single_future_trade(self):
        ticker = self.trade_info.get('ticker')
        latest_price = self.trade_info.get('ticker_latest_price')
        ticker_size = self.trade_info.get('ticker_size')

        # add new entry if position data doesn't contain current ticker/ticker_pair
        new_entry = {ticker: 0}
        new_entry.update(self.account_obj.future_position_data)
        self.account_obj.future_position_data = new_entry

        future_asset_available = list(self.account_obj.future_available_asset.values())[0].get('available_asset')
        margin_lower_bound = 0.3 * ticker_size * latest_price * TradeExecution.FUTURE_MULTIPLIER
        if future_asset_available >= margin_lower_bound:
            self.long_truth_func = self.single_future_long
            self.short_truth_func = self.single_future_short
        else:
            print('margin condition not met, cannot trade futures!')
            self.long_truth_func = lambda: print('long operation on futures cannot be executed!')
            self.short_truth_func = lambda: print('short operation on futures cannot be executed!')

    def single_security_trade(self):
        keys = ['ticker', 'ticker_size', 'ticker_type', 'ticker_signal', 'ticker_latest_price', 'ticker_drift',
                'ticker_pair']
        ticker, ticker_size, ticker_type, signal, latest_price, drift \
            = (self.trade_info.get(key) for key in keys)
        stock_trade_volume = ticker_size * TradeExecution.ETF_SIZE_WEIGHT
        stock_asset_available = list(self.account_obj.stock_available_asset.values())[0].get('available_asset')

        # check available asset enough to long
        available_long_ratio = stock_asset_available / (stock_trade_volume * latest_price)
        if available_long_ratio >= 1.02:
            self.long_truth_func = self.single_ticker_long
        else:
            print(f'available asset is not enough to long {ticker}!')
            self.long_truth_func = lambda: print('long operation cannot be executed!')

        # check available asset enough to short
        ticker_available = self.account_obj.stock_position_data.get(ticker).get('available')
        upper_bound = stock_trade_volume * 1.02
        lower_bound = stock_trade_volume * 1
        if lower_bound <= ticker_available <= upper_bound:
            self.short_truth_func = self.single_ticker_short
        else:
            print(f'available asset is not enough to short {ticker}!')
            self.long_truth_func = lambda: print('short operation cannot be executed!')

    def security_replace_trade(self):
        keys = ['ticker', 'ticker_size', 'ticker_type', 'ticker_signal', 'ticker_latest_price', 'ticker_drift',
                'ticker_pair']
        ticker, ticker_size, ticker_type, signal, latest_price, drift, ticker_pair \
            = (self.trade_info.get(key) for key in keys)
        stock_trade_volume = ticker_size * TradeExecution.ETF_SIZE_WEIGHT
        stock_asset_available = list(self.account_obj.stock_available_asset.values())[0].get('available_asset')
        future_asset_available = list(self.account_obj.future_available_asset.values())[0].get('available_asset')

        # add new entry if position data doesn't contain current ticker/ticker_pair
        stock_new_entry = {ticker: {'holding': 0, 'available': 0}}
        stock_new_entry.update(self.account_obj.stock_position_data)
        self.account_obj.stock_position_data = stock_new_entry

        future_new_entry = {ticker_pair: 0}
        future_new_entry.update(self.account_obj.future_position_data)
        self.account_obj.future_position_data = future_new_entry

        # check available asset enough to long
        available_long_ratio = stock_asset_available / (stock_trade_volume * latest_price)
        if available_long_ratio >= 1.02:
            self.long_truth_func = self.single_ticker_long
        else:
            print(f'available asset is not enough to long {ticker}!')
            self.long_truth_func = lambda: print('long operation cannot be executed!')

        # check short logic: if stock not enough to short, trigger future short
        ticker_available = self.account_obj.stock_position_data.get(ticker).get('available')
        upper_bound = stock_trade_volume * 1.02
        lower_bound = stock_trade_volume * 1

        margin_lower_bound = TradeExecution.ETF_SIZE_WEIGHT * ticker_size * latest_price * 0.3
        if lower_bound <= ticker_available <= upper_bound:
            self.short_truth_func = self.single_ticker_short
        elif future_asset_available >= margin_lower_bound:
            self.short_truth_func = self.single_future_short
        else:
            print(f'available asset is not enough to short {ticker_pair}!')
            self.long_truth_func = lambda: print('short operation cannot be executed!')

    def arb_trade(self):
        pass

    def single_future_net(self, current_net):
        ticker = self.trade_info.get('ticker')
        size = self.trade_info.get('ticker_size')
        future_net = self.account_obj.future_position_data.get(ticker)
        net_sum = size * current_net
        net_diff = net_sum - future_net
        return net_diff

    def etf_replace_net(self, current_net):
        ticker = self.trade_info.get('ticker')
        trade_number = self.trade_info.get('ticker_size')
        target_net = current_net * trade_number
        replace_ticker = self.trade_info.get('ticker_pair')

        stock_hold = (self.account_obj.stock_position_data.get(ticker)).get('holding')
        short_net = self.account_obj.future_position_data.get(replace_ticker)
        long_net = (stock_hold / TradeExecution.ETF_SIZE_WEIGHT)
        net_sum = long_net + short_net

        exec_num = round(target_net - net_sum)

        return exec_num

    def single_security_net(self, current_net):
        pass

    def arb_trade_net(self, current_net):
        pass

    def signal_order_execution(self):
        current_signal = self.trade_info.get('ticker_signal')

        net_pos_func = {
            'single_future_trade': self.single_future_net,
            'single_security_trade': self.single_security_net,
            'ETF_replace': self.etf_replace_net,
            'arb_trade': self.arb_trade_net,
        }
        # signal position exist? calculate net position execute or not?
        net_calc = net_pos_func[self.trade_mode](current_signal)
        if net_calc == 0:
            print(f'pos net is {current_signal},no need trade')

        else:
            direction = np.sign(net_calc)
            func_decided = {
                1: self.long_truth_func,
                -1: self.short_truth_func,
            }
            final_exec_func = func_decided[direction]
            final_exec_func(size=abs(net_calc))
