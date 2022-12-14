from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required, permission_required

from django.urls import reverse_lazy

from .forms import *
from .models import *

import os
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
#from django.contrib.staticfiles import finders

from django.utils.translation import gettext_lazy as _

from django.contrib import messages

# Create your views here.
@login_required
def base(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()
    invoice = Invoice.objects.all()

    # for i in invoice.total_invoice:
    #     i = i + 0

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
    }

    return render(request, "invoice/base/base.html", context)


# Product view
@permission_required('invoice.add_product')
def create_product(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = ProductForm()

    if request.method == "POST":
        product = ProductForm(request.POST)
        if product.is_valid():
            
            product.save()
            messages.success(request, 'Producto Guardado')
            return redirect("create_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/create_product.html", context)

@permission_required('invoice.view_product')
def view_product(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.filter(product_is_delete=False)

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/view_product.html", context)


# Customer view
@permission_required('invoice.add_customer')
def create_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = CustomerForm()

    if request.method == "POST":
        customer = CustomerForm(request.POST)
        if customer.is_valid():
            customer.save()
            return redirect("create_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/create_customer.html", context)

@permission_required('invoice.view_customer')
def view_customer(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/view_customer.html", context)


# Invoice view
@login_required
def create_invoice(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    form = InvoiceForm()
    formset = InvoiceDetailFormSet()
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        formset = InvoiceDetailFormSet(request.POST)
        if form.is_valid():
            invoice = Invoice.objects.create(
                customer=form.cleaned_data.get("customer"),
                date=form.cleaned_data.get("date"),
            )
        if formset.is_valid():
            total = 0
            for form in formset:
                product = form.cleaned_data.get("product")
                amount = form.cleaned_data.get("amount")
                if product and amount:
                    # Sum each row
                    sum = float(product.product_price) * float(amount)
                    # Sum of total invoice
                    total += sum
                    InvoiceDetail(
                        invoice=invoice, product=product, amount=amount
                    ).save()
            # Pointing the customer
            points = 0
            if total > 1000:
                points += total / 1000
            invoice.customer.customer_points = round(points)
            # Save the points to Customer table
            invoice.customer.save()

            # Save the invoice
            invoice.total = total
            invoice.save()
            return redirect("view_invoice")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "form": form,
        "formset": formset,
    }

    return render(request, "invoice/create_invoice.html", context)

@permission_required('invoice.view_invoice')
def view_invoice(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "invoice": invoice,
    }

    return render(request, "invoice/view_invoice.html", context)


# Detail view of invoices
@permission_required('invoice.view_invoice_detail')
def view_invoice_detail(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        # 'invoice': invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/view_invoice_detail.html", context)


# Delete invoice
@permission_required('invoice.delete_invoice')
def delete_invoice(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    invoice = Invoice.objects.get(id=pk)
    invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
    if request.method == "POST":
        invoice_detail.delete()
        invoice.delete()
        return redirect("view_invoice")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "invoice": invoice,
        "invoice_detail": invoice_detail,
    }

    return render(request, "invoice/delete_invoice.html", context)


# Edit customer
@permission_required('invoice.edit_customer')
def edit_customer(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.get(id=pk)
    form = CustomerForm(instance=customer)

    if request.method == "POST":
        customer = CustomerForm(request.POST, instance=customer)
        if customer.is_valid():
            customer.save()
            return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": form,
    }

    return render(request, "invoice/create_customer.html", context)


# Delete customer
@permission_required('invoice.delete_customer')
def delete_customer(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    customer = Customer.objects.get(id=pk)

    if request.method == "POST":
        customer.delete()
        return redirect("view_customer")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "customer": customer,
    }

    return render(request, "invoice/delete_customer.html", context)


# Edit product
@permission_required('invoice.edit_customer')
def edit_product(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.get(id=pk)
    form = ProductForm(instance=product)

    if request.method == "POST":
        customer = CustomerForm(request.POST, instance=product)
        if customer.is_valid():
            product.save()
            return redirect("view_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": form,
    }

    return render(request, "invoice/create_product.html", context)


# Delete product
@permission_required('invoice.delete_product')
def delete_product(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    product = Product.objects.get(id=pk)

    if request.method == "POST":
        product.product_is_delete = True
        product.save()
        return redirect("view_product")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "product": product,
    }

    return render(request, "invoice/delete_product.html", context)


# iniciar sesion
def iniciarSesion(request):
    return redirect("login")

# registrar 
# def registrar(request):
#     return render(request, 'invoice/registrar.html')

#@permission_required('invoice.add_user')
def registrar(request):

    if request.method == 'GET':
        return render(request, 'invoice/registrar.html', {
            'form': UserCreationForm
        }) 
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('ver_usuarios')
            except IntegrityError:
                return render(request, 'invoice/registrar.html', {
                    'form': UserCreationForm, 
                    'error': 'user already exists'
                }) 
             
        return render(request, 'invoice/registrar.html', {
                    'form': UserCreationForm, 
                    'error': 'Password do no match'
        }) 


@permission_required('invoice.view_user')
def ver_usuarios(request):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    usuarios = User.objects.all()

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "usuarios": usuarios,
    }

    return render(request, "invoice/ver_usuarios.html", context)


# Delete usuario
@permission_required('invoice.delete_user')
def eliminar_usuario(request, pk):
    total_product = Product.objects.count()
    total_customer = Customer.objects.count()
    total_invoice = Invoice.objects.count()

    usuario = User.objects.get(id=pk)

    if request.method == "POST":
        usuario.delete()
        return redirect("ver_usuarios")

    context = {
        "total_product": total_product,
        "total_customer": total_customer,
        "total_invoice": total_invoice,
        "usuario": usuario,
    }

    return render(request, "invoice/eliminar_usuario.html", context)



#class SaleFacturaPdf(View):
    
 #   def get(self, request, *args, **kwargs):
  #      return HttpResponse('Hello, World')

def generar_pdf(request, pk):
    try:
        template = get_template('invoice/view_reportpfd.html')
        invoice = Invoice.objects.get(id=pk)
        invoice_detail = InvoiceDetail.objects.filter(invoice=invoice)
        context = {
            'factura': invoice.id,
            'cliente': invoice.customer,
            'fecha': invoice.date,
            'comp': {'name': 'Mi Tienda', 'ruc': '344754238694', 'address': 'Sucre - Bolivia'},
            "invoice_detail": invoice_detail,
            "iva": invoice.total*0.13,
            "total_invoice": invoice.total,
            "total": invoice.total + invoice.total*0.13,
        }
        html = template.render(context)
        response = HttpResponse(content_type='application/pdf')
        #response['Content-Disposition'] = 'attachment; filename="report.pdf'
        pisaStatus = pisa.CreatePDF(
            html, dest=response)
        #if pisaStatus.err:
         #   return HttpResponse('We had some errors <pre>' + html+ '</pre>')
        return response
    except:
        pass
    return HttpResponse('Error al crear la factura')