from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import MedicineForm, SaleForm
from .models import Medicine, Sale

def dashboard(request):
    qs=Medicine.objects.all(); today=timezone.localdate()
    return render(request,'main/dashboard.html',{'medicine_count':qs.count(),'stock_units':qs.aggregate(n=Sum('quantity'))['n'] or 0,'low_stock_count':qs.filter(quantity__lte=F('low_stock_threshold')).count(),'expiring_count':qs.filter(expiry_date__lte=today+timezone.timedelta(days=90)).count(),'recent_sales':Sale.objects.select_related('medicine')[:6]})

def medicine_list(request):
    qs=Medicine.objects.all(); q=request.GET.get('q','').strip(); category=request.GET.get('category',''); status=request.GET.get('status','')
    if q: qs=qs.filter(Q(name__icontains=q)|Q(company__icontains=q)|Q(batch_number__icontains=q))
    if category: qs=qs.filter(category=category)
    if status=='low': qs=qs.filter(quantity__lte=F('low_stock_threshold'))
    elif status=='expiring': qs=qs.filter(expiry_date__lte=timezone.localdate()+timezone.timedelta(days=90),expiry_date__gte=timezone.localdate())
    elif status=='expired': qs=qs.filter(expiry_date__lt=timezone.localdate())
    return render(request,'main/medicine_list.html',{'medicines':qs,'query':q,'category':category,'status':status,'categories':Medicine.CATEGORY_CHOICES})

def medicine_create(request):
    form=MedicineForm(request.POST or None)
    if form.is_valid():
        form.save(); messages.success(request,'Medicine added.'); return redirect('main:medicine_list')
    return render(request,'main/medicine_form.html',{'form':form,'title':'Add medicine'})

def medicine_edit(request,pk):
    obj=get_object_or_404(Medicine,pk=pk); form=MedicineForm(request.POST or None,instance=obj)
    if form.is_valid():
        form.save(); messages.success(request,'Medicine updated.'); return redirect('main:medicine_list')
    return render(request,'main/medicine_form.html',{'form':form,'title':'Edit medicine'})

def medicine_delete(request,pk):
    obj=get_object_or_404(Medicine,pk=pk)
    if request.method=='POST':
        if obj.sales.exists(): messages.error(request,'Medicine has sales history; set its quantity to zero instead.')
        else: obj.delete(); messages.success(request,'Medicine deleted.')
        return redirect('main:medicine_list')
    return render(request,'main/confirm_delete.html',{'medicine':obj})

def sales(request):
    return render(request,'main/sales.html',{'sales':Sale.objects.select_related('medicine')[:200]})

def sale_create(request):
    initial={'medicine':request.GET.get('medicine')} if request.GET.get('medicine') else None
    form=SaleForm(request.POST or None,initial=initial)
    if form.is_valid():
        sale=form.save(commit=False)
        with transaction.atomic():
            medicine=Medicine.objects.select_for_update().get(pk=sale.medicine_id)
            if sale.quantity>medicine.quantity: form.add_error('quantity',f'Only {medicine.quantity} unit(s) in stock.')
            else:
                sale.medicine=medicine; sale.buy_price_at_sale=medicine.buy_price
                medicine.quantity-=sale.quantity; medicine.save(update_fields=['quantity'])
                sale.save(); messages.success(request,'Sale recorded; stock updated.'); return redirect('main:sales')
    return render(request,'main/sale_form.html',{'form':form,'title':'Record sale'})
