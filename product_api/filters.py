import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['name', 'price_min', 'price_max', 'category', 'in_stock']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset
