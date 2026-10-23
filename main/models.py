from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
class Medicine(models.Model):
    CATEGORY_CHOICES=[(x,x) for x in ['Tablet','Capsule','Syrup','Antibiotic','Supplement','Injection','Cream','Other']]
    name=models.CharField(max_length=160); company=models.CharField(max_length=160,blank=True); category=models.CharField(max_length=30,choices=CATEGORY_CHOICES,default='Other')
    buy_price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0'))]); sell_price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0'))])
    quantity=models.PositiveIntegerField(default=0); low_stock_threshold=models.PositiveIntegerField(default=10); expiry_date=models.DateField(); batch_number=models.CharField(max_length=80,blank=True); created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['name']
    def __str__(self): return f'{self.name} ({self.quantity} in stock)'
    @property
    def is_low_stock(self): return self.quantity<=self.low_stock_threshold
    @property
    def is_expiring_soon(self): return self.expiry_date<=timezone.localdate()+timezone.timedelta(days=90)
    @property
    def is_expired(self): return self.expiry_date<timezone.localdate()
    @property
    def stock_cost_value(self): return self.buy_price*self.quantity
class Sale(models.Model):
    medicine=models.ForeignKey(Medicine,on_delete=models.PROTECT,related_name='sales'); quantity=models.PositiveIntegerField(validators=[MinValueValidator(1)])
    sold_price=models.DecimalField(max_digits=10,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))],help_text='Actual price charged per unit for this sale.')
    buy_price_at_sale=models.DecimalField(max_digits=10,decimal_places=2,editable=False); sold_at=models.DateTimeField(default=timezone.now)
    class Meta: ordering=['-sold_at']
    def save(self,*args,**kwargs):
        if not self.pk and self.medicine_id: self.buy_price_at_sale=self.medicine.buy_price
        super().save(*args,**kwargs)
    @property
    def total_revenue(self): return self.sold_price*self.quantity
    @property
    def profit(self): return self.total_revenue-self.buy_price_at_sale*self.quantity
