from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.mail import EmailMessage
from django.core.mail import BadHeaderError
from django.http import FileResponse

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
            cost = form.cleaned_data['cost'].replace('\xa0', '')
            context = {'number_document': form.cleaned_data['number_document'],
                       'data_creation': form.cleaned_data['data_creation'].replace('/', '.'),
                       "name_of_work": form.cleaned_data['name_of_work'],
                       'count_hours': form.cleaned_data['count_hours'],
                       'cost': cost.replace(',', '.'),
                       'rubles': rubles,
                       'penny_cost': form.cleaned_data['cost'][penny_in_the_cost:],
                       'penny': penny,
                       'cost_words': str(num2text(float(cost.replace(',', '.')))),
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
            if not form.cleaned_data['name_of_document']:
                doc.save(f'./documents/{form.cleaned_data["data_creation"].replace("/", ".")}-Act-{form.cleaned_data["number_document"]}.docx')
                html = mammoth.convert_to_html(f'./documents/{form.cleaned_data["data_creation"].replace("/", ".")}-Act-{form.cleaned_data["number_document"]}.docx').value
                models.FileClient.objects.create(
                    date_creation=form.cleaned_data['data_creation'],
                    number_document=form.cleaned_data['number_document'],
                )
            else:
                doc.save(f'./documents/{form.cleaned_data["name_of_document"]}.docx')
                html = mammoth.convert_to_html(f'./documents/{form.cleaned_data["name_of_document"]}.docx').value
                models.FileClient.objects.create(
                    date_creation=form.cleaned_data['data_creation'],
                    number_document=form.cleaned_data['number_document'],
                    name_of_document=form.cleaned_data['name_of_document'],
                )

            name_of_document = form.cleaned_data['name_of_document']
            data = form.cleaned_data["data_creation"].replace("/", ".")
            number = form.cleaned_data["number_document"]
            return render(request, 'docx.html', {'file': html, 'data': data, 'number': number, 'form': form, 'name_of_document': name_of_document})
    else:
        form = forms.InputTextForms()
    return render(request, 'detail.html', {'form': form, 'client': client})


def send_mail(request):
    """Receive data from the last file and sends it to mail."""
    file = models.FileClient.objects.last()
    if request.method == "POST":
        form = forms.SendMailForm(request.POST)
        if form.is_valid():
            if file:
                email = EmailMessage(
                    f'{form.cleaned_data["topic"]}',
                    f'{form.cleaned_data["text"]}',
                    f'{form.cleaned_data["email"]}',
                    [f'{form.cleaned_data["email"]}'],
                )
                if not file.name_of_document:
                    email.attach_file(f'./documents/{file.date_creation}-Act-{file.number_document}.docx')
                else:
                    email.attach_file(f'./documents/{file.name_of_document}.docx')
                try:
                    email.send()
                except BadHeaderError:
                    return HttpResponse('Message not sent')
                return render(request, 'send_done.html')
    else:
        form = forms.SendMailForm()
    return render(request, 'send.html', {'form': form})


def download_file(request):
    file = models.FileClient.objects.last()
    if not file.name_of_document:
        _file = f'./documents/{file.date_creation}-Act-{file.number_document}.docx'
    else:
        _file = f'./documents/{file.name_of_document}.docx'
    response = FileResponse(open(_file, 'rb'))
    return response


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


import os

from optparse import OptionParser

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep

def screenshot(request):
    CHROME_PATH = '/usr/bin/google-chrome'
    CHROMEDRIVER_PATH = '/usr/bin/chromedriver'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH
    if request.method == "POST":
        form = forms.ScreenshotForm(request.POST)
        if form.is_valid():
            driver = webdriver.Chrome(
                executable_path=CHROMEDRIVER_PATH,
                chrome_options=chrome_options
            )
            driver.get(form.cleaned_data['link'])
            driver.save_screenshot(f"./screenshot/{form.cleaned_data['name_of_photo']}.png")
            driver.close()
            name_of_photo = form.cleaned_data['name_of_photo']
            return render(request, 'get_photo.html', {'form': form, 'name_of_photo': name_of_photo})
    form = forms.ScreenshotForm()
    return render(request, 'link.html', {'form': form})
