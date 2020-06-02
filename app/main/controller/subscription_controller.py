from flask_restful import Resource, request
from flask_jwt_extended import jwt_required

from app.main.libs.strings import get_text
from app.main.libs.util import get_error


class CreateSubscription(Resource):
    def __init__(self, **kwargs):
        self.subscription_service = kwargs['subscription_service']

    @jwt_required
    def post(self):
        """
        Creates pro tier subscription and returns Stripe's subscription obj if successful
        """
        data = request.get_json()
        try:
            subscription = self.subscription_service.save_new_subscription(
                stripe_cust_id=data['customerId'],
                payment_method_id=data['paymentMethodId']
            )
            return subscription, 201
        except Exception as e:
            return get_error(400, str(e))

