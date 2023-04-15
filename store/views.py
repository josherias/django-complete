from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from store.pagination import DefaultPagination
from .filters import ProductFilter
from .models import OrderItem, Product, Collection, Review
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    # filtering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    
    # pagination settings - page number -settings  
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'last_updated']
             
    def get_serializer_context(self):
        return {'request' : self.request}
 
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error' : 'Product cannot be deleted, its associated with an orderitem'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
 
    

class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    
    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']).count() > 0:
            return Response({'error' : 'Collection cannot be deleted beacuse its associated with products'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
        

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    
    # overide default method to prevenyt returning all reviews on each product
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    
    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}
    