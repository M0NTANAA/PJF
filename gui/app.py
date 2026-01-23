import os
import sys
from datetime import datetime

from PyQt6.QtCore import QDate, QTimer, Qt, QStringListModel
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QComboBox, QMessageBox,
    QTextEdit, QDateEdit, QCompleter
)

from PJF.models.plotter import plot_portfolio, plot_stock
from PJF.models.portfolio import Portfolio
from PJF.models.simulator import Simulator
from PJF.models.stock import Stock


class GPWSimulatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Symulator GPW")
        self.resize(700, 750)

        self.stocks = {}
        self.load_stocks()

        self.portfolio = Portfolio()
        self.simulator = Simulator(self.portfolio)

        # ===== TIMER =====
        self.timer = QTimer()
        self.timer.setInterval(10_000)
        self.timer.timeout.connect(self.auto_next_day)

        self.simulation_speeds = {
            "1x": 10_000,
            "5x": 2_000,
            "10x": 1_000,
            "50x": 200,
        }

        self.speed_1x_btn = QPushButton("1x")
        self.speed_5x_btn = QPushButton("5x")
        self.speed_10x_btn = QPushButton("10x")
        self.speed_50x_btn = QPushButton("50x")

        self.speed_1x_btn.clicked.connect(lambda: self.set_speed("1x"))
        self.speed_5x_btn.clicked.connect(lambda: self.set_speed("5x"))
        self.speed_10x_btn.clicked.connect(lambda: self.set_speed("10x"))
        self.speed_50x_btn.clicked.connect(lambda: self.set_speed("50x"))

        # ===== WIDGETY =====
        self.company_box = QComboBox()
        self.company_box.setEditable(True)


        self.shares_input = QLineEdit()
        self.shares_input.setPlaceholderText("Ilość akcji")

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

        self.company_box.addItems(sorted(self.stocks.keys()))
        self.company_box.currentTextChanged.connect(self.change_stock)

        # ustawiamy pierwszą spółkę ręcznie
        first = next(iter(self.stocks))
        self.company_box.setCurrentText(first)
        self.current_stock = self.stocks[first]
        self.update_date_range()

        # ===== LAYOUT =====
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Prędkość symulacji:"))
        layout.addWidget(self.speed_1x_btn)
        layout.addWidget(self.speed_5x_btn)
        layout.addWidget(self.speed_10x_btn)
        layout.addWidget(self.speed_50x_btn)

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

        # Ustawiamy bieżącą spółkę
        if not self.stocks:
            QMessageBox.critical(self, "Błąd", "Brak danych w folderze data/")
            sys.exit(1)

        first = next(iter(self.stocks))
        self.current_stock = self.stocks[first]
        self.company_box.setCurrentText(first)
        self.update_date_range()

    # ==========================================================

    def load_stocks(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")

        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Nie znaleziono katalogu danych: {data_dir}")

        for f in os.listdir(data_dir):
            if f.endswith(".csv"):
                name = f.replace(".csv", "").replace("_", " ")
                path = os.path.join(data_dir, f)
                self.stocks[name] = Stock(name, path)

    # ==========================================================

    def change_stock(self, name):
        if name not in self.stocks:
            return
        self.current_stock = self.stocks[name]
        self.update_date_range()
        self.redraw_charts()

    # ==========================================================

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
        plot_portfolio(self.portfolio, self.simulator)

        name = self.current_stock.name
        if name in self.portfolio.positions:
            plot_stock(self.portfolio.positions[name], self.simulator)

    # ==========================================================

    def is_weekend(self, date: datetime):
        return date.weekday() >= 5

    # ==========================================================

    def buy(self):
        try:
            shares = int(self.shares_input.text())

            if self.simulator.current_date is None:
                qd = self.date_picker.date()
                date = datetime(qd.year(), qd.month(), qd.day())
            else:
                date = self.simulator.current_date

            if self.is_weekend(date):
                QMessageBox.warning(self, "GPW zamknięta", "Weekend – brak sesji.")
                return

            if not self.current_stock.has_quote_on_date(date):
                QMessageBox.warning(self, "Brak notowań", "Spółka nie była notowana tego dnia.")
                return

            price = self.current_stock.get_price_on_date(date)
            self.portfolio.buy(self.current_stock, shares, price, date)

            if self.simulator.current_date is None:
                self.simulator.start(date)
                self.timer.start()

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
            QMessageBox.information(self, "OK", "Ustawiono SL / TP")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", str(e))

    # ==========================================================

    def auto_next_day(self):
        if self.simulator.current_date is None:
            return

        self.simulator.next_day()
        cd = self.simulator.current_date
        self.date_picker.setDate(QDate(cd.year, cd.month, cd.day))

        self.refresh()
        self.redraw_charts()

    # ==========================================================

    def set_speed(self, speed_key):
        self.timer.setInterval(self.simulation_speeds[speed_key])

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

            roi = ((current_value - invested) / invested) * 100 if invested > 0 else 0

            color = "#00ff00" if roi > 0 else "#ff4040" if roi < 0 else "#cccccc"
            roi_text = f'<span style="color:{color};">{roi:.2f} %</span>'

            text += (
                f"<b>{name}</b><br>"
                f"Akcje: {pos.shares}<br>"
                f"Śr. cena zakupu: {pos.avg_price:.2f}<br>"
                f"Obecna cena: {price:.2f}<br>"
                f"Wartość: {current_value:.2f}<br>"
                f"Zainwestowano: {invested:.2f}<br>"
                f"Stopa zwrotu: {roi_text}<br><br>"
            )

        # ===== PODSUMOWANIE PORTFELA =====
        if total_invested > 0:
            portfolio_roi = ((total_current_value - total_invested) / total_invested) * 100
        else:
            portfolio_roi = 0.0

        if portfolio_roi > 0:
            portfolio_roi_text = f'<span style="color:#00ff00;">{portfolio_roi:.2f} %</span>'
        elif portfolio_roi < 0:
            portfolio_roi_text = f'<span style="color:#ff4040;">{portfolio_roi:.2f} %</span>'
        else:
            portfolio_roi_text = f'<span style="color:#cccccc;">{portfolio_roi:.2f} %</span>'

        if self.simulator.current_date:
            text += (
                "<hr>"
                f"Data symulacji: {self.simulator.current_date.date()}<br>"
                f"<b>Wartość portfela: {total_current_value:.2f} zł</b><br>"
                f"<b>Zainwestowano łącznie: {total_invested:.2f} zł</b><br>"
                f"<b>Stopa zwrotu portfela: {portfolio_roi_text}</b>"
            )

        self.portfolio_view.setHtml(text)

