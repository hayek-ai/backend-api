import os
import stripe
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from main.libs.strings import get_text
from main.libs.util import get_error


class CreateSubscription(Resource):
    def __init__(self, **kwargs):
        self.subscription_service = kwargs['subscription_service']

    @jwt_required
    def post(self):
        """
        Creates pro tier subscription and returns Stripe's subscription obj if successful
        """
        payment_method_id = request.json.get('paymentMethodId', None)
        if not payment_method_id:
            return get_error(400, get_text("incorrect_fields"))

        user_id = get_jwt_identity()
        try:
            subscription = self.subscription_service.save_new_subscription(
                user_id=user_id,
                payment_method_id=payment_method_id
            )
            return subscription, 201
        except Exception as e:
            return get_error(400, str(e))


class RetryInvoice(Resource):
    def __init__(self, **kwargs):
        self.subscription_service = kwargs['subscription_service']

    @jwt_required
    def post(self):
        """Retries subscription creation if initial payment method fails"""
        payment_method_id = request.json.get('paymentMethodId', None)
        if not payment_method_id:
            return get_error(400, get_text("incorrect_fields"))

        user_id = get_jwt_identity()
        try:
            invoice = self.subscription_service.retry_invoice(
                user_id=user_id,
                payment_method_id=payment_method_id
            )
            return invoice, 201
        except Exception as e:
            return get_error(400, str(e))


class CancelSubscription(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']
        self.subscription_service = kwargs['subscription_service']

    @jwt_required
    def post(self):
        user_id = get_jwt_identity()
        user = self.user_service.get_user_by_id(user_id)
        if not user:
            return get_text(404, get_text("not_found").format("User"))
        if user.pro_tier_status != "succeeded":
            return get_text(400, get_text("subscription_not_active"))
        sub = user.subscriptions.first()
        if not sub:
            return get_text(404, get_text("not_found").format("Subscription"))
        try:
            deleted_subscription = stripe.Subscription.delete(sub.stripe_subscription_id)
            user.pro_tier_status = "deleted"
            self.user_service.save_changes(user)
            self.subscription_service.delete_from_db(sub)
            return deleted_subscription, 200
        except Exception as e:
            return get_error(403, str(e))


class StripeWebhook(Resource):
    def __init__(self, **kwargs):
        self.user_service = kwargs['user_service']

    def post(self):
        """
        Webooks receive events from Stripe
        primary events: invoice.payment_failed and invoice.payment_succeeded
        """
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")
        request_data = request.get_json()
        if webhook_secret:
            # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
            signature = request.headers.get('stripe-signature')
            try:
                event = stripe.Webhook.construct_event(
                    payload=request.data, sig_header=signature, secret=webhook_secret)
                data = event['data']
            except Exception as e:
                return e
            # Get the type of webhook event sent - used to check the status of PaymentIntents.
            event_type = event['type']
        else:
            data = request_data['data']
            event_type = request_data['type']

        data_object = data['object']

        if "customer" in data_object:
            stripe_cust_id = data_object['customer']
            user = self.user_service.get_user_by_stripe_cust_id(stripe_cust_id)
            if not user:
                return get_error(404, get_text("not_found").format("User"))

            if event_type == 'invoice.payment_succeeded':
                user.pro_tier_status = "succeeded"

            if event_type == 'invoice.payment_failed':
                user.pro_tier_status = "requires_payment_method"

            self.user_service.save_changes(user)

        return {'status': 'success'}, 200





