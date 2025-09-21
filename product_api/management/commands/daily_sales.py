from django.core.management.base import BaseCommand
from datetime import date
from product_api.models import Account, DailySales


class Command(BaseCommand):
    help = "Save daily sales and reset global account"

    def handle(self, *args, **kwargs):
        try:
            account = Account.objects.get(account_id="00000000-0000-0000-0000-000000000001")
        except Account.DoesNotExist:
            self.stdout.write("Global account not found")
            return

        # Create DailySales record
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

        self.stdout.write(f"Saved Daily Sales for {date.today()} and reset Account Successfully.")
