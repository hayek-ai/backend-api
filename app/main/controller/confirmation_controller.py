from flask_restful import Resource

from app.main.libs.strings import get_text
from app.main.libs.util import get_error
from flask_jwt_extended import get_jwt_identity, jwt_required


class Confirmation(Resource):
    def __init__(self, **kwargs):
        self.confirmation_service = kwargs['confirmation_service']
        self.user_service = kwargs['user_service']

    @jwt_required
    def get(self, confirmation_code: str):
        """Confirms user with confirmation_code"""
        user_id = get_jwt_identity()
        user = self.user_service.get_user_by_id(user_id)
        confirmation = user.most_recent_confirmation
        if not confirmation:
            return get_error(404, get_text("not_found").format("Confirmation"))

        if user.is_confirmed:
            return get_error(400, get_text("user_already_confirmed"))

        if confirmation.is_expired:
            self.confirmation_service.save_new_confirmation(user_id)
            self.confirmation_service.send_confirmation_email(user_id)
            return get_error(400, get_text("confirmation_code_expired"))

        if confirmation_code != confirmation.code:
            return get_error(400, get_text("incorrect_confirmation_code"))

        confirmation.is_confirmed = True
        self.confirmation_service.save_changes(confirmation)
        user.is_confirmed = True
        self.user_service.save_changes(user)

        return {"message": get_text("user_confirmed")}, 200


class ResendConfirmation(Resource):
    def __init__(self, **kwargs):
        self.confirmation_service = kwargs['confirmation_service']
        self.user_service = kwargs['user_service']

    @jwt_required
    def post(self):
        """Resend confirmation email"""
        user_id = get_jwt_identity()
        user = self.user_service.get_user_by_id(user_id)
        if user.is_confirmed:
            return get_error(400, get_text("user_already_confirmed"))

        try:
            # make sure most recent confirmation expired and send new confirmation email
            confirmation = user.most_recent_confirmation
            if confirmation:
                self.confirmation_service.force_to_expire(confirmation.id)
            self.confirmation_service.save_new_confirmation(user_id)
            self.confirmation_service.send_confirmation_email(user_id)
            return {"message": get_text("confirmation_resend_successful")}, 201
        except Exception as e:
            return get_error(500, str(e))
