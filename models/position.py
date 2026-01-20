class Position:
    def __init__(self, stock):
        self.stock = stock
        self.shares = 0
        self.avg_price = 0.0
        self.stop_loss = None
        self.take_profit = None
        self.first_buy_date = None

    def buy(self, shares, price, date):
        if self.first_buy_date is None:
            self.first_buy_date = date

        total_value = self.shares * self.avg_price + shares * price
        self.shares += shares
        self.avg_price = total_value / self.shares

    def sell(self, shares):
        if shares > self.shares:
            raise ValueError("Nie masz tylu akcji.")
        self.shares -= shares
