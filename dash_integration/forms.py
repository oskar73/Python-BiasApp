from django import forms
from .models import *

class UploadFileForm(forms.ModelForm):
    file = forms.FileField(label='Upload File', widget=forms.FileInput(attrs={'class': 'form-control', 'id': 'fileformid'}))
    class Meta:
        model = FinancialInstrument
        fields = ('file',)

class HugeStatForm(forms.Form):
    year_range=forms.CharField(required=False, max_length=100, widget=forms.TextInput())
    month_select_all=forms.BooleanField(required=False)
    for i in range(1,13):
        key="month_filter{}".format(i)
        value=forms.BooleanField(required=False)
        locals()[key]=value
        
    day_month_all=forms.BooleanField(required=False)                  
    for i in range(1,32):
        key="days_of_month{}".format(i)
        value=forms.BooleanField(required=False)                    
        locals()[key]=value
    
    days_week_all=forms.BooleanField(required=False)  
    for i in range(1,8):
        key="days_week_filter{}".format(i)
        value=forms.BooleanField(required=False)                    
        locals()[key]=value
        
    hour_range=forms.CharField(required=False, max_length=100, widget=forms.TextInput())
    symbolselector=forms.ChoiceField(required=False,choices=[], widget=forms.Select(attrs={'class': 'form-control form-control-sm mb-3 pb-1'}))
    select_chart=forms.ChoiceField(required=False,choices=[('0','Select chart type'),('line','Line Chart'),('column','Column Chart'),('histogram','Histogram Chart'),], widget=forms.Select())
    series1=forms.BooleanField(required=False)  
    allseries=forms.BooleanField(required=False)  
    select_aggregation=forms.ChoiceField(required=False,choices=[('0','Select aggregation interval'),('1','1 minute'),('5','5 minutes'),('15','15 minutes'),('30','30 minutes'),('60','60 minutes')], widget=forms.Select())
    select_group=forms.ChoiceField(required=False,choices=[('0','Select group'),('HH.MM.DW','HH:MM Day of the Week'),('DM.HH.MM','Day of Month,HH:MM'),('MY.HH.MM','Month of Year,HH:MM'),('Y.HH.MM','Year, HH:MM'),('DW.D','Days of the Week,Day'),('DM.D','Days of Month,Day'),('MY.D','Month of Year,Day'),('D.HH','Day, Hours'),('D.D','Day, Day')], widget=forms.Select())             
    select_units=forms.ChoiceField(required=False,choices=[('0','Select units'),('unit1','Unit 1'),('unit2','Unit 2'),('unit3','Unit 3')], widget=forms.Select())
    select_statistic=forms.ChoiceField(required=False,choices=[('0','Select statistics'),('mean','Mean'),('median','Median'),('std_deviation','Standard Deviation'),('sum','Sum'),('count','Count')], widget=forms.Select())
    select_metric=forms.ChoiceField(required=False,choices=[('0','Select metric'),('close_close_minus_1','Close - Close (-1)'),('close_open_diff','Close - Open'),('high_low_diff','High - Low'),('high_count','High Count'),('low_count','Low Count'),('high_low_sum','High + Low')], widget=forms.Select())
    select_meridian=forms.BooleanField(required=False)  
    
    def __init__(self, *args, **kwargs):
        historical_me = kwargs.pop('historical_me', None)
        super(HugeStatForm, self).__init__(*args, **kwargs)
        if historical_me:
            self.fields['symbolselector'].choices = [(symbol, symbol) for symbol in historical_me]

    
class UploadInfoForm(forms.ModelForm):
    symbol = forms.CharField(label='Symbol', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'symbolformid'}))
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'nameformid'}))
    class Meta:
        model = FinancialInstrument
        fields = ('symbol','name',)
        
'''
class StillDataForm(forms.Form):
    symbol = forms.ChoiceField(choices=[('BTUSD','BTUSD'),('USDEUR','USDEUR'),('GBPEUR','GPBEUR')], widget=forms.Select(attrs={'class': 'form-control'}))
'''

class VisualizeDataForm(forms.Form):
    symbol = forms.ChoiceField(choices=[], widget=forms.Select(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        historical_me = kwargs.pop('historical_me', None)
        super(VisualizeDataForm, self).__init__(*args, **kwargs)
        if historical_me:
            self.fields['symbol'].choices = [(symbol, symbol) for symbol in historical_me]
