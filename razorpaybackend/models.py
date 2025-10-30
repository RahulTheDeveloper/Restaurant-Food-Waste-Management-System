from django.db import models

# Create your models here.
class Transaction(models.Model):
    payment_id = models.CharField(max_length=100, verbose_name="Payment ID")
    order_id = models.CharField(max_length=100, verbose_name="Order ID")
    signature = models.CharField(max_length=100, verbose_name="Signature")
    amount = models.IntegerField(verbose_name="Amount")
    
    def __str__(self):
        return str(self.id)
    