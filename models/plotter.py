import matplotlib.pyplot as plt


def plot_portfolio(portfolio, simulator):
    """
    Wykres wartości portfela od pierwszej transakcji
    do aktualnej daty symulacji.
    """
    if not portfolio.history or simulator.current_date is None:
        return

    dates = []
    values = []

    for d, v in portfolio.history:
        if d <= simulator.current_date:
            dates.append(d)
            values.append(v)

    plt.figure("Portfel")
    plt.clf()
    plt.plot(dates, values)
    plt.title("Wartość portfela (symulacja)")
    plt.xlabel("Data")
    plt.ylabel("Wartość [zł]")
    plt.tight_layout()
    plt.show(block=False)


def plot_stock(position, simulator):
    """
    Wykres ceny jednej spółki:
    od pierwszego zakupu do aktualnej daty symulacji.
    """
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

    plt.figure(f"Spółka: {stock.name}")
    plt.clf()
    plt.plot(dates, prices)
    plt.title(f"{stock.name} (od zakupu do dnia symulacji)")
    plt.xlabel("Data")
    plt.ylabel("Cena [zł]")
    plt.tight_layout()
    plt.show(block=False)
