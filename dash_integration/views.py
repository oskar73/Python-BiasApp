from django.shortcuts import render, redirect
#Django Stuff
from django.views import View
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse
#from dash_integration.dash_app import app
#Dash Stuff
from django_plotly_dash import DjangoDash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import Dash, html, dcc, callback, Output, Input

import pandas as pd
import os
from bias_app import settings
from .forms import *
from .models import *
from bias_app.models import User

from datetime import datetime



#https://en.wikipedia.org/wiki/Security_theater
#https://forum.djangoproject.com/t/how-to-allow-only-certain-devices-to-access-django-web-aplication/14819/16

#https://www.alphavantage.co/documentation/
#https://alpha-vantage.readthedocs.io/en/latest/#community-pulse


class UserCheck(View):
    '''Responsable to indicate the way to the Offline Analysis' '''	
    template_name='charts/usercheck.html'

    def get(self, request,page=1):
        user=request.user
        if user.is_authenticated:
            hd = User.objects.all()
            paginator = Paginator(hd, per_page=6)
            page_object = paginator.get_page(page)
            context = {"page_obj": page_object}
            return render(request,self.template_name, context)
        return redirect('home')
    
class DataLook(View):
    '''Responsable to indicate the way to the Offline Analysis' '''	
    form_class=VisualizeDataForm
    template_name='charts/datalook.html'

    def get(self, request,stock,page):
        user=request.user
        if user.is_authenticated:
            hd = HistoricalData.objects.filter(instrument__symbol=stock)
            paginator = Paginator(hd, per_page=6)
            page_object = paginator.get_page(page)
            context = {"page_obj": page_object}
            return render(request,self.template_name, context)
        return redirect('home')

class DataMinus(View):
    '''Responsable to indicate the way to the Offline Analysis' '''	
    form_class=VisualizeDataForm
    template_name='charts/dataminus.html'
    api_key = 'I0T0AM1MH4Y4X0DC'

    def get(self, request):
        user=request.user
        if user.is_authenticated:
            historical_me=FinancialInstrument.objects.all()
            form = self.form_class(historical_me=historical_me)
            return render(request,self.template_name, {'form':form,'historical_me':historical_me,'new_symbol':'BTUSD'})
        return redirect('home')
        
    def post(self, request, *args, **kwargs):
        user=request.user
        form = self.form_class(request.POST, historical_me=FinancialInstrument.objects.all())
        if form.is_valid():
            if user.is_authenticated:
                new_symbol=form.cleaned_data['symbol']
                new_symbol=new_symbol
                historical=HistoricalData.objects.filter(instrument__symbol=new_symbol)[:5]
                return render(request,self.template_name, {'form':form, 'historical':historical,'new_symbol':new_symbol})
            return redirect('home')
        messages.error(request, 'Your form is invalid')
        return redirect('dash_integration:dataminus')


class DataPlus(View):
    form_class = UploadFileForm
    second_form_class = UploadInfoForm
    template_name = 'charts/dataplus.html'
    api_key = 'I0T0AM1MH4Y4X0DC'
    
    def get(self, request):
        form = self.form_class()
        second_form = self.second_form_class()
        user=request.user
        if user.is_authenticated:
            return render(request, self.template_name, {'form': form, 'second_form': second_form})
        return redirect('home')
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        second_form = self.second_form_class(request.POST)
        
        if form.is_valid():
            user=request.user
            if user.is_authenticated:
                file = request.FILES['file']
                if file.name.endswith('.txt'):
                    chunk_size = 100  # Adjust the chunk size as needed
                    chunks = pd.read_csv(file, header=None, dtype=str, chunksize=chunk_size, nrows=100)
                    table_html = ''
                    for chunk in chunks:
                        table_html += chunk.to_html(header=False, index=False, classes='table table-striped')
                    
                    request.session['file_uploaded'] = file.name
                    file_path = os.path.join(settings.MEDIA_ROOT, 'csvs', file.name)
                    with open(file_path, 'wb') as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    request.session['file_uploaded'] = file_path
                    messages.success(request, 'Your file was uploaded successfully...')
                    return render(request, self.template_name, {'form': form, 'second_form': second_form, 'table_html':table_html})
                else:
                    messages.error(request, 'Invalid file format. Please upload a .txt or .csv file.')
                    return redirect('dash_integration:dataplus')
            return redirect('home')
        
        elif second_form.is_valid():
            symbol = second_form.cleaned_data['symbol']
            name = second_form.cleaned_data['name']
            file = request.session.get('file_uploaded')
            
            #Here we create a function that is capable of adding values to the database without errors and interruptions
            @transaction.atomic
            def create_objects(objects_to_create):
                HistoricalData.objects.bulk_create(objects_to_create)
                
            if file:
                data_uploaded = FinancialInstrument(symbol=symbol, name=name, file=file)
                file_path = os.path.join(settings.MEDIA_ROOT, 'csvs', file)
                try:
                    df = pd.read_csv(file_path, header=None, dtype=str, skiprows=1)
                except Exception as e:
                    messages.error(request, f"Error reading file: {str(e)}")
                    return redirect('dash_integration:dataplus')
                #We need to be sure that we are going to create a symbol that does not exist already.
                data_uploaded_testing=FinancialInstrument.objects.filter(symbol=symbol)
                if data_uploaded_testing.exists():
                    #This code ensures that we only update the file if the symbol already exists 
                    #As we don't want errors in our app, we get the first rather than considering that 
                    #There realy isn't any duplicate symbol yet, allthought we should not accept this possibility
                    data_uploaded=FinancialInstrument.objects.filter(symbol=symbol).first()
                    data_uploaded.file=file
                    data_uploaded.save()
                #Otherwise, we only create a new symbol and proceed with the code logic:
                data_uploaded.save()
                #Here we are trying to create bulk objects to speed up the proccess, we tryed a number equivalent to 1 month in minutes
                batch_size=43830
                objects_to_create=[]
                total_lines = len(df)
                progress = 0
                for index, row in df.iterrows():
                    #print ("here are the fields",row)
                    date_str=row[0]
                    time_str=row[1]
                    date_str = datetime.strptime(date_str, '%m/%d/%Y').date()
                    time_object = datetime.strptime(time_str, '%H:%M').time()
                    historical_data = HistoricalData(
                        instrument=data_uploaded,
                        date=date_str,
                        time=time_object,
                        datetime=datetime.combine(date_str, time_object),
                        opening_price=float(row[2]),
                        max_price=float(row[3]),
                        min_price=float(row[4]),
                        closing_price=float(row[5]),
                        volume=int(row[6])+int(row[7])
                    )
                    #This approach is going to create 1750 objs at a time.
                    progress = (index + 1) / total_lines * 100
                    objects_to_create.append(historical_data)
                    if len(objects_to_create) >= batch_size or index == total_lines - 1:                        
                        create_objects(objects_to_create)
                        print("________________Total objects already created:",HistoricalData.objects.filter(instrument=data_uploaded).count())
                        objects_to_create = []
                    request.session['progress'] = progress
                #We ensure that no object stays behind.
                if objects_to_create:
                    create_objects(objects_to_create)
                    #historical_data.save()
                
                messages.success(request, 'Your Stock Object was added successfully')
                return JsonResponse({'success': True})
            else:
                messages.error(request, 'File data is missing. Please upload a file first.')
                return redirect('dash_integration:dataplus')
        else:
            messages.error(request, 'Form validation failed. Please check your input.')
            return redirect('dash_integration:dataplus')
class Online(View):
    '''Responsable to indicate the way to the Online Analisys' '''	
    form_class=HugeStatForm
    template_name='charts/online.html'
    api_key = 'I0T0AM1MH4Y4X0DC'

    def get(self, request):
        user=request.user
        form = self.form_class    
        historical_me=FinancialInstrument.objects.all()
        retrive=HistoricalData.objects.filter(instrument__symbol="BTUSD").order_by('datetime')
        fields=retrive.values('instrument','datetime','opening_price','closing_price','min_price','max_price','volume')
        df=pd.DataFrame.from_records(fields)
        sheet=[dbc.themes.BOOTSTRAP]
        app = DjangoDash(name='dash_app_online', external_stylesheets=sheet)
        app.layout = html.Div([
        dcc.Input(id='my-input',
                    value='hello'),
        dcc.Slider(0,20,5, value=10,
                    id='slider'),
        html.Div(id='my-output1'),
        html.Div(id='my-output2')
        ])
        @app.callback(
        Output('my-output1','children'),
        Output('my-output2','children'),
        Input('slider','value'),
        Input('my-input','value')
        )
        def update_out(slider,input_v):
            return input_v, str(slider)
        if user.is_authenticated:
            return render(request,self.template_name, {'form':form,})
        return redirect('home')
    
    def post(self, request, *args, **kwargs):
        user=request.user
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            if user.is_authenticated:
                form.save()
                return redirect('dash_integration:online')
            return redirect('home')
        return render(request,self.template_name, {'form':form})


class Offline(View):
    '''Responsable to indicate the way to the Online Analisys '''	
    template_name='charts/offline.html'

    def get(self, request):
        user=request.user
        if user.is_authenticated:
            return render(request,self.template_name)
        return redirect('home')
