from django.db import models


# Create your models here.
class MutualFunds(models.Model):
    """
    Store mutual fund ID and name
    """
    isin = models.CharField(max_length=70, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ['isin', 'name']

    def __str__(self):
        return self.isin


class PriceData(models.Model):
    """
    Store the price data of mutual fund
    """
    fk_mutual_fund = models.ForeignKey('MutualFunds', on_delete=models.CASCADE)
    date = models.DateTimeField()
    price = models.FloatField()

    class Meta:
        unique_together = ['fk_mutual_fund', 'date']
