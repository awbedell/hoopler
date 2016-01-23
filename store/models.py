import moneyed
from djmoney.models.fields import MoneyField
from django.db import models
from core.models import Student

class StoreItem(models.Model):
    name = models.CharField(max_length=20)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    stock = models.IntegerField(null=True, blank=True)

    def buy(self, student):
        if student.cash >= self.price and (self.stock > 0 or self.stock == None):
            self.purchase_set.create(purchaser=student)
            student.cash -= self.price
            student.save()
            if self.stock:
                self.stock -= 1
                self.save()
        else:
            return False

class Purchase(models.Model):
    purchaser = models.ForeignKey(Student)
    item = models.ForeignKey(StoreItem)
