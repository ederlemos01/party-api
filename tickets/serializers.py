from rest_framework import serializers
from .models import TicketType
from .validators import validate_start_end,validate_quantity_gte_max_user,validate_max_user_gte_max_order,validate_max_order_gte_min_order

class CreateTicketTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = TicketType
        fields = ['id','event','title','description','price','quantity','min_quantity_per_order',
                  'max_quantity_per_order','max_quantity_per_user','sales_start_at',
                  'sales_end_at','absorb_fee']
        read_only_fields = ['id','event']
        validators = [
            validate_start_end,
            validate_quantity_gte_max_user,
            validate_max_user_gte_max_order,
            validate_max_order_gte_min_order
        ]

class RetrieveTicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketType
        fields = ['id','title','description','price','sales_end_at','min_quantity_per_order','max_quantity_per_order']
        read_only_fields =  ['id','title','description','price','sales_end_at','min_quantity_per_order','max_quantity_per_order']

