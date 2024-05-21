class OrderArgs:
    # 投资备注
    invest_message = {
        1: 'message1'
    }
    # 报单类型
    order_types = {
        'security_buy_in': 23,  # 证券买入
        'security_sell_out': 24,  # 证券卖出

        'long': 27,  # 融资买入
        'short': 28,  # 融券卖出

        'buy_security_payback_security': 29,  # 买券还券
        'directly_payback_security': 30,  # 直接还券

        'buy_security_payback_money': 31,  # 买券还款
        'directly_payback_money': 32,  # 直接还款
    }
    # 报价方式
    bid_types = {
        'latest': '1',  # 最新价
        'specified': '3',  # 指定价
        'sci_tech_after_hours_price': '6',  # 科创盘后定价

        'best_five_immediate_or_cancel_SH': 'M1',  # 最优五档即成剩撤(SH)
        'best_five_immediate_or_trans_SH': 'M2',  # 最优五档即成剩转(SH)

        'immediate_or_cancel_SZ': 'M3',  # 即时成交剩余撤销委托(SZ)
        'fill_or_kill_SZ': 'M4',  # 全额成交或撤(SZ)
        'best_bid_price_SZ': 'M5',  # 本方最优价(SZ)
        'best_ask_price_SZ': 'M6',  # 对手最优价(SZ)
        'best_five_immediate_or_cancel_SZ': 'M7',  # 最优五档即时成交剩余撤销委托(SZ)
    }
