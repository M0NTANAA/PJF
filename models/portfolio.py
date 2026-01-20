from PJF.models.position import Position

class Portfolio:
    def __init__(self):
        self.positions = {}   # { "PKN ORLEN": Position }
        self.history = []     # [(date, value)]

    def buy(self, stock, shares, price, date):
        if stock.name not in self.positions:
            self.positions[stock.name] = Position(stock)
        self.positions[stock.name].buy(shares, price, date)

    def sell(self, stock_name, shares):
        self.positions[stock_name].sell(shares)
        if self.positions[stock_name].shares == 0:
            del self.positions[stock_name]

    def set_sl_tp(self, stock_name, stop_loss=None, take_profit=None):
        pos = self.positions[stock_name]
        pos.stop_loss = stop_loss
        pos.take_profit = take_profit

    def total_value(self, date):
        value = 0
        for pos in self.positions.values():
            price = pos.stock.get_price_on_date(date)
            value += pos.shares * price
        return value
