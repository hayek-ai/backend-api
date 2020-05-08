from app.main.db import db
from app.main.model.idea import IdeaModel
from app.main.model.download import DownloadModel
from sqlalchemy import and_


class DownloadService:
    def save_new_download(self, user_id: int, idea_id: int) -> "DownloadModel":
        download = DownloadModel(idea_id=idea_id, user_id=user_id)
        self.save_changes(download)
        return download

    @classmethod
    def get_download_by_id(cls, download_id: int) -> "DownloadModel":
        return DownloadModel.query.filter_by(id=download_id).first()

    @classmethod
    def get_idea_download_count(cls, idea_id: int, start_date=None, end_date=None) -> int:
        """Returns the number of downloads of an idea for a given time period"""
        filters = [DownloadModel.idea_id == idea_id]
        if start_date:
            filters.append(DownloadModel.created_at > start_date)
        if end_date:
            filters.append(DownloadModel.created_at < end_date)

        return DownloadModel.query.filter(and_(*filters)).count()

    @classmethod
    def get_user_download_count(cls, user_id: int, start_date=None, end_date=None) -> int:
        """Returns the number of times a user has downloaded a report for a given time period"""
        filters = [DownloadModel.user_id == user_id]
        if start_date:
            filters.append(DownloadModel.created_at > start_date)
        if end_date:
            filters.append(DownloadModel.created_at < end_date)

        return DownloadModel.query.filter(and_(*filters)).count()

    @classmethod
    def get_analyst_download_count(cls, analyst_id: int, start_date=None, end_date=None) -> int:
        """
        Returns the number of times an analyst's reports have been downloaded
        across all reports for a given time period
        """
        filters = [IdeaModel.analyst_id == analyst_id]
        if start_date:
            filters.append(DownloadModel.created_at > start_date)
        if end_date:
            filters.append(DownloadModel.created_at < end_date)

        return DownloadModel.query.join(IdeaModel).filter(and_(*filters)).count()

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
