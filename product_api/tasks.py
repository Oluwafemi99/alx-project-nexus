from celery import shared_task
from django.core.mail import send_mail
from smtplib import SMTPException


@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # 3 retries, 60s delay
def send_low_stock_email(self, product_name, stock_quantity, recipient):
    subject = f"Low Stock Alert: {product_name}"
    message = f"Only {stock_quantity} units left for '{product_name}'. Please restock soon."

    try:
        send_mail(subject, message, 'noreply@yourdomain.com', [recipient], fail_silently=False)
    except SMTPException as exc:
        # Retry the task if email fails
        raise self.retry(exc=exc)
