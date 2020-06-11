import datetime

from flask_restful import Resource, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from app.main.schema.user_schema import (
    user_schema,
    user_register_schema,
    user_login_schema,
    user_follow_list_schema,
    analyst_leaderboard_schema,
)
from app.main.schema.idea_schema import idea_list_schema


class UserRegister(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.confirmation_service = kwargs['confirmation_service']

    def post(self):
        """
        Takes email, username, and password.  Then creates user (defaults to not analyst).
        Then sends confirmation email and returns new user.
        """
        user_json = request.get_json()
        errors = user_register_schema.validate(user_json)
        if errors:
            response_errors = []
            for key, value in errors.items():
                response_errors.append({
                    "status": 400,
                    "detail": value[0],
                    "field": key
                })
            return {"errors": response_errors}, 400

        user = self.user_service.get_user_by_email(user_json['email'])
        if user:
            return get_error(409, get_text("email_exists"), field="email")

        user = self.user_service.get_user_by_username(user_json['username'])
        if user:
            return get_error(409, get_text("username_exists"), field="username")

        try:
            new_user = self.user_service.save_new_user(
                user_json["email"],
                user_json["username"],
                user_json["password"]
            )
            email_success = bool(self.confirmation_service.send_confirmation_email(new_user.id))
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(identity=new_user.id, expires_delta=expires, fresh=True)
            return {
                       "user": {
                           **user_schema.dump(new_user),
                           "following": [],
                           "followers": [],
                           "ideas": []
                       },
                       "accessToken": access_token,
                       "confirmationEmailSent": email_success
                   }, 201
        except Exception as e:
            return get_error(500, str(e), field="general")


class User(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.follow_service = kwargs['follow_service']

    @jwt_required
    def get(self, username_or_id):
        if username_or_id.isdigit():
            user = self.user_service.get_user_by_id(username_or_id)
        else:
            user = self.user_service.get_user_by_username(username_or_id)

        if user:
            following = self.follow_service.get_following(user.id)
            followers = self.follow_service.get_followers(user.id)
            return {
                **user_schema.dump(user),
                "following": user_follow_list_schema.dump(following),
                "followers": user_follow_list_schema.dump(followers),
                "ideas": idea_list_schema.dump(user.ideas.all())
            }, 200
        else:
            return get_error(404, get_text("not_found").format("User"))

    @jwt_required
    def put(self, username_or_id):
        if username_or_id.isdigit():
            user = self.user_service.get_user_by_id(username_or_id)
        else:
            user = self.user_service.get_user_by_username(username_or_id)

        if not user:
            return get_error(404, get_text("not_found").format("User"))

        # users are only permitted to edit their own account details.
        if user.id != get_jwt_identity():
            return get_error(403, get_text("unauthorized_user_edit"))

        if "bio" in request.form:
            if request.form.get('bio').strip() == "":
                user.bio = None
            else:
                user.bio = request.form.get('bio')
        if "prefersDarkmode" in request.form:
            if request.form.get('prefersDarkmode').lower() == "true":
                user.prefers_darkmode = True
            else:
                user.prefers_darkmode = False

        if "profileImage" in request.files:
            try:
                # get file and rename
                image = request.files['profileImage']
                image_extension = image.filename.split('.')[len(image.filename.split(".")) - 1].lower()
                valid_extensions = ['jpg', 'png', 'jpeg']
                if image_extension not in valid_extensions:
                    return get_error(400, get_text("invalid_file_extension"))
                filename = f"{user.username}-profile-image.{image_extension}"
                self.user_service.change_user_image(user.id, image, filename)
            except Exception as e:
                return get_error(400, str(e))

        self.user_service.save_changes(user)
        following = self.follow_service.get_following(user.id)
        followers = self.follow_service.get_followers(user.id)
        return {
            **user_schema.dump(user),
            "following": user_follow_list_schema.dump(following),
            "followers": user_follow_list_schema.dump(followers),
            "ideas": idea_list_schema.dump(user.ideas.all())
        }, 201


class UserLogin(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.follow_service = kwargs['follow_service']

    def post(self):
        credentials = request.get_json()
        errors = user_login_schema.validate(credentials)
        if errors:
            return get_error(400, get_text("incorrect_fields"), **errors)

        # allow user to login with email or username
        user = self.user_service.get_user_by_email(credentials["emailOrUsername"])
        if user is None:
            user = self.user_service.get_user_by_username(credentials["emailOrUsername"])

        if user and user.check_password(credentials["password"]):
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(identity=user.id, expires_delta=expires, fresh=True)
            following = self.follow_service.get_following(user.id)
            followers = self.follow_service.get_followers(user.id)
            return {
               "user": {
                   **user_schema.dump(user),
                   "following": user_follow_list_schema.dump(following),
                   "followers": user_follow_list_schema.dump(followers),
                   "ideas": idea_list_schema.dump(user.ideas.all())
                },
               "accessToken": access_token,
            }, 200

        return get_error(401, get_text("user_invalid_credentials"), field="general")


class AnalystLeaderboard(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']

    def get(self):
        """
        Takes a query string and returns a list of analysts for leaderboard
        parameters:
            sortColumn (str) -> "analyst_rank", "success_rate", "avg_return",
                "num_ideas", "avg_holding_period", "num_followers"
            orderType (str) -> "desc" or "asc
            page (int)
            pageSize (int)
        """
        query_string = request.args
        page = 0
        page_size = None
        if "page" in query_string:
            page = int(query_string["page"])
        if "pageSize" in query_string:
            page_size = int(query_string["pageSize"])

        try:
            analysts = self.user_service.get_analysts_for_leaderboard(
                query_string=query_string,
                page=page,
                page_size=page_size)
            return analyst_leaderboard_schema.dump(analysts), 200
        except Exception as e:
            return get_error(500, str(e))

