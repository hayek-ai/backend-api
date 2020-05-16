import datetime

from flask_restful import Resource, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from app.main.schema.user_schema import user_schema, user_register_schema, user_login_schema


class UserRegister(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.confirmation_service = kwargs['confirmation_service']
        self.user_schema = user_schema
        self.user_register_schema = user_register_schema

    def post(self):
        """
        Takes email, username, and password.  Then creates user (defaults to not analyst).
        Then sends confirmation email and returns new user.
        """
        user_json = request.get_json()
        errors = self.user_register_schema.validate(user_json)
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
                       "user": self.user_schema.dump(new_user),
                       "accessToken": access_token,
                       "confirmationEmailSent": email_success
                   }, 201
        except Exception as e:
            return get_error(500, str(e), field="general")


class User(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['service']
        self.user_schema = user_schema

    @jwt_required
    def get(self, username_or_id):
        if username_or_id.isdigit():
            user = self.user_service.get_user_by_id(username_or_id)
        else:
            user = self.user_service.get_user_by_username(username_or_id)

        if user:
            return self.user_schema.dump(user), 200
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
                image_extension = image.filename.split('.')[len(image.filename.split(".")) - 1]
                valid_extensions = ['jpg', 'png', 'jpeg']
                if image_extension not in valid_extensions:
                    return get_error(400, get_text("invalid_file_extension"))
                filename = f"{user.username}-profile-image.{image_extension}"
                self.user_service.change_user_image(user.id, image, filename)
            except Exception as e:
                return get_error(400, str(e))

        self.user_service.save_changes(user)
        return self.user_schema.dump(user), 201


class UserLogin(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['service']
        self.user_schema = user_schema
        self.user_login_schema = user_login_schema

    def post(self):
        credentials = request.get_json()
        errors = self.user_login_schema.validate(credentials)
        if errors:
            return get_error(400, get_text("incorrect_fields"), **errors)

        # allow user to login with email or username
        user = self.user_service.get_user_by_email(credentials["emailOrUsername"])
        if user is None:
            user = self.user_service.get_user_by_username(credentials["emailOrUsername"])

        if user and user.check_password(credentials["password"]):
            expires = datetime.timedelta(days=30)
            access_token = create_access_token(identity=user.id, expires_delta=expires, fresh=True)
            return {
                       "user": self.user_schema.dump(user),
                       "accessToken": access_token,
                   }, 200

        return get_error(401, get_text("user_invalid_credentials"), field="general")
