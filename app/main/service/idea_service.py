import datetime
import json
from typing import List, TextIO
from sqlalchemy import or_, and_, func

from app.main.libs.s3 import S3
from app.main.libs.stock import Stock, StockException
from app.main.libs.strings import get_text
from app.main.db import db
from app.main.model.user import UserModel
from app.main.model.idea import IdeaModel
from app.main.model.upvote import UpvoteModel
from app.main.model.downvote import DownvoteModel
from app.main.model.bookmark import BookmarkModel
from app.main.model.download import DownloadModel
from app.main.service.user_service import UserService


class IdeaService:
    def save_new_idea(self, analyst_id: int, symbol: str, position_type: str,
                      agreed_to_terms: bool, bull_target: float, bull_probability: float,
                      base_target: float, base_probability: float, bear_target: float,
                      bear_probability: float, entry_price: float, thesis_summary: str,
                      full_report: str, exhibits=[], exhibit_title_map=None):
        analyst = UserService.get_user_by_id(analyst_id)

        price_target = (float(bull_target) * float(bull_probability))\
            + (float(base_target) * float(base_probability))\
            + (float(bear_target) * float(bear_probability))

        stock_data = {}
        try:
            stock_data.update(Stock.fetch_company_info(symbol))
            stock_data.update(Stock.fetch_stock_quote(symbol))
        except StockException as e:
            return {"error": str(e)}

        # make sure the price isn't too far off from what API says before committing
        if abs(float(entry_price) - stock_data["latestPrice"])/stock_data["latestPrice"] > 0.01:
            return {"error": get_text("incorrect_price")}

        exhibit_dict_list = []
        for image_file in exhibits:
            title = exhibit_title_map[image_file.filename]
            image_extension = image_file.filename.split('.')[len(image_file.filename.split(".")) - 1]
            suffix = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
            title_for_url = title.replace(" ", "-")
            filename = f"{analyst.username}-{symbol}-{title_for_url}-{suffix}.{image_extension}"
            response_dict = self.upload_exhibit(title, filename, image_file)
            if "error" in response_dict:
                return {"error": response_dict["error"]}
            exhibit_dict_list.append(response_dict)

        exhibit_dict_list = json.dumps(exhibit_dict_list)

        new_idea = IdeaModel(
            analyst_id=analyst_id,
            symbol=symbol.upper(),
            position_type=position_type.lower(),
            agreed_to_terms=agreed_to_terms,
            price_target=price_target,
            bull_target=bull_target,
            bull_probability=bull_probability,
            base_target=base_target,
            base_probability=base_probability,
            bear_target=bear_target,
            bear_probability=bear_probability,
            company_name=stock_data["companyName"],
            market_cap=stock_data["marketCap"],
            sector=stock_data["sector"].lower(),
            entry_price=entry_price,
            last_price=stock_data["latestPrice"],
            thesis_summary=thesis_summary,
            full_report=full_report,
            exhibits=exhibit_dict_list
        )
        self.save_changes(new_idea)

        # update analyst idea count
        analyst.num_ideas = analyst.num_ideas + 1
        self.save_changes(analyst)
        return new_idea

    @classmethod
    def upload_exhibit(cls, title: str, filename, image: TextIO):
        client = S3.get_client()
        try:
            # upload file to S3 bucket
            client.put_object(
                ACL="public-read",
                Body=image,
                Bucket=S3.S3_BUCKET,
                Key=f"report_exhibits/{filename}",
                ContentType=image.content_type
            )
        except Exception as e:
            return {"error": str(e)}

        exhibit_dict = {
            "url": f"{S3.S3_ENDPOINT_URL}/report_exhibits/{filename}",
            "title": title
        }
        return exhibit_dict

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

        position_type_filter = []  # all is default
        if "positionType" in query_string:
            if query_string["positionType"].lower() == "long":
                position_type_filter.append(func.lower(IdeaModel.position_type) == "long")
            if query_string["positionType"].lower() == "short":
                position_type_filter.append(func.lower(IdeaModel.position_type) == "short")

        time_period_filter = []  # all is default
        if "timePeriod" in query_string:
            time_period = float(query_string["timePeriod"])
            date = datetime.datetime.now() - datetime.timedelta(days=time_period)
            time_period_filter.append(IdeaModel.created_at >= date)

        sector_filter = []
        if "sector" in query_string:
            sector_list = query_string['sector']
            for sector in sector_list:
                sector = sector.strip().lower()
                sector_filter.append(func.lower(IdeaModel.sector) == sector)

        market_cap_filter = []
        if "marketCap" in query_string:
            market_cap_list = query_string["marketCap"]
            for market_cap in market_cap_list:
                market_cap = market_cap.strip().lower()
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
        query = IdeaModel.query.join(UserModel).filter(filters).order_by(db.desc(IdeaModel.created_at))

        if "sort" in query_string:
            if query_string["sort"] == "top":
                query = IdeaModel.query.join(UserModel).filter(filters)\
                    .order_by(db.desc(IdeaModel.score), db.desc(IdeaModel.created_at))

        if page_size:
            query = query.limit(page_size)
        if page:
            query = query.offset(page * page_size)

        return query.all()

    @classmethod
    def get_idea_financial_metrics(cls, symbol) -> dict:
        try:
            return Stock.fetch_financial_metrics(symbol)
        except StockException as e:
            return {"error": str(e)}

    def close_idea_by_id(self, idea_id: int) -> None:
        idea = self.get_idea_by_id(idea_id)
        idea.closed_date = datetime.datetime.utcnow()
        idea.last_price = Stock.fetch_stock_quote(idea.symbol)["latestPrice"]
        self.save_changes(idea)

    def delete_idea_by_id(self, idea_id: int) -> None:
        idea = self.get_idea_by_id(idea_id)
        comments = idea.comments.all()
        for comment in comments:
            self.delete_from_db(comment)
        downloads = DownloadModel.query.filter_by(idea_id=idea.id).all()
        for download in downloads:
            self.delete_from_db(download)
        upvotes = UpvoteModel.query.filter_by(idea_id=idea.id).all()
        for upvote in upvotes:
            self.delete_from_db(upvote)
        downvotes = DownvoteModel.query.filter_by(idea_id=idea.id).all()
        for downvote in downvotes:
            self.delete_from_db(downvote)
        bookmarks = BookmarkModel.query.filter_by(idea_id=idea.id).all()
        for bookmark in bookmarks:
            self.delete_from_db((bookmark))
        analyst = UserModel.query.filter_by(id=idea.analyst_id).first()
        analyst.num_ideas = analyst.num_ideas - 1
        self.save_changes(analyst)
        self.delete_from_db(idea)

    @classmethod
    def delete_from_db(cls, data) -> None:
        db.session.delete(data)
        db.session.commit()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
