import os

from app.main import create_app
from app.main.service.bookmark_service import BookmarkService
from app.main.service.comment_service import CommentService
from app.main.service.confirmation_service import ConfirmationService
from app.main.service.password_reset_service import PasswordResetService
from app.main.service.download_service import DownloadService
from app.main.service.downvote_service import DownvoteService
from app.main.service.follow_service import FollowService
from app.main.service.idea_service import IdeaService
from app.main.service.review_service import ReviewService
from app.main.service.upvote_service import UpvoteService
from app.main.service.user_service import UserService
from app.main.service.subscription_service import SubscriptionService


def create_services():
    services = {
        "user": UserService(),
        "confirmation": ConfirmationService(),
        "password_reset": PasswordResetService(),
        "idea": IdeaService(),
        "download": DownloadService(),
        "follow": FollowService(),
        'review': ReviewService(),
        'comment': CommentService(),
        'upvote': UpvoteService(),
        'downvote': DownvoteService(),
        'bookmark': BookmarkService(),
        'subscription': SubscriptionService()
    }
    return services


config_name = os.environ['APP_SETTINGS']
app = create_app(create_services(), config_name)

if __name__ == '__main__':
    app.run()
