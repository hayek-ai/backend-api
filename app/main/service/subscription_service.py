import os
import stripe

from app.main.db import db
from app.main.libs.strings import get_text
from app.main.model.subscription import SubscriptionModel
from app.main.model.user import UserModel

stripe.api_key = os.environ.get("STRIPE_TEST_SECRET_API_KEY")


class SubscriptionService:
    def save_new_subscription(self, stripe_cust_id: str,payment_method_id: str) -> "SubscriptionModel":
        user = UserModel.query.filter(UserModel.stripe_cust_id == stripe_cust_id).first()
        if not user:
            raise ValueError(get_text("not_found").format("User"))
        # attach the payment method to the customer
        stripe.PaymentMethod.attach(payment_method_id, customer=stripe_cust_id)
        # set the default payment method on the customer
        stripe.Customer.modify(stripe_cust_id, invoice_settings={
            'default_payment_method': payment_method_id
        })
        # create the subscription
        subscription = stripe.Subscription.create(
            customer=stripe_cust_id,
            items=[{'price': 'price_HO4cXUiEmz0i1i'}],
            expand=['latest_invoice.payment_intent']
        )
        is_active = subscription.latest_invoice.payment_intent.status == "succeeded"
        new_subscription = SubscriptionModel(
            stripe_subscription_id=subscription.id,
            current_period_end=subscription.current_period_end,
            stripe_price_id=subscription.items.data[0].price.id,
            is_active=is_active,
            user_id=user.id
        )
        self.save_changes(new_subscription)
        user.is_pro_tier = True
        self.save_changes(user)
        return subscription

    @classmethod
    def save_changes(cls, data) -> None:
        db.session.add(data)
        db.session.commit()
