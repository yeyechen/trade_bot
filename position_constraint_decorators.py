from functools import wraps


class PositionConstraint:

    @staticmethod
    def long_stock_availability(func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            ticker = kwargs.get('ticker') if 'ticker' in kwargs else args[0]
            order_volume = kwargs.get('order_volume') if 'order_volume' in kwargs else args[1]
            order_price = kwargs.get('order_price') if 'order_price' in kwargs else args[2]

            if instance.available_asset < order_price * 1.05 * order_volume:
                print(
                    f'available asset: {instance.available_asset} in account {instance.acc1_capital_number}_{instance.acc1_capital_type} '
                    f'is not enough to long {order_volume} amount of share of {ticker} at the price {order_price}!')
                return

            return func(instance, *args, **kwargs)

        return wrapper

    @staticmethod
    def short_stock_availability(func):
        @wraps(func)
        def wrapper(instance, *args, **kwargs):
            ticker = kwargs.get('ticker') if 'ticker' in kwargs else args[0]
            order_volume = kwargs.get('order_volume') if 'order_volume' in kwargs else args[1]

            ticker_data = instance.stock_position_data.get(ticker[2:])
            available_holding = ticker_data.get('available')
            # availability checking
            cond = order_volume > available_holding
            conds = {True: f'available holding:{available_holding} in account {instance.acc1_capital_number}_{instance.acc1_capital_type} '
                      f'is not enough to short {order_volume} amount of share of {ticker}!',
                     False: 'continue order'}

            print_truth = conds[cond]

            print(print_truth)

            if cond:
                return

            return func(instance, *args, **kwargs)

        return wrapper

    @staticmethod
    def long_future_availability(func):
        pass

    @staticmethod
    def short_future_availability(func):
        pass
