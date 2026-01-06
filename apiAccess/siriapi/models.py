from django.db import models


class Expense(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=80)
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}: ${self.amount}"


class SiriRequest(models.Model):
    request_id = models.CharField(max_length=255, unique=True)
    endpoint = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request_id', 'endpoint')

    def __str__(self):
        return f"{self.endpoint}: {self.request_id}"


class Budget(models.Model):
    period = models.CharField(max_length=7)  # YYYY-MM
    category = models.CharField(max_length=80, blank=True, default="")  # if blank, overall budget
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('period', 'category')

    def __str__(self):
        cat = self.category or "Overall"
        return f"{cat} Budget for {self.period}: ${self.amount}"
