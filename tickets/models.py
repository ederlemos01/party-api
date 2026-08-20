from common.models import BaseModel
from events.models import Event
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid
from django.contrib.auth import get_user_model
authuser = get_user_model()

class TicketType(BaseModel):
    event = models.ForeignKey(Event, editable=False,
                                     on_delete=models.CASCADE,related_name='ticket_types',)
    title = models.CharField(max_length=120)
    description = models.CharField(blank=True,max_length=300)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0, validators=[
         MinValueValidator(Decimal('0.00'))
         ])
    quantity = models.PositiveSmallIntegerField(validators=[
            MinValueValidator(1),   
            MaxValueValidator(30000)  
        ])
    quantity_reserved = models.PositiveSmallIntegerField(default=0,validators=[
            MinValueValidator(0),  
            MaxValueValidator(30000)  
            ])
    quantity_sold = models.PositiveSmallIntegerField(default=0,validators=[
            MinValueValidator(0),
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
         return self.price == Decimal('0.00')

    @property
    def available_quantity(self):
         return self.quantity - self.quantity_sold - self.quantity_reserved

    class Meta(BaseModel.Meta):
        constraints = [
                    models.CheckConstraint(condition=models.Q(sales_end_at__gt=models.F('sales_start_at')), 
                                             name='sales_end_after_start'),
                    models.CheckConstraint(condition=models.Q(max_quantity_per_order__gte=models.F('min_quantity_per_order')), 
                                            name='max_order_quantity_gte_min'),
                    models.CheckConstraint(condition=models.Q(quantity__gte=models.F('quantity_sold')), 
                                            name='quantity_gte_quantity_sold'),
                    models.CheckConstraint(condition=models.Q(quantity__gte=models.F('max_quantity_per_user')),
                                           name='quantity_gte_max_quantity_per_user'),
                    models.CheckConstraint(condition=models.Q(quantity__gte=models.F('max_quantity_per_order')),
                                           name='quantity_gte_max_quantity_per_order'),
                    models.CheckConstraint(condition=models.Q(quantity__gte=models.F('quantity_reserved') + models.F('quantity_sold')),
                                            name='quantity_gte_reserved_plus_sold')]

    def __str__(self):
            return f'{self.title} - {self.price}'



class TicketStatusChoices(models.TextChoices):
        VALID = 'VALID', 'Válido'
        CANCELLED = 'CANCELLED', 'Cancelado'
        USED = 'USED', 'Utilizado'

class Ticket(BaseModel):
    holder = models.ForeignKey(authuser,editable=True, on_delete=models.PROTECT,related_name='tickets')
    ticket_type = models.ForeignKey(TicketType,editable=False,on_delete=models.PROTECT,related_name='tickets')
    order = models.ForeignKey("orders.Order",editable=False,on_delete=models.PROTECT,related_name='tickets')
    status = models.CharField(max_length=20,choices=TicketStatusChoices.choices,default=TicketStatusChoices.VALID)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    checked_in_by = models.CharField(max_length=100,blank=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)


    class Meta(BaseModel.Meta):
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(status=TicketStatusChoices.USED) | models.Q(checked_in_at__isnull=False),
                name='checkin_consistency'
            )
        ]

    @property
    def attend_name(self):
         return self.holder.get_full_name()

    @property
    def attend_email(self):
             return self.holder.email

    def __str__(self):
          return f'{self.attend_email} - {self.ticket_type}'