from datetime import timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from main.models import Medicine, Sale

class Command(BaseCommand):
    help = "Add realistic demo medicines and sample sales for Sherzad Pharmacy."

    @transaction.atomic
    def handle(self, *args, **options):
        today = timezone.localdate()
        demo_medicines = [
            {"name":"Paracetamol 500mg","company":"Acme Pharma","category":"Tablet","buy_price":"0.05","sell_price":"0.10","quantity":200,"low_stock_threshold":40,"expiry_date":today+timedelta(days=540),"batch_number":"PCM-2601"},
            {"name":"Amoxicillin 500mg","company":"NovaMed Labs","category":"Antibiotic","buy_price":"0.20","sell_price":"0.35","quantity":150,"low_stock_threshold":30,"expiry_date":today+timedelta(days=420),"batch_number":"AMX-2602"},
            {"name":"Ibuprofen 400mg","company":"HealthPlus","category":"Tablet","buy_price":"0.08","sell_price":"0.15","quantity":18,"low_stock_threshold":25,"expiry_date":today+timedelta(days=365),"batch_number":"IBU-2511"},
            {"name":"Omeprazole 20mg","company":"CureWell","category":"Capsule","buy_price":"0.12","sell_price":"0.25","quantity":50,"low_stock_threshold":15,"expiry_date":today+timedelta(days=35),"batch_number":"OMP-2601"},
            {"name":"Cetirizine 10mg","company":"NovaMed Labs","category":"Other","buy_price":"0.06","sell_price":"0.12","quantity":120,"low_stock_threshold":20,"expiry_date":today+timedelta(days=300),"batch_number":"CTZ-2603"},
            {"name":"Azithromycin 500mg","company":"Acme Pharma","category":"Antibiotic","buy_price":"0.30","sell_price":"0.55","quantity":8,"low_stock_threshold":20,"expiry_date":today+timedelta(days=480),"batch_number":"AZI-2601"},
            {"name":"Vitamin D3 1000 IU","company":"VitaCare","category":"Supplement","buy_price":"0.15","sell_price":"0.30","quantity":90,"low_stock_threshold":20,"expiry_date":today+timedelta(days=600),"batch_number":"VD3-2602"},
            {"name":"Cough Syrup 100ml","company":"CureWell","category":"Syrup","buy_price":"0.40","sell_price":"0.70","quantity":25,"low_stock_threshold":30,"expiry_date":today+timedelta(days=20),"batch_number":"CS-2601"},
            {"name":"Metformin 500mg","company":"HealthPlus","category":"Tablet","buy_price":"0.07","sell_price":"0.15","quantity":100,"low_stock_threshold":25,"expiry_date":today+timedelta(days=390),"batch_number":"MET-2602"},
            {"name":"Amlodipine 5mg","company":"Medline Works","category":"Tablet","buy_price":"0.10","sell_price":"0.20","quantity":60,"low_stock_threshold":15,"expiry_date":today-timedelta(days=5),"batch_number":"AML-2508"},
        ]
        created = 0
        for data in demo_medicines:
            medicine, was_created = Medicine.objects.get_or_create(
                name=data["name"], company=data["company"], batch_number=data["batch_number"],
                defaults=data,
            )
            if was_created:
                created += 1

        # Create example transactions once only. Existing stock is left intact
        # on subsequent runs so the command is safe to rerun.
        if not Sale.objects.exists():
            examples = [
                ("Paracetamol 500mg","Acme Pharma","PCM-2601",12,"0.09"),
                ("Amoxicillin 500mg","NovaMed Labs","AMX-2602",5,"0.32"),
                ("Cetirizine 10mg","NovaMed Labs","CTZ-2603",8,"0.10"),
            ]
            sales_created = 0
            for name, company, batch, qty, price in examples:
                medicine = Medicine.objects.get(name=name, company=company, batch_number=batch)
                if medicine.quantity >= qty:
                    Sale.objects.create(
                        medicine=medicine, quantity=qty, sold_price=Decimal(price),
                        buy_price_at_sale=medicine.buy_price,
                    )
                    medicine.quantity -= qty
                    medicine.save(update_fields=["quantity"])
                    sales_created += 1
        else:
            sales_created = 0

        self.stdout.write(self.style.SUCCESS(
            f"Demo data ready: {created} new medicines added and {sales_created} sample sales created. "
            "Existing records were preserved."
        ))
