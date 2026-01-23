import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt


# globalne uchwyty do okien
_portfolio_fig = None
_portfolio_ax = None
_portfolio_line = None

_stock_figs = {}   # {stock_name: (fig, ax, line)}


def plot_portfolio(portfolio, simulator):
    global _portfolio_fig, _portfolio_ax, _portfolio_line

    if not portfolio.history or simulator.current_date is None:
        return

    dates = []
    values = []

    for d, v in portfolio.history:
        if d <= simulator.current_date:
            dates.append(d)
            values.append(v)

    # jeśli okno nie istnieje – tworzymy je raz
    if _portfolio_fig is None:
        _portfolio_fig, _portfolio_ax = plt.subplots(figsize=(8, 4))
        _portfolio_line, = _portfolio_ax.plot(dates, values)
        _portfolio_ax.set_title("Wartość portfela")
        _portfolio_ax.set_xlabel("Data")
        _portfolio_ax.set_ylabel("Wartość [zł]")
        _portfolio_fig.show()
    else:
        # tylko aktualizacja danych
        _portfolio_line.set_data(dates, values)
        _portfolio_ax.relim()
        _portfolio_ax.autoscale_view()

    _portfolio_fig.canvas.draw_idle()
    _portfolio_fig.canvas.flush_events()


def plot_stock(position, simulator):
    global _stock_figs

    if position.first_buy_date is None or simulator.current_date is None:
        return

    stock = position.stock
    start = position.first_buy_date
    end = simulator.current_date

    data = stock.data[
        (stock.data["date"] >= start) &
        (stock.data["date"] <= end)
    ]

    if data.empty:
        return

    dates = data["date"]
    prices = data["close"]

    # jeśli dla tej spółki nie ma jeszcze okna – tworzymy
    if stock.name not in _stock_figs:
        fig, ax = plt.subplots(figsize=(8, 4))
        line, = ax.plot(dates, prices)
        ax.set_title(f"{stock.name}")
        ax.set_xlabel("Data")
        ax.set_ylabel("Cena [zł]")
        fig.show()
        _stock_figs[stock.name] = (fig, ax, line)
    else:
        fig, ax, line = _stock_figs[stock.name]
        line.set_data(dates, prices)
        ax.relim()
        ax.autoscale_view()

    fig.canvas.draw_idle()
    fig.canvas.flush_events()
