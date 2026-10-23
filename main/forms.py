from django import forms
from .models import Medicine, Sale
class MedicineForm(forms.ModelForm):
    class Meta:
        model=Medicine
        fields=['name','company','category','buy_price','sell_price','quantity','low_stock_threshold','expiry_date']
        widgets={'expiry_date':forms.DateInput(attrs={'type':'date'})}
class SaleForm(forms.ModelForm):
    class Meta:
        model=Sale
        fields=['medicine','quantity','sold_price']
        widgets={'quantity':forms.NumberInput(attrs={'min':1,'step':1}),'sold_price':forms.NumberInput(attrs={'min':'0.01','step':'0.01'})}
