from common.models import BaseModel
from events.models import Event
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class TicketType(BaseModel):
    event = models.ForeignKey(Event, editable=False,
                                     on_delete=models.CASCADE,related_name='tickets',)
    title = models.CharField(max_length=120)
    description = models.CharField(blank=True,max_length=300)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[
         MinValueValidator(Decimal('0.00'))])
    quantity = models.PositiveSmallIntegerField(validators=[
            MinValueValidator(1),   
            MaxValueValidator(30000)  
        ])
    quantity_reserved = models.PositiveSmallIntegerField(default=0,validators=[
                MaxValueValidator(30000)  
            ])
    quantity_sold = models.PositiveSmallIntegerField(default=0,validators=[
            MaxValueValidator(30000)  
        ])
    min_quantity_per_order =  models.PositiveSmallIntegerField(validators=[
            MinValueValidator(1),   
            MaxValueValidator(100)  
        ])
    max_quantity_per_order =  models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),   
                MaxValueValidator(100)  
            ])
    max_quantity_per_user = models.PositiveSmallIntegerField(validators=[
                MinValueValidator(1),   
                MaxValueValidator(100)  
            ])
    sales_start_at = models.DateTimeField()
    sales_end_at = models.DateTimeField()
    absorb_fee = models.BooleanField(default=False)

    @property
    def is_free(self):
         return self.price == 0

    class Meta(BaseModel.Meta):
        constraints = [
                    models.CheckConstraint(condition=models.Q(sales_end_at__gt=models.F('sales_start_at')), 
                                             name='sales_end_after_start'),
                    models.CheckConstraint(condition=models.Q(max_quantity_per_order__gte=models.F('min_quantity_per_order')), 
                                            name='max_order_quantity_gte_min'),
                    models.CheckConstraint(condition=models.Q(quantity__gte=models.F('quantity_sold')), 
                                            name='quantity_gte_quantity_sold'),
                    models.CheckConstraint(price__gte=0),
                    models.CheckConstraint(condition=models.Q(quantity_gte=models.F('max_quantity_per_user')),
                                           name='quantity_gte_max_quantity_per_user'),
                    models.CheckConstraint(condition=models.Q(quantity_gte=models.F('max_quantity_per_order')),
                                           name='quantity_gte_max_quantity_per_order')]

    def __str__(self):
            return f'{self.title} - {self.price}'