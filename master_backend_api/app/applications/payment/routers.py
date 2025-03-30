from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from pydantic import AnyUrl

from applications.payment.constants import CurrencyEnum
from applications.payment.schemas import StripePaymentUrl, SetOrderToClosedSchema
from applications.products.crud import order_manager
from applications.products.models import Order
from applications.products.schemas import OrderSchema
from applications.users.crud import user_manager
from applications.users.models import User
from dependencies.database import get_async_session
from fastapi import APIRouter, Depends, Header, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

import stripe

from dependencies.security import get_current_user
from settings import settings
from utils.images import ensure_full_url

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.get("/payment-stripe-data")
async def payment_stripe_data(
    user: User = Depends(get_current_user), session: AsyncSession = Depends(get_async_session)
) -> StripePaymentUrl:
    order = await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
    raw_data = OrderSchema.from_orm(order)
    raw_data.filter_zero_quantity_products()

    line_items: list[dict] = [
        {
            "price_data": {
                "currency": CurrencyEnum.UAH,
                "product_data": {
                    "name": order_product.product.title,
                    "description": order_product.product.description or "",
                    "images": [ensure_full_url(order_product.product.main_image)]
                    + [ensure_full_url(img) for img in order_product.product.images],
                },
                "unit_amount": int(order_product.price * 100),
            },
            "quantity": order_product.quantity,
        }
        for order_product in raw_data.order_products
    ]

    session_stripe: dict = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        success_url=f"{settings.WORK_URL}/payment/success-payment",
        cancel_url=f"{settings.WORK_URL}/payment/failed-payment",
        customer_email=user.email,
        # locale='uk',
        metadata={"user_uuid": user.uuid_data, "total": raw_data.cost, "order_id": order.id},
    )

    return StripePaymentUrl(url=session_stripe["url"])


@router.post("/proceed-payment-stripe-hook")
async def proceed_payment_stripe(
    data: dict,
    session: AsyncSession = Depends(get_async_session),
):
    if not data:
        return
    # n = {
    #     "id": "evt_1PfmSbRvJkC5nYiuZcj7BJaL",
    #     "object": "event",
    #     "api_version": "2024-06-20",
    #     "created": 1721755512,
    #     "data": {
    #         "object": {
    #             "id": "cs_test_a1hEyG1x8EtCPlm5rVW3jrN8HLVqEIBPAzM6aENJIlC0ifMv1Dy2esougo",
    #             "object": "checkout.session",
    #             "after_expiration": None,
    #             "allow_promotion_codes": None,
    #             "amount_subtotal": 580800,
    #             "amount_total": 580800,
    #             "automatic_tax": {"enabled": False, "liability": None, "status": None},
    #             "billing_address_collection": None,
    #             "cancel_url": "https://96ea-176-119-83-0.ngrok-free.app/cancel_payment",
    #             "client_reference_id": None,
    #             "client_secret": None,
    #             "consent": None,
    #             "consent_collection": None,
    #             "created": 1721755489,
    #             "currency": "usd",
    #             "currency_conversion": None,
    #             "custom_fields": [],
    #             "custom_text": {
    #                 "after_submit": None,
    #                 "shipping_address": None,
    #                 "submit": None,
    #                 "terms_of_service_acceptance": None,
    #             },
    #             "customer": None,
    #             "customer_creation": "if_required",
    #             "customer_details": {
    #                 "address": {
    #                     "city": None,
    #                     "country": "UA",
    #                     "line1": None,
    #                     "line2": None,
    #                     "postal_code": None,
    #                     "state": None,
    #                 },
    #                 "email": "12345@ukr.net",
    #                 "name": "kjfhjgfhj",
    #                 "phone": None,
    #                 "tax_exempt": "none",
    #                 "tax_ids": [],
    #             },
    #             "customer_email": "12345@ukr.net",
    #             "expires_at": 1721841889,
    #             "invoice": None,
    #             "invoice_creation": {
    #                 "enabled": False,
    #                 "invoice_data": {
    #                     "account_tax_ids": None,
    #                     "custom_fields": None,
    #                     "description": None,
    #                     "footer": None,
    #                     "issuer": None,
    #                     "metadata": {},
    #                     "rendering_options": None,
    #                 },
    #             },
    #             "livemode": False,
    #             "locale": None,
    #             "metadata": {"our_metadata": "78787877"},
    #             "mode": "payment",
    #             "payment_intent": "pi_3PfmSYRvJkC5nYiu1W4lMDqC",
    #             "payment_link": None,
    #             "payment_method_collection": "if_required",
    #             "payment_method_configuration_details": None,
    #             "payment_method_options": {"card": {"request_three_d_secure": "automatic"}},
    #             "payment_method_types": ["card"],
    #             "payment_status": "paid",
    #             "phone_number_collection": {"enabled": False},
    #             "recovered_from": None,
    #             "saved_payment_method_options": None,
    #             "setup_intent": None,
    #             "shipping_address_collection": None,
    #             "shipping_cost": None,
    #             "shipping_details": None,
    #             "shipping_options": [],
    #             "status": "complete",
    #             "submit_type": None,
    #             "subscription": None,
    #             "success_url": "https://96ea-176-119-83-0.ngrok-free.app/success_payment",
    #             "total_details": {"amount_discount": 0, "amount_shipping": 0, "amount_tax": 0},
    #             "ui_mode": "hosted",
    #             "url": None,
    #         }
    #     },
    #     "livemode": False,
    #     "pending_webhooks": 3,
    #     "request": {"id": None, "idempotency_key": None},
    #     "type": "checkout.session.completed",
    # }
    try:
        event = stripe.Event.construct_from(data, settings.STRIPE_SECRET_KEY)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(detail="NOT STRIPE DATA", status_code=status.HTTP_400_BAD_REQUEST)
    print(event)
    if event["type"] == "checkout.session.completed":
        user_uuid = event["data"]["object"]["metadata"]["user_uuid"]
        user = await user_manager.get_item(field=User.uuid_data, field_value=user_uuid, session=session)
        if not user:
            raise HTTPException(detail="No users found", status_code=status.HTTP_400_BAD_REQUEST)

        order: Order = await order_manager.get_or_create(user_id=user.id, is_closed=False, session=session)
        paid = data["data"]["object"]["amount_total"]
        if int(float(order.cost)) != int(float(paid / 100)):
            # for sentry log
            raise ValueError(f"{order.id=}, {user.id=} => {paid/100=}{order.cost=}")
        await order_manager.patch_item(
            instance_id=order.id, session=session, data_to_patch=SetOrderToClosedSchema(), exclude_unset=False
        )
        return {"Order closed": True}
