import os

import requests_cache
from requests import get
from app.main.libs.strings import get_text


def to_float(s):
    if s:
        try:
            return float(s)
        except ValueError:
            return 0
    return 0


class StockException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class Stock:
    IEX_API_KEY = os.environ.get("IEX_API_KEY", None)
    IEX_URI = os.environ.get("IEX_URI", None)

    CACHE_SESSION = requests_cache.CachedSession(
            cache_name="stock_cache",
            backend='sqlite',
            allowable_methods='GET',
            allowable_codes=[200],
            expire_after=86_400)

    @classmethod
    def fetch_stock_quote(cls, symbol: str) -> dict:
        if cls.IEX_API_KEY is None or cls.IEX_URI is None:
            raise StockException(get_text("env_fail").format("IEX API Key"))

        response = get(url=f"{cls.IEX_URI}v1/stock/{symbol}/quote?token={cls.IEX_API_KEY}")

        if response.status_code != 200:
            raise StockException(response.content)

        return response.json()

    @classmethod
    def fetch_company_info(cls, symbol: str) -> dict:
        if cls.IEX_API_KEY is None or cls.IEX_URI is None:
            raise StockException(get_text("env_fail").format("IEX API Key"))

        response = cls.CACHE_SESSION.get(url=f"{cls.IEX_URI}v1/stock/{symbol}/company?token={cls.IEX_API_KEY}")

        if response.status_code != 200:
            raise StockException(response.content)

        company_info = response.json()

        # rename sectors
        sector_map = {
            "Electronic Technology": "Technology",
            "Technology Services": "Technology",
            "Distribution Services": "Communication Services",
            "Health Technology": "Health Care",
            "Health Services": "Health Care",
            "Commercial Services": "Industrials",
            "Industrial Services": "Industrials",
            "Transportation": "Industrials",
            "Process Industries": "Consumer Staples",
            "Consumer Non-Durables": "Consumer Staples",
            "Finance": "Financials",
            "Producer Manufacturing": "Industrials",
            "Retail Trade": "Consumer Discretionary",
            "Non-Energy Minerals": "Materials",
            "Utilities": "Utilities",
            "Miscellaneous": "Miscellaneous",
            "Consumer Durables": "Consumer Discretionary",
            "Consumer Services": "Consumer Discretionary",
            "Communications": "Communication Services",
            "Energy Minerals": "Energy",
            "Government": "Miscellaneous"
        }

        # tag_map used for more granularity in labeling some sectors
        # if sector is mislabeled by IEX, use tagMap to fix
        tag_map = {
            "Aerospace & Defense": "Industrials",
            "Real Estate Development": "Real Estate",
            "Real Estate Investment Trusts": "Real Estate"
        }

        if company_info["sector"] in sector_map:
            company_info["sector"] = sector_map[company_info["sector"]]
        for tag in company_info["tags"]:
            if tag in tag_map:
                company_info["sector"] = tag_map[tag]

        return company_info

    @classmethod
    def fetch_chart_info(cls, symbol: str, date: str) -> dict:
        """
        Returns historical price data
        date options: max, 5y, 2y, 1y, ytd, 6m, 3m, 1m, 1mm, 5d, 5dm,
        """
        if cls.IEX_API_KEY is None:
            raise StockException(get_text("env_fail").format("IEX API Key"))

        response = cls.CACHE_SESSION.get(
            url=f"{cls.IEX_URI}v1/stock/{symbol}/chart/{date}?token={cls.IEX_API_KEY}&chartCloseOnly=true")

        if response.status_code != 200:
            raise StockException(response.content)

        return response.json()

    @classmethod
    def fetch_financial_metrics(cls, symbol: str) -> dict:
        """Returns key financial metrics for a given symbol"""
        if cls.IEX_API_KEY is None:
            raise StockException(get_text("env_fail").format("IEX API Key"))

        metrics = {}
        quote_info = get(url=f"{cls.IEX_URI}v1/stock/{symbol}/quote?token={cls.IEX_API_KEY}")
        if quote_info.status_code != 200:
            raise StockException(quote_info.content)
        quote_info = quote_info.json()

        advanced_stats = cls.CACHE_SESSION.get(
            url=f"{cls.IEX_URI}v1/stock/{symbol}/advanced-stats?token={cls.IEX_API_KEY}")

        if advanced_stats.status_code != 200:
            raise StockException(advanced_stats.content)

        advanced_stats = advanced_stats.json()
        ev_to_ebitda = advanced_stats["enterpriseValue"] / advanced_stats["EBITDA"] if advanced_stats[
                                                                                           "EBITDA"] > 0 else "n/a"
        metrics["forwardPE"] = advanced_stats["forwardPERatio"]
        metrics["evToEBITDA"] = ev_to_ebitda
        metrics["priceToSales"] = advanced_stats["priceToSales"]
        metrics["netDebt"] = (to_float(advanced_stats["currentDebt"]) - to_float(advanced_stats["totalCash"])) / 1000000
        metrics["putCallRatio"] = advanced_stats["putCallRatio"]
        metrics["marketCap"] = to_float(quote_info["marketCap"]) / 1000000
        metrics["latestPrice"] = quote_info["latestPrice"]
        metrics["week52High"] = quote_info["week52High"]
        metrics["week52Low"] = quote_info["week52Low"]

        return metrics
