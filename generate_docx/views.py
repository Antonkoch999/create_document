from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.mail import EmailMessage

import datetime
import mammoth

from docxtpl import DocxTemplate
from .сhange_number_to_words import num2text
from . import forms
from . import models


class MyLoginView(LoginView):
    """Change the shape to add recaptcha."""

    form_class = forms.MyAuthenticationForm


def register(request):
    """Registration new users."""
    if request.method == 'POST':
        user_form = forms.UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            return render(request, 'register_done.html', {'new_user': new_user})
    else:
        user_form = forms.UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


@login_required(login_url="/login/")
def start_page(request):
    """View start page with clients."""
    clients = models.Client.objects.all()
    return render(request, 'start_page.html', {'clients': clients})


@login_required(login_url="/login/")
def create_documents(request, id_):
    """Generate new document.

    Receives a data for template depending on client and gets data from a form,
    then replaces the data in the template and sends it to the mail,
    then outputs the HTML code of the generated template.
    """
    client = get_object_or_404(models.Client, id=id_)
    doc = DocxTemplate("./template_documents/template_for_24.docx")
    if request.method == 'POST':
        form = forms.InputTextForms(request.POST)
        if form.is_valid():
            penny_in_the_cost = -2  # Magic number
            second_last_number_in_the_cost = -5  # Magic number
            this_number_for_slice = -3  # Magic number
            if form.cleaned_data['cost'][second_last_number_in_the_cost:this_number_for_slice] in \
                    ['01', '21', '31', '41', '51', '61', '71', '81', '91']:
                rubles = 'рубль'
            elif form.cleaned_data['cost'][second_last_number_in_the_cost:this_number_for_slice] in \
                    ['02', '03', '04', '22', '23', '24', '32', '33', '34', '42', '43', '44',
                     '52', '53', '54', '62', '63', '64', '72', '73', '74', '82', '83', '84',
                     '92', '93', '94']:
                rubles = 'рубля'
            else:
                rubles = 'рублей'

            if form.cleaned_data['cost'][penny_in_the_cost:] in \
                    ['01', '21', '31', '41', '51', '61', '71', '81', '91']:
                penny = 'копейка'
            elif form.cleaned_data['cost'][penny_in_the_cost:] in \
                    ['02', '03', '04', '22', '23', '24', '32', '33', '34', '42', '43', '44',
                     '52', '53', '54', '62', '63', '64', '72', '73', '74', '82', '83', '84',
                     '92', '93', '94']:
                penny = 'копейки'
            else:
                penny = 'копеек'
            context = {'number_document': form.cleaned_data['number_document'],
                       'data_creation': form.cleaned_data['data_creation'].replace('/', '.'),
                       "name_of_work": form.cleaned_data['name_of_work'],
                       'count_hours': form.cleaned_data['count_hours'],
                       'cost': form.cleaned_data['cost'].replace(',', '.'),
                       'rubles': rubles,
                       'penny_cost': form.cleaned_data['cost'][penny_in_the_cost:],
                       'penny': penny,
                       'cost_words': str(num2text(float(form.cleaned_data['cost'].replace(',', '.')))),
                       'number_of_contract': str(client.number_of_contract),
                       'date_contract': str(client.date_of_contract),
                       'city': str(client.city),
                       'name_of_organization': str(client.name_of_organization),
                       'in_face': str(client.in_face),
                       'name_face_organizations': str(client.name_face_organizations),
                       'acting_on_the_basic': str(client.acting_on_the_basis),
                       'legal_address': str(client.legal_address),
                       'address_of_bank': str(client.address_of_bank),
                       'unp': str(client.unp),
                       'initials': str(client.initials),
                       'in_face_in_nominative': str(client.in_face_in_nominative),
                       'phone_number': str(client.phone_number),
                       'email': str(client.email),
                       }
            doc.render(context)
            doc.save(f'./documents/{form.cleaned_data["data_creation"].replace("/", ".")}-Act{form.cleaned_data["number_document"]}.docx')
            # email = EmailMessage(
            #     'Hello',
            #     f'Акт№{form.cleaned_data["number_document"]}',
            #     'anton.kisialiou@gmail.com',
            #     ['anton.kisialiou@gmail.com'],
            # )
            # email.attach_file(f'./documents/{form.cleaned_data["data_creation"]}-Акт№{form.cleaned_data["number_document"]}.docx')
            # email.send()

            html = mammoth.convert_to_html(f'./documents/{form.cleaned_data["data_creation"].replace("/", ".")}-Act-{form.cleaned_data["number_document"]}.docx').value
            data = form.cleaned_data["data_creation"].replace("/", ".")
            number = form.cleaned_data["number_document"]
            return render(request, 'docx.html', {'file': html, 'data': data, 'number': number})
    else:
        form = forms.InputTextForms()
    return render(request, 'detail.html', {'form': form, 'client': client})


@login_required(login_url="/login/")
def create_client(request):
    """Create new client."""
    if request.method == 'POST':
        form = forms.CreateClientForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('../..')
    form = forms.CreateClientForm()
    return render(request, 'create_client.html', {'form': form})


# def input_form(request):
#     #TODO Adding path file
#     doc = DocxTemplate("/home/anton/snap/kisa/template_documents/template_for_24.docx")
#     if request.method == 'POST':
#         form = forms.InputTextForms(request.POST)
#         if form.is_valid():
#             context = {'number_document': form.cleaned_data['number_document'],
#                        'data_creation': form.cleaned_data['data_creation'],
#                        "name_of_work": form.cleaned_data['name_of_work'],
#                        'count_hours': form.cleaned_data['count_hours'],
#                        'cost': form.cleaned_data['cost'],
#                        'cost_words': str(num2text(float(form.cleaned_data['cost'])))}
#             doc.render(context)
#             #TODO Adding path save file
#             doc.save(f'/home/anton/snap/kisa/documents/{datetime.date}/{form.cleaned_data["data_creation"]}-Акт№{form.cleaned_data["number_document"]}.docx')
#             return HttpResponseRedirect('./')
#     else:
#         form = forms.InputTextForms()
#     return render(request, 'input.html', {'form': form})
