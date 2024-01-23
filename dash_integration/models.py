from django.db import models
from datetime import datetime

class FinancialInstrument(models.Model):
    file = models.FileField(upload_to='csvs/')
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    class Meta:
        db_table = 'bias_app_FinancialInstrument'
    def __str__(self):
        return self.symbol
        

class HistoricalData(models.Model):
    instrument = models.ForeignKey(FinancialInstrument, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    date = models.DateField()
    time = models.TimeField()
    opening_price = models.FloatField()
    closing_price = models.FloatField()
    min_price = models.FloatField()
    max_price = models.FloatField()
    volume = models.FloatField()
    
    class Meta:
        ordering=('datetime',)

    def __str__(self):
        return self.instrument.symbol
    