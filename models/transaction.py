from datetime import datetime

class Transaction:
    def __init__(self, stock_name, shares, price, date, type_):
        self.stock_name = stock_name
        self.shares = shares
        self.price = price
        self.date = date
        self.type = type_  # "BUY" lub "SELL"
