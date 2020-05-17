import io
from app.main.model.idea import IdeaModel
from app.main.model.user import UserModel
from app.main.service.idea_service import IdeaService
from app.main.service.user_service import UserService


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


def get_error(status_code, message, **kwargs):
    return {"errors": [
        {
            "status": status_code,
            "detail": message,
            **kwargs
        }
    ]}, status_code


def create_image_file(filename, content_type):
    file = io.BytesIO(b"abcdef")
    file.filename = filename
    file.content_type = content_type
    return file


def create_idea(analyst_id: int, symbol: str, with_image: bool) -> "IdeaModel":
    idea_service = IdeaService()
    exhibit1 = create_image_file("testexhibit1.png", "image/png")
    exhibit2 = create_image_file("testexhibit2.jpg", "image/jpg")
    exhibit_title_map = {"testexhibit1.png": "Exhibit 1", "testexhibit2.jpg": "Exhibit 2"}

    if symbol.lower() == "aapl":
        if with_image:
            new_idea = idea_service.save_new_idea(
                analyst_id=analyst_id,
                symbol="AAPL",
                position_type="long",
                bull_target=420,
                bull_probability=0.2,
                base_target=400,
                base_probability=0.6,
                bear_target=380,
                bear_probability=0.2,
                entry_price=313.49,
                thesis_summary="Test Thesis Summary",
                full_report="Test Full Report",
                exhibits=[exhibit1, exhibit2],
                exhibit_title_map=exhibit_title_map)
        else:
            new_idea = idea_service.save_new_idea(
                analyst_id=analyst_id,
                symbol="AAPL",
                position_type="long",
                bull_target=420,
                bull_probability=0.2,
                base_target=400,
                base_probability=0.6,
                bear_target=380,
                bear_probability=0.2,
                entry_price=313.49,
                thesis_summary="Test Thesis Summary",
                full_report="Test Full Report")
    if symbol.lower() == "gm":
        if with_image:
            new_idea = idea_service.save_new_idea(
                analyst_id=analyst_id,
                symbol="GM",
                position_type="short",
                bull_target=20,
                bull_probability=0.2,
                base_target=15,
                base_probability=0.6,
                bear_target=10,
                bear_probability=0.2,
                entry_price=23.21,
                thesis_summary="Test Thesis Summary",
                full_report="Test Full Report",
                exhibits=[exhibit1, exhibit2],
                exhibit_title_map=exhibit_title_map)
        else:
            new_idea = idea_service.save_new_idea(
                analyst_id=analyst_id,
                symbol="GM",
                position_type="short",
                bull_target=20,
                bull_probability=0.2,
                base_target=15,
                base_probability=0.6,
                bear_target=10,
                bear_probability=0.2,
                entry_price=23.21,
                thesis_summary="Test Thesis Summary",
                full_report="Test Full Report")
    return new_idea
