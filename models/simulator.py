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
        if not self.portfolio.positions:
            self.max_date = None
            return

        self.max_date = min(
            pos.stock.data.iloc[-1]["date"]
            for pos in self.portfolio.positions.values()
        )

    def next_day(self):
        if self.current_date is None or self.max_date is None:
            return
        if self.current_date >= self.max_date:
            return

        next_date = self.current_date + timedelta(days=1)

        while next_date.weekday() >= 5:
            next_date += timedelta(days=1)

        self.current_date = next_date
        self.update()

    def update(self):
        total = 0
        to_close = []

        for name, pos in self.portfolio.positions.items():

            # Cena zawsze istnieje (z ostatniej sesji)
            price = pos.stock.get_price_on_date(self.current_date)

            # Jeżeli to NIE jest dzień sesyjny dla tej spółki, nie sprawdzamy SL/TP
            if not pos.stock.has_quote_on_date(self.current_date):
                total += pos.shares * price
                continue

            # Tylko w dniu rzeczywistej sesji sprawdzamy zlecenia

            if pos.stop_loss is not None and price <= pos.stop_loss:
                to_close.append(name)
                continue

            if pos.take_profit is not None and price >= pos.take_profit:
                to_close.append(name)
                continue

            total += pos.shares * price

        for name in to_close:
            del self.portfolio.positions[name]

        self.portfolio.history.append((self.current_date, total))
