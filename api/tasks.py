from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Order

@shared_task
def send_order_confirmation(order_id, user_emali):
    subject = 'Order Confirmation'
    message = f'Your order has been successfully placed. Order ID: {order_id}'
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_emali])