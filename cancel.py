
class Cancel:
    def __init__(self, cancel_type: str, cancel_number: str, market=None):
        self.cancel_type = cancel_type
        self.cancel_target = cancel_number
        self.market = market

        # when using 'cancel_sys', market is mandatory
        if self.cancel_type == 'cancel_sys' and self.market is None:
            raise ValueError('when using "cancel_sys", market is mandatory')

    def to_string(self):
        attr = vars(self)
        return ','.join(str(v) for v in attr.values() if v is not None)

    def save_txt(self, path):
        content = self.to_string()
        with open(path, 'w') as file:
            file.write(content)
        print(f'cancel has been saved to {path}')
