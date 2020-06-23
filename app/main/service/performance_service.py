import datetime
from scipy import stats
from functools import reduce
from main.db import db
from main.libs.stock import Stock, StockException
from main.model.user import UserModel
from main.model.idea import IdeaModel


def calc_idea_return(idea: dict) -> float:
    if idea.position_type.lower() == "long":
        return idea.last_price / idea.entry_price - 1
    else:
        return 1 - idea.last_price / idea.entry_price


def calc_holding_period(idea: dict) -> float:
    d0 = idea.created_at.date()
    d1 = idea.closed_date.date() if idea.closed_date else datetime.date.today()
    delta = d1 - d0
    return delta.days


def calc_pt_capture(idea: dict) -> float:
    if idea.position_type.lower() == "long":
        expected_gain = idea.price_target / idea.entry_price - 1
        actual_gain = idea.last_price / idea.entry_price - 1
        if expected_gain <= 0 or actual_gain <= 0:
            return 0
        return min(1, actual_gain / expected_gain)
    else:
        expected_gain = 1 - idea.price_target / idea.entry_price
        actual_gain = 1 - idea.last_price / idea.entry_price
        if expected_gain <= 0 or actual_gain <= 0:
            return 0
        return min(1, actual_gain / expected_gain)


def calc_idea_profitability(idea: dict) -> int:
    if idea.position_type.lower() == "long":
        if idea.last_price / idea.entry_price - 1 > 0:
            return 1
        else:
            return 0
    else:
        if 1 - idea.last_price / idea.entry_price > 0:
            return 1
        else:
            return 0


class PerformanceService:
    def update_performance(self):
        """
        First updates the last_price field for all ideas with null closed_date.
        Then updates performance metrics for all analysts
        """
        # update the last_price field for all ideas with null closed_date.
        ideas = IdeaModel.query.all()
        for idea in ideas:
            if not idea.closed_date:
                idea.last_price = Stock.fetch_stock_quote(idea.symbol)["latestPrice"]
                self.save_changes(idea)

        analysts = UserModel.query.filter(UserModel.num_ideas > 0).all()
        for analyst in analysts:
            ideas_by_analyst = analyst.ideas.all()

            cumulative_return = reduce((lambda x, y: x + y), map(calc_idea_return, ideas_by_analyst))
            analyst.avg_return = cumulative_return / analyst.num_ideas

            total_price_target_capture = reduce((lambda x, y: x + y), map(calc_pt_capture, ideas_by_analyst))
            analyst.avg_price_target_capture = total_price_target_capture / analyst.num_ideas

            successful_total = reduce((lambda x, y: x + y), map(calc_idea_profitability, ideas_by_analyst))
            analyst.success_rate = successful_total / analyst.num_ideas

            cumulative_holding_period = reduce((lambda x, y: x + y), map(calc_holding_period, ideas_by_analyst))
            analyst.avg_holding_period = cumulative_holding_period / analyst.num_ideas

        num_analysts = len(analysts)
        all_avg_returns = [analyst.avg_return for analyst in analysts]
        avg_return_percentiles = stats.rankdata(all_avg_returns, "average") / num_analysts
        all_pt_captures = [analyst.avg_price_target_capture for analyst in analysts]
        avg_price_target_capture_percentiles = stats.rankdata(all_pt_captures, "average") / num_analysts
        all_success_rates = [analyst.success_rate for analyst in analysts]
        success_rate_percentiles = stats.rankdata(all_success_rates, "average") / num_analysts
        all_avg_holding_periods = [analyst.avg_holding_period for analyst in analysts]
        avg_holding_period_percentiles = stats.rankdata(all_avg_holding_periods, "average") / num_analysts
        all_num_ideas = [analyst.num_ideas for analyst in analysts]
        num_ideas_percentiles = stats.rankdata(all_num_ideas, "average") / num_analysts

        for idx, analyst in enumerate(analysts):
            analyst.avg_return_percentile = avg_return_percentiles[idx]
            analyst.avg_price_target_capture_percentile = avg_price_target_capture_percentiles[idx]
            analyst.success_rate_percentile = success_rate_percentiles[idx]
            analyst.avg_holding_period_percentile = avg_holding_period_percentiles[idx]
            analyst.num_ideas_percentile = num_ideas_percentiles[idx]

            # temporary score to keep track of analyst ranking
            analyst.analyst_rank = analyst.avg_return_percentile + 0.5 * analyst.avg_price_target_capture_percentile

        # sort list of analysts by ranking score, update percentile ranking, and save analyst changes
        analysts.sort(key=lambda x: x.analyst_rank, reverse=True)
        all_analyst_ranks = [analyst.analyst_rank for analyst in analysts]
        analyst_rank_percentiles = stats.rankdata(all_analyst_ranks, "average") / num_analysts

        for idx, analyst in enumerate(analysts):
            analyst.analyst_rank = idx + 1
            analyst.analyst_rank_percentile = analyst_rank_percentiles[idx]
            self.save_changes(analyst)

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
