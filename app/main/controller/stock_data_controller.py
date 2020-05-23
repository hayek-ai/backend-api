from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, func

from app.main.libs.util import get_error
from app.main.libs.stock import Stock, StockException
from app.main.model.user import UserModel
from app.main.model.idea import IdeaModel
from app.main.schema.user_schema import UserSchema

user_list_schema = UserSchema(many=True, only=("username",))


class StockData(Resource):
    @classmethod
    @jwt_required
    def get(cls, symbol: str):
        """
        Returns price and company info for a given stock symbol
        Optional query parameter: "withChart" boolean (if chart time series data needed)
        """
        query = request.args
        stock_data = {}
        try:
            stock_data.update(Stock.fetch_stock_quote(symbol))
            stock_data.update(Stock.fetch_company_info(symbol))
            if "withChart" in query and query["withChart"].lower() == "true":
                chart_info = Stock.fetch_chart_info(symbol, "1y")
                return {"companyInfo": stock_data, "chartInfo": chart_info}, 200
            else:
                return {**stock_data}, 200
        except StockException as e:
            return get_error(500, str(e))


class SearchAutocomplete(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        """Takes query string and returns lists of matching analysts and stocks"""
        query = request.args['q']
        ideas = IdeaModel.query.filter(
            or_(IdeaModel.company_name.ilike('%'+query+'%'), IdeaModel.symbol.ilike(query+'%'))).all()
        stocks = [{"symbol": idea.symbol, "companyName": idea.company_name} for idea in ideas]
        seen_symbols = set()
        new_list = []
        for stock in stocks:
            if stock["symbol"] not in seen_symbols:
                new_list.append(stock)
                seen_symbols.add(stock["symbol"])
        analysts = UserModel.query.filter_by(is_analyst=True).\
            filter(UserModel.username.ilike(query+'%')).all()
        return {"stocks": new_list, "analysts": user_list_schema.dump(analysts)}, 200
