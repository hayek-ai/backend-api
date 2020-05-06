import datetime
from typing import List
from sqlalchemy import or_, and_, func

from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.idea import IdeaModel


class IdeaService:
    def save_new_idea(self, analyst_id: int, symbol: str, position_type: str,
                      price_target: float, company_name: str, market_cap: int,
                      sector: str, entry_price: float, last_price: float,
                      thesis_summary: str, full_report: str, exhibits=None):
        new_idea = IdeaModel(
            analyst_id=analyst_id,
            symbol=symbol,
            position_type=position_type,
            price_target=price_target,
            company_name=company_name,
            market_cap=market_cap,
            sector=sector,
            entry_price=entry_price,
            last_price=last_price,
            thesis_summary=thesis_summary,
            full_report=full_report,
            exhibits=exhibits
        )
        self.save_changes(new_idea)
        return new_idea

    @classmethod
    def get_idea_by_id(cls, idea_id: int) -> "IdeaModel":
        return IdeaModel.query.filter_by(id=idea_id).first()

    @classmethod
    def query_ideas(cls, analyst_ids=[], query_string={}, page=0, page_size=None) -> List["IdeaModel"]:
        """
        Returns list of ideas filtered by query_string for given list of analysts (analyst_ids)

        If no analyst ids are specified, it returns ideas from all analysts
        If no query_string is specified, no filters are applied
        """
        analyst_filter = []
        for analyst_id in analyst_ids:
            analyst_filter.append(IdeaModel.analyst_id == analyst_id)

        symbol_filter = []
        if "symbol" in query_string:
            symbol_filter.append(func.lower(IdeaModel.symbol) == query_string["symbol"].lower())

        position_type_filter = [] # all is default
        if "positionType" in query_string:
            if query_string["positionType"].lower() == "long":
                position_type_filter.append(func.lower(IdeaModel.position_type) == "long")
            if query_string["positionType"].lower() == "short":
                position_type_filter.append(func.lower(IdeaModel.position_type) == "short")

        time_period_filter = [] # all is default
        try:
            time_period = float(query_string["timePeriod"])
            date = datetime.datetime.now() - datetime.timedelta(days=time_period)
            time_period_filter.append(IdeaModel.created_at >= date)
        except Exception as e:
            print(e)

        sector_filter = []
        if "sector" in query_string:
            sector_list = query_string.getlist('sector')
            if len(sector_list) > 0:
                for sector in sector_list:
                    sector_filter.append(func.lower(IdeaModel.sector) == sector.lower())

        market_cap_filter = []
        if "marketCap" in query_string:
            market_cap_list = query_string.getlist("marketCap")
            if len(market_cap_list) > 0 :
                for market_cap in market_cap_list:
                    if market_cap == "mega":
                        market_cap_filter.append(IdeaModel.market_cap >= 200000000000)
                    if market_cap == "large":
                        market_cap_filter.append(IdeaModel.market_cap.between(10000000000, 200000000000))
                    if market_cap == "medium":
                        market_cap_filter.append(IdeaModel.market_cap.between(2000000000, 10000000000))
                    if market_cap == "small":
                        market_cap_filter.append(IdeaModel.market_cap.between(300000000, 2000000000))
                    if market_cap == "micro":
                        market_cap_filter.append(IdeaModel.market_cap <= 300000000)

        filters = and_(
            or_(*analyst_filter),
            *symbol_filter,
            *position_type_filter,
            *time_period_filter,
            or_(*sector_filter),
            or_(*market_cap_filter)
        )

        # assume query_string["sort"] == "latest" (as default)
        query = cls.query.join(UserModel).filter(filters).order_by(db.desc(IdeaModel.created_at))

        if "sort" in query_string:
            if query_string["sort"] == "top":
                query = cls.query.join(UserModel).filter(filters).order_by(db.asc(UserModel.analyst_rank))

        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)

        return query.all()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
