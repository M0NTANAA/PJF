class Position:
    def __init__(self, stock):
        self.stock = stock
        self.shares = 0
        self.avg_price = 0.0
        self.first_buy_date = None

        # Zlecenia
        self.stop_loss = None
        self.take_profit = None

    def buy(self, shares, price, date):
        if self.first_buy_date is None:
            self.first_buy_date = date

        total = self.shares * self.avg_price + shares * price
        self.shares += shares
        self.avg_price = total / self.shares

    def sell(self, shares):
        if shares > self.shares:
            raise ValueError("Nie masz tylu akcji.")
        self.shares -= shares

    def set_stop_loss(self, price):
        self.stop_loss = price

    def set_take_profit(self, price):
        self.take_profit = price
