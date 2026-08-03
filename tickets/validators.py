from rest_framework import serializers

def validate_start_end(attrs):
    sales_start_at = attrs.get('sales_start_at')
    sales_end_at = attrs.get('sales_end_at')

    if sales_start_at and sales_end_at:
        if sales_start_at >= sales_end_at:
            raise serializers.ValidationError({
                "sales_start_at": "Esta data não pode ser maior ou igual ao término.",
                "sales_end_at": "A data de término deve ser posterior à data de início."
            })

def validate_quantity_gte_max_user(attrs):
    quantity = attrs.get('quantity')
    max_quantity_per_user = attrs.get('max_quantity_per_user')
     
    if quantity is not None and max_quantity_per_user is not None:
        if quantity < max_quantity_per_user:
            raise serializers.ValidationError({
                "quantity": "A quantidade de ingressos tem que ser maior que a quantidade máxima por usuário.",
                "max_quantity_per_user": "A quantidade de ingressos tem que ser maior que a quantidade máxima por usuário."
            })

def validate_max_user_gte_max_order(attrs):
    max_quantity_per_user = attrs.get('max_quantity_per_user')
    max_quantity_per_order = attrs.get('max_quantity_per_order')
     
    if max_quantity_per_order is not None and max_quantity_per_user is not None:
        if max_quantity_per_user < max_quantity_per_order:
            raise serializers.ValidationError({
                "max_quantity_per_user": "A quantidade máxima por usuário tem que ser maior ou igual à quantidade máxima por pedido.",
                "max_quantity_per_order": "A quantidade máxima por usuário tem que ser maior ou igual à quantidade máxima por pedido."
            })

def validate_max_order_gte_min_order(attrs):
    max_quantity_per_order = attrs.get('max_quantity_per_order')
    min_quantity_per_order = attrs.get('min_quantity_per_order')
     
    if max_quantity_per_order is not None and min_quantity_per_order is not None:
        if max_quantity_per_order < min_quantity_per_order:
            raise serializers.ValidationError({
                "max_quantity_per_order": "A quantidade máxima por pedido tem que ser maior ou igual à quantidade mínima.",
                "min_quantity_per_order": "A quantidade máxima por pedido tem que ser maior ou igual à quantidade mínima."
            })