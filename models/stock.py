import pandas as pd
from datetime import datetime


class Stock:
    def __init__(self, name: str, csv_path: str):
        self.name = name
        self.csv_path = csv_path

        self.data = pd.read_csv(csv_path, sep=";")
        self.data.columns = self.data.columns.str.strip().str.lower()

        self.data.rename(columns={
            "data": "date",
            "zamkniecie": "close"
        }, inplace=True)

        self.data["date"] = pd.to_datetime(self.data["date"])
        self.data.sort_values("date", inplace=True)

    def has_quote_on_date(self, date):
        target = date.date()
        available_dates = self.data["date"].dt.normalize().dt.date
        return target in available_dates.values

    def get_price_on_date(self, date: datetime) -> float:
        target = date.date()
        filtered = self.data[self.data["date"].dt.date <= target]
        if filtered.empty:
            raise ValueError("Brak notowań przed tą datą.")
        return float(filtered.iloc[-1]["close"])

    def get_latest_price(self):
        return float(self.data.iloc[-1]["close"])
