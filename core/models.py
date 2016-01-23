import moneyed
from djmoney.models.fields import MoneyField
from moneyed import Money
from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    type_choices = (
        ('SU', 'Superuser'), ('I', 'Instructor'), ('S', 'Student'))
    user_type = models.CharField(
        max_length=2, choices=type_choices,  default='S')


class Instructor(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)


class Period(models.Model):
    name = models.CharField(max_length=40)
    instructor = models.ForeignKey(Instructor)
    payscale = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')
    average_adjust = models.IntegerField()

    def class_average(self):
        if self.student_set.count() == 0:
            return 0
        else:
            cash = self.student_set.values_list('cash', flat=True)
            return Money(
                sum(cash) / len(cash) + (self.average_adjust or 0), 'USD')

    def pay_students(self):
        for student in self.student_set.all():
            student.cash += self.payscale
            student.save()

    def richest(self):
        return self.students.all().order_by('-cash').first()

    def total_bonuses(self):
        return Money(
            sum(self.periodbonus_set.values_list('amount', flat=True)), 'USD')


class Student(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE)
    period = models.ForeignKey(Period)
    cash = MoneyField(max_digits=10, decimal_places=2, default_currency='USD')

    def well_behaved(self):
        if self.behavior_set.last() and self.behavior_set.last().well_behaved:
            return True
        else:
            return False

# Transaction Models
class BaseTransaction(models.Model):
    date = models.DateField()
    reason = models.TextField()
    sender = models.ForeignKey(MyUser)
    amount = MoneyField(
        max_digits=10, decimal_places=2, default_currency='USD')

    class Meta:
        abstract = True

class Transaction(BaseTransaction):
    recipient = models.ForeignKey(Student)

class StudentBonus(BaseTransaction):
    student = models.ForeignKey(Student)

    def save(self, *args, **kwargs):
        self.student.cash -= self.amount
        self.student.save()
        super(StudentBonus, self).save(*args, **kwargs)

class PeriodBonus(BaseTransaction):
    period = models.ForeignKey(Period)

    def distribute_bonus(self):
        portion = self.amount / self.period.students.count()
        for student in self.period.students:
            student.cash += portion
            student.save()


class Behavior(models.Model):
    student = models.ForeignKey(Student)
    date = models.DateField()
    well_behaved = models.BooleanField()
    current_balance = MoneyField(
        max_digits=10, decimal_places=2, default_currency='USD')


class Job(models.Model):
    name = models.CharField(max_length=80)
    student = models.ForeignKey(Student)
    boss = models.ForeignKey(MyUser, related_name='employees')
    payscale = MoneyField(
        max_digits=10, decimal_places=2, default_currency='USD')
