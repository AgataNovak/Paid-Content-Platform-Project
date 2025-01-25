import os

import stripe

stripe.api_key = os.environ["STRIPE_API_KEY"]


def create_stripe_product(product):

    stripe.Product.create(name=product)


def create_stripe_price(amount):

    price = stripe.Price.create(
        currency="rub", unit_amount=amount, product_data={"name": "Payment"}
    )
    return price


def create_stripe_session(price):

    session = stripe.checkout.Session.create(
        success_url="https://127.0.0.1:8000/",
        line_items=[{"price": price, "quantity": 1}],
        mode="payment",
    )
    return session.get("id"), session.get("url")
