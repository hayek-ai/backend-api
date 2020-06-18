import os

from main import create_app
from main.service.bookmark_service import BookmarkService
from main.service.comment_service import CommentService
from main.service.confirmation_service import ConfirmationService
from main.service.password_reset_service import PasswordResetService
from main.service.download_service import DownloadService
from main.service.downvote_service import DownvoteService
from main.service.follow_service import FollowService
from main.service.idea_service import IdeaService
from main.service.performance_service import PerformanceService
from main.service.review_service import ReviewService
from main.service.upvote_service import UpvoteService
from main.service.user_service import UserService
from main.service.subscription_service import SubscriptionService


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
        'subscription': SubscriptionService(),
        'performance': PerformanceService()
    }
    return services


config_name = os.environ['APP_SETTINGS']
app = create_app(create_services(), config_name)

if __name__ == '__main__':
    app.run()
