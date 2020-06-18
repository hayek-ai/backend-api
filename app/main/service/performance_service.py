import datetime
from functools import reduce
from main.db import db
from main.libs.stock import Stock, StockException
from main.libs.strings import get_text
from main.model.user import UserModel
from main.model.idea import IdeaModel


def calc_idea_return(idea: dict) -> float:
    if idea.position_type.lower() == "long":
        return idea.last_price / idea.entry_price - 1
    else:
        return 1 - idea.last_price / idea.entry_price

def calc_holding_period(idea: dict) -> float:
    d0 = idea.created_at
    d1 = idea.closed_date if idea.closed_date else datetime.date.today()
    delta = d1 - d0
    return delta.days

class PerformanceService:
    def update_performance(self):
        """
        First updates the last_price field for all ideas with null closed_date.
        Then updates performance metrics for all analysts
        """
        # update the last_price field for all ideas with null closed_date.
        ideas = IdeaModel.query.all()
        for idea in ideas:
            idea.last_price = Stock.fetch_stock_quote["latestPrice"]
            self.save_changes(idea)

        # for each analyst, calculate brier_score, average_return, success_rate, avg_holding_period
        # store in list of analyst dicts
        analysts = UserModel.query.filter(UserModel.num_ideas > 0).all()
        for analyst in analysts:
            ideas_by_analyst = analyst.ideas.all()

            cumulative_return = reduce((lambda x, y: calc_idea_return(x) + y), ideas_by_analyst)
            analyst.avg_return = cumulative_return / analyst.num_ideas

            cumulative_holding_period = reduce((lambda x, y: calc_holding_period(x) + y), ideas_by_analyst)
            analyst.avg_holding_period = cumulative_holding_period / analyst.num_ideas





    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
