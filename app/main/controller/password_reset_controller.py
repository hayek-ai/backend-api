from flask_restful import Resource, request

from app.main.libs.strings import get_text
from app.main.libs.util import get_error


class SendPasswordReset(Resource):
    def __init__(self, **kwargs):
        self.password_reset_service = kwargs['password_reset_service']
        self.user_service = kwargs['user_service']

    def post(self):
        """Sends email with link to reset password"""
        request_json = request.get_json()
        try:
            email = request_json["email"]
        except Exception as e:
            return get_error(400, str(e))
        user = self.user_service.get_user_by_email(email)
        if not user:
            return get_error(400, get_text("not_found").format("User"))
        try:
            # make sure most recent reset expired and send new email
            password_reset = user.most_recent_password_reset
            if password_reset:
                self.password_reset_service.force_to_expire(password_reset.id)
            self.password_reset_service.save_new_password_reset(user.id)
            self.password_reset_service.send_password_reset_email(user.id)
            return {"message": get_text("password_reset_sent")}, 201
        except Exception as e:
            return get_error(500, str(e))


class PasswordReset(Resource):
    def __init__(self, **kwargs):
        self.password_reset_service = kwargs['password_reset_service']
        self.user_service = kwargs['user_service']

    def post(self, password_reset_code: str):
        """Resets user's password w/ code and new password in JSON body"""
        request_json = request.get_json()
        try:
            new_password = request_json["password"]
        except Exception as e:
            return get_error(400, str(e))
        password_reset = self.password_reset_service.get_password_reset_by_id(password_reset_code)
        if not password_reset:
            return get_error(404, get_text("not_found").format("Password Reset"))
        user = self.user_service.get_user_by_id(password_reset.user_id)
        if password_reset.is_expired:
            self.password_reset_service.save_new_password_reset(user.id)
            self.password_reset_service.send_password_reset_email(user.id)
            return get_error(400, get_text("password_reset_expired"))
        if password_reset.id != user.most_recent_password_reset.id:
            return get_error(400, get_text("incorrect_password_reset_code"))
        user.password = new_password
        self.user_service.save_changes(user)
        return {"message": get_text("password_changed")}, 200

