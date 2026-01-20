from datetime import timedelta


class Simulator:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.current_date = None
        self.start_date = None
        self.max_date = None

    def start(self, date):
        self.start_date = date
        self.current_date = date
        self.recalculate_max_date()

    def recalculate_max_date(self):
        """
        Maksymalna możliwa data symulacji = ostatnia sesja
        dostępna dla wszystkich spółek w portfelu.
        """
        if not self.portfolio.positions:
            self.max_date = None
            return

        self.max_date = min(
            pos.stock.data.iloc[-1]["date"]
            for pos in self.portfolio.positions.values()
        )

    def next_day(self):
        if self.current_date is None:
            return

        if self.max_date is None:
            return

        if self.current_date >= self.max_date:
            return  # koniec danych giełdowych

        self.current_date += timedelta(days=1)
        self.update()

    def update(self):
        total = 0
        to_remove = []

        for name, pos in self.portfolio.positions.items():
            try:
                price = pos.stock.get_price_on_date(self.current_date)
            except:
                continue

            # Stop Loss
            if pos.stop_loss is not None and price <= pos.stop_loss:
                to_remove.append(name)
                continue

            # Take Profit
            if pos.take_profit is not None and price >= pos.take_profit:
                to_remove.append(name)
                continue

            total += pos.shares * price

        for name in to_remove:
            del self.portfolio.positions[name]

        self.portfolio.history.append((self.current_date, total))
