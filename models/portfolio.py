from PJF.models.position import Position


class Portfolio:
    def __init__(self):
        self.positions = {}
        self.history = []

    def buy(self, stock, shares, price, date):
        if stock.name not in self.positions:
            self.positions[stock.name] = Position(stock)
        self.positions[stock.name].buy(shares, price, date)

    def sell(self, stock_name, shares):
        pos = self.positions[stock_name]
        pos.sell(shares)
        if pos.shares == 0:
            del self.positions[stock_name]

    def set_sl_tp(self, stock_name, sl=None, tp=None):
        pos = self.positions[stock_name]
        pos.stop_loss = sl
        pos.take_profit = tp

    def total_value(self, date):
        value = 0
        for pos in self.positions.values():
            price = pos.stock.get_price_on_date(date)
            value += pos.shares * price
        return value
