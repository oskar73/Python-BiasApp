from django.db import models

class FinancialInstrument(models.Model):
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()
    date_joined = models.DateTimeField(auto_now_add=True)
    # Add more fields as needed

class HistoricalData(models.Model):
    instrument = models.ForeignKey(FinancialInstrument, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    opening_price = models.DecimalField(max_digits=10, decimal_places=2)
    closing_price = models.DecimalField(max_digits=10, decimal_places=2)
    min_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.instrument} - {self.date} {self.time}"
