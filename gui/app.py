import os
from datetime import datetime

from PyQt6.QtCore import QDate, QTimer
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QComboBox, QMessageBox,
    QTextEdit, QDateEdit
)

from PJF.models.plotter import plot_portfolio, plot_stock
from PJF.models.portfolio import Portfolio
from PJF.models.simulator import Simulator
from PJF.models.stock import Stock


class GPWSimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulator GPW – Portfel + SL/TP")
        self.resize(650, 650)

        self.stocks = {}
        self.load_stocks()

        self.portfolio = Portfolio()
        self.simulator = Simulator(self.portfolio)

        # TIMER: 10 sekund = 1 sesja
        self.timer = QTimer()
        self.timer.setInterval(10_000)
        self.timer.timeout.connect(self.auto_next_day)

        # ===== WIDGETY =====
        self.company_box = QComboBox()
        self.company_box.addItems(self.stocks.keys())
        self.company_box.currentTextChanged.connect(self.change_stock)

        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Ilość akcji")

        # SL / TP
        self.sl_input = QLineEdit()
        self.sl_input.setPlaceholderText("Stop Loss")

        self.tp_input = QLineEdit()
        self.tp_input.setPlaceholderText("Take Profit")

        self.set_orders_btn = QPushButton("Ustaw SL / TP")
        self.set_orders_btn.clicked.connect(self.set_orders)

        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("yyyy-MM-dd")

        self.buy_btn = QPushButton("Kup")
        self.buy_btn.clicked.connect(self.buy)

        self.sell_btn = QPushButton("Sprzedaj")
        self.sell_btn.clicked.connect(self.sell)

        self.portfolio_view = QTextEdit()
        self.portfolio_view.setReadOnly(True)

        # ===== LAYOUT =====
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Spółka:"))
        layout.addWidget(self.company_box)

        layout.addWidget(QLabel("Ilość akcji:"))
        layout.addWidget(self.shares_input)

        layout.addWidget(QLabel("Stop Loss:"))
        layout.addWidget(self.sl_input)

        layout.addWidget(QLabel("Take Profit:"))
        layout.addWidget(self.tp_input)

        layout.addWidget(self.set_orders_btn)

        layout.addWidget(QLabel("Data sesji:"))
        layout.addWidget(self.date_picker)

        layout.addWidget(self.buy_btn)
        layout.addWidget(self.sell_btn)

        layout.addWidget(QLabel("Portfel:"))
        layout.addWidget(self.portfolio_view)

        self.setLayout(layout)

        self.current_stock = self.stocks[self.company_box.currentText()]
        self.update_date_range()

    # ==========================================================

    def load_stocks(self):
        for f in os.listdir("data"):
            if f.endswith(".csv"):
                name = f.replace(".csv", "").replace("_", " ")
                self.stocks[name] = Stock(name, os.path.join("data", f))

    def change_stock(self, name):
        self.current_stock = self.stocks[name]
        self.update_date_range()
        self.redraw_charts()

    def update_date_range(self):
        first = self.current_stock.data.iloc[0]["date"].date()
        last = self.current_stock.data.iloc[-1]["date"].date()

        if self.simulator.current_date is None:
            self.date_picker.setMinimumDate(QDate(first.year, first.month, first.day))
            self.date_picker.setMaximumDate(QDate(last.year, last.month, last.day))
            self.date_picker.setDate(QDate(first.year, first.month, first.day))
            self.date_picker.setEnabled(True)
        else:
            cd = self.simulator.current_date
            qd = QDate(cd.year, cd.month, cd.day)
            self.date_picker.setMinimumDate(qd)
            self.date_picker.setMaximumDate(qd)
            self.date_picker.setDate(qd)
            self.date_picker.setEnabled(False)

    # ==========================================================

    def redraw_charts(self):
        try:
            plot_portfolio(self.portfolio, self.simulator)

            name = self.current_stock.name
            if name in self.portfolio.positions:
                pos = self.portfolio.positions[name]
                plot_stock(pos, self.simulator)

        except Exception as e:
            QMessageBox.critical(self, "Błąd wykresu", str(e))

    # ==========================================================

    def is_weekend(self, date: datetime):
        return date.weekday() >= 5

    # ==========================================================

    def buy(self):
        try:
            shares = int(self.shares_input.text())
            if shares <= 0:
                raise ValueError("Ilość musi być > 0")

            if self.simulator.current_date is None:
                qd = self.date_picker.date()
                date = datetime(qd.year(), qd.month(), qd.day())
            else:
                date = self.simulator.current_date

            if self.is_weekend(date):
                QMessageBox.warning(self, "GPW zamknięta",
                                    "GPW jest zamknięta (sobota lub niedziela).")
                return

            if not self.current_stock.has_quote_on_date(date):
                QMessageBox.warning(self, "GPW zamknięta",
                                    "Brak notowań tej spółki w tej sesji.")
                return

            price = self.current_stock.get_price_on_date(date)
            self.portfolio.buy(self.current_stock, shares, price, date)

            if self.simulator.current_date is None:
                self.simulator.start(date)
                self.timer.start()
            else:
                self.simulator.recalculate_max_date()

            self.update_date_range()
            self.refresh()
            self.redraw_charts()

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    # ==========================================================

    def sell(self):
        try:
            shares = int(self.shares_input.text())
            self.portfolio.sell(self.current_stock.name, shares)
            self.refresh()
            self.redraw_charts()
        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    # ==========================================================

    def set_orders(self):
        try:
            name = self.current_stock.name
            if name not in self.portfolio.positions:
                QMessageBox.warning(self, "Błąd", "Nie masz tej spółki w portfelu.")
                return

            sl = float(self.sl_input.text()) if self.sl_input.text() else None
            tp = float(self.tp_input.text()) if self.tp_input.text() else None

            self.portfolio.set_sl_tp(name, sl, tp)

            QMessageBox.information(
                self,
                "Zlecenia ustawione",
                f"Ustawiono:\nStop Loss = {sl}\nTake Profit = {tp}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    # ==========================================================

    def auto_next_day(self):
        if self.simulator.current_date is None:
            return

        self.simulator.next_day()

        cd = self.simulator.current_date
        qd = QDate(cd.year, cd.month, cd.day)
        self.date_picker.setDate(qd)

        self.refresh()
        self.redraw_charts()

    # ==========================================================

    def refresh(self):
        text = ""

        total_invested = 0
        total_current_value = 0

        for name, pos in self.portfolio.positions.items():
            price = pos.stock.get_price_on_date(self.simulator.current_date)

            invested = pos.avg_price * pos.shares
            current_value = price * pos.shares

            total_invested += invested
            total_current_value += current_value

            if invested > 0:
                roi = ((current_value - invested) / invested) * 100
            else:
                roi = 0.0

            # Kolor dla pojedynczej pozycji
            if roi > 0:
                roi_text = f'<span style="color: #00ff00;">{roi:.2f} %</span>'
            elif roi < 0:
                roi_text = f'<span style="color: #ff4040;">{roi:.2f} %</span>'
            else:
                roi_text = f'<span style="color: #cccccc;">{roi:.2f} %</span>'

            text += (
                f"<b>{name}</b><br>"
                f"Akcje: {pos.shares}<br>"
                f"Śr. cena zakupu: {pos.avg_price:.2f}<br>"
                f"SL: {pos.stop_loss}<br>"
                f"TP: {pos.take_profit}<br>"
                f"Obecna cena: {price:.2f}<br>"
                f"Wartość: {current_value:.2f}<br>"
                f"Zainwestowano: {invested:.2f}<br>"
                f"Stopa zwrotu: {roi_text}<br><br>"
            )

        # ===== STOPA ZWROTU CAŁEGO PORTFELA =====
        if total_invested > 0:
            portfolio_roi = ((total_current_value - total_invested) / total_invested) * 100
        else:
            portfolio_roi = 0.0

        if portfolio_roi > 0:
            portfolio_roi_text = f'<span style="color: #00ff00;">{portfolio_roi:.2f} %</span>'
        elif portfolio_roi < 0:
            portfolio_roi_text = f'<span style="color: #ff4040;">{portfolio_roi:.2f} %</span>'
        else:
            portfolio_roi_text = f'<span style="color: #cccccc;">{portfolio_roi:.2f} %</span>'

        if self.simulator.current_date:
            total_value = self.portfolio.total_value(self.simulator.current_date)
            text += (
                f"<hr>"
                f"Data symulacji: {self.simulator.current_date.date()}<br>"
                f"<b>Wartość portfela: {total_value:.2f} zł</b><br>"
                f"<b>Zainwestowano łącznie: {total_invested:.2f} zł</b><br>"
                f"<b>Stopa zwrotu portfela: {portfolio_roi_text}</b>"
            )

        self.portfolio_view.setHtml(text)
