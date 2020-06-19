import unittest
from test.conftest import flask_test_client

flask_client = flask_test_client()


class TestEndpointsConfiguration(unittest.TestCase):
    def setUp(self):
        endpoints = []
        for rule in flask_client.application.url_map.iter_rules():
            endpoints.append(str(rule))
        self.endpoints = endpoints

    def test_endpoints_are_configured(self):
        assert '/register' in self.endpoints
        assert '/login' in self.endpoints
        assert '/user/<username_or_id>' in self.endpoints
        assert '/leaderboard' in self.endpoints
        assert '/user/confirm/<string:confirmation_code>' in self.endpoints
        assert '/resend-confirmation' in self.endpoints
        assert '/user/reset-password' in self.endpoints
        assert '/user/reset-password/<string:password_reset_code>' in self.endpoints
        assert '/new-idea' in self.endpoints
        assert '/idea/<int:idea_id>' in self.endpoints
        assert '/idea/<int:idea_id>/download' in self.endpoints
        assert '/analyst/<int:analyst_id>/follow' in self.endpoints
        assert '/user/<int:user_id>/following' in self.endpoints
        assert '/analyst/<int:analyst_id>/followers' in self.endpoints
        assert '/analyst/<int:analyst_id>/review' in self.endpoints
        assert '/review/<int:review_id>' in self.endpoints
        assert '/analyst/<int:analyst_id>/reviews' in self.endpoints
        assert '/idea/<int:idea_id>/comment' in self.endpoints
        assert '/comment/<int:comment_id>' in self.endpoints
        assert '/idea/<int:idea_id>/comments' in self.endpoints
        assert '/idea/<int:idea_id>/upvote' in self.endpoints
        assert '/user/<string:username>/upvotes' in self.endpoints
        assert '/idea/<int:idea_id>/downvote' in self.endpoints
        assert '/idea/<int:idea_id>/bookmark' in self.endpoints
        assert '/user/<string:username>/bookmarks' in self.endpoints
        assert '/stock/<string:symbol>' in self.endpoints
        assert '/autosearch' in self.endpoints
        assert '/create-subscription' in self.endpoints
        assert '/retry-invoice' in self.endpoints
        assert '/cancel-subscription' in self.endpoints
        assert '/stripe-webhook' in self.endpoints
