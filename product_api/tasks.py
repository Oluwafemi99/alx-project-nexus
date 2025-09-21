from celery import shared_task
from django.core.mail import send_mail
from smtplib import SMTPException
from . models import RequestLog, SuspiciousIP
from django.utils.timezone import now, timedelta
from .models import DailySales, Account
from datetime import date


# Task to Alert Low Stock by Email
@shared_task(bind=True, max_retries=3, default_retry_delay=60)  # 3 retries, 60s delay
def send_low_stock_email(self, product_name, stock_quantity, recipient):
    subject = f"Low Stock Alert: {product_name}"
    message = f"Only {stock_quantity} units left for '{product_name}'. Please restock soon."

    try:
        send_mail(
            subject, message, 'noreply@yourdomain.com',
            [recipient], fail_silently=False)
    except SMTPException as exc:
        # Retry the task if email fails
        raise self.retry(exc=exc)


SENSITIVE_PATHS = ['/admin', '/login']


# Task to Flag Suspicious IP
@shared_task
def flag_suspicious_ips():
    one_hour_ago = now() - timedelta(hours=1)

    # Get all logs from the past hour
    recent_logs = RequestLog.objects.filter(timestamp__gte=one_hour_ago)

    # Count requests per IP
    ip_counts = {}
    flagged_ips = set()

    for log in recent_logs:
        ip = log.ip_address
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

        # Check for sensitive path access
        if log.path in SENSITIVE_PATHS:
            flagged_ips.add(ip)
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                defaults={'reason': f"Accessed sensitive path: {log.path}"}
            )

    # Flag IPs exceeding 100 requests/hour
    for ip, count in ip_counts.items():
        if count > 100 and ip not in flagged_ips:
            SuspiciousIP.objects.get_or_create(
                ip_address=ip,
                defaults={'reason': f"{count} requests in the past hour"}
            )


# Task to Send order confirmation email
@shared_task
def send_order_confirmation_email(order_id, user_email):
    subject = "Order Confirmation"
    message = f"Thank you! Your order {order_id} has been confirmed."
    send_mail(
        subject,
        message,
        "noreply@yourdomain.com",
        [user_email],
        fail_silently=True,
    )


# Task to save Daily sales and Reset Account for a New Day
@shared_task
def save_daily_sales_task():
    try:
        account = Account.objects.get(
            account_id="00000000-0000-0000-0000-000000000001")
    except Account.DoesNotExist:
        return "Global account not found"

    DailySales.objects.create(
        date=date.today(),
        total_sales_amount=account.total_sales_amount,
        total_transactions=account.total_transactions,
        total_stock_sold=account.total_stock_sold
    )
    # Reset global account for new day
    account.total_sales_amount = 0
    account.total_transactions = 0
    account.total_stock_sold = 0
    account.save()
    return f"Saved daily sales for {date.today()}"
