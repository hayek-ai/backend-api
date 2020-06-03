import os
import stripe

from app.main.db import db
from app.main.libs.strings import get_text
from app.main.model.subscription import SubscriptionModel
from app.main.model.user import UserModel

stripe.api_key = os.environ.get("STRIPE_TEST_SECRET_API_KEY")
hayek_pro_price_id = "price_1Gq3mdCXANgFLlKVwCQwEquQ"


class SubscriptionService:
    def save_new_subscription(self, user_id: int, payment_method_id: str) -> dict:
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            raise ValueError(get_text("not_found").format("User"))
        if user.is_pro_tier is True:
            raise ValueError(get_text("already_subscribed"))
        stripe_cust_id = user.stripe_cust_id
        # attach the payment method to the customer
        stripe.PaymentMethod.attach(payment_method_id, customer=stripe_cust_id)
        # set the default payment method on the customer
        stripe.Customer.modify(stripe_cust_id, invoice_settings={
            'default_payment_method': payment_method_id
        })
        # create the subscription
        subscription = stripe.Subscription.create(
            customer=stripe_cust_id,
            items=[{'price': hayek_pro_price_id}],
            expand=['latest_invoice.payment_intent']
        )
        status = subscription['latest_invoice']['payment_intent']['status']
        new_subscription = SubscriptionModel(
            stripe_subscription_id=subscription.id,
            current_period_end=subscription.current_period_end,
            stripe_price_id=subscription["items"]["data"][0]["price"]["id"],
            status=status,
            user_id=user_id
        )
        self.save_changes(new_subscription)
        if status == "succeeded":
            user.is_pro_tier = True
            self.save_changes(user)
        return subscription

    def retry_invoice(self, user_id: int, payment_method_id: str, invoice_id: str) -> dict:
        """
        Updates customer with the new payment method, and assigns it as
        new default payment method for subscription invoices.
        """
        user = UserModel.query.filter_by(id=user_id).first()
        if not user:
            raise ValueError(get_text("not_found").format("User"))
        if user.is_pro_tier is True:
            raise ValueError(get_text("already_subscribed"))
        stripe_cust_id = user.stripe_cust_id
        stripe.PaymentMethod.attach(payment_method_id, customer=stripe_cust_id)
        # set the default payment method on the customer
        stripe.Customer.modify(stripe_cust_id, invoice_settings={
            'default_payment_method': payment_method_id
        })
        invoice = stripe.Invoice.retrieve(invoice_id, expand=['payment_intent'])
        print(invoice.error)
        if not invoice.error:
            user.is_pro_tier = True
            sub = user.most_recent_subscription
            sub.status = "succeeded"
            self.save_changes(user)
            self.save_changes(sub)
        return invoice

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
