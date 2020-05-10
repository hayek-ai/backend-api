import os
from app.main import create_app
from app.main.service.user_service import UserService
from app.main.service.confirmation_service import ConfirmationService
from app.main.service.idea_service import IdeaService
from app.main.service.download_service import DownloadService
from app.main.service.follow_service import FollowService
from app.main.service.review_service import ReviewService
from app.main.service.comment_service import CommentService


def create_services():
    services = {
        "user": UserService(),
        "confirmation": ConfirmationService(),
        "idea": IdeaService(),
        "download": DownloadService(),
        "follow": FollowService(),
        'review': ReviewService(),
        'comment': CommentService()
    }
    return services


config_name = os.getenv('APP_SETTINGS')
app = create_app(create_services(), config_name)

if __name__ == '__main__':
    app.run()
