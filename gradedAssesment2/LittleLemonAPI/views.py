from django.shortcuts import render
from requests import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.models import Group, User
from .models import *
from .serializers import *
from .permissions import IsManager, IsDeliveryCrew
from datetime import date
import math
# Create your views here.


class CategoriesView(generics.ListCreateAPIView): ##allows me to list and create categories if user is Admin
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def get_permissions(self): ##only the admin can add or delete categories
        if self.request.method == 'POST' or self.request.method =='DELETE':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    

class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category_title']
    ordering_fields = ['price', 'category']

    def get_permissions(self): ##only admin can post, patch, delete, put
        permission_classes = []
        if self.request.method !='GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return  [permission() for permission in permission_classes]



class SingleMenuItem(generics.ListAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()

        return Response({'message': f'Status of {str(menuitem.title)} changed to {str(menuitem.featured)}'}, status.HTTP_200_OK)
    
class ManagersView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name = 'Managers')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):   #adding a user to the manager group
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers= Group.objects.get(groups__name = 'Managers')
            managers.user_set.add(user)

        return Response({'message': 'User added to managers'}, status.HTTP_201_CREATED)
    

class ManagerDeleteView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name = 'Managers')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(groups__name='Managers')
        managers.user_set.remove(user)
        return Response({'message': 'Manager succesfully deleted'}, status.HTTP_200_OK)

class DeliveryCrewView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset =  User.objects.filter(groups__name = 'Delivery_Crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            crew = Group.objects.get(name = 'Deliver_Crew')
            crew.user_set.add(user)
            return Response({'message':'Added to Delivery_Crew'}, status.HTTP_201_CREATED)
        

class DeliveryCrewDelete(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset =  User.objects.filter(groups__name = 'Delivery_Crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        crew=  Group.objects.get(name ='Delivery_Crew')
        crew.user_set.remove(user) ##from group Delivery_Crew(defined by crew), delete(defined by .remove) user( defined by get_object_or_404)

        return Response({'message': 'Removed from Delivery_Crew'}, status.HTTP_200_OK)
    

class CartView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = IsAuthenticated

    def get_queryset(self):
        return Cart.objects.filter(user = self.request.user)
    
    def post(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=id) ##i get the appropriate menuitem according to the id
        serialized_item = CartAddSerializer(data = request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']  #i extract the data that i want through the request.data
        unit_price = request.data['unit_price']
        price = int(quantity) * unit_price ##using the price assigned to menuitem and quantity i calculate price

        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=unit_price, price=price, menuitem = menuitem)
        except:
            return Response({'message':'Item already in cart'}, status.HTTP_409_CONFLICT)
        return Response({'message': 'Item in cart'}, status.HTTP_201_CREATED)
    
    def delete(self,request,*args,**kwargs):
        if request.data['menuitem']:
            serialized_item = CartRemoveSerializer(data = request.data)
            serialized_item.is_valid(raise_exception=True)
            menuitem = request.data['menuitem']
            cart = get_object_or_404(Cart, user = request.user, menuitem=menuitem)
            cart.delete()

            return Response({'message': 'Item removed from cart'}, status.HTTP_200_OK)
        else:
            Cart.objects.filter(user = request.user).delete()
            return Response({'message':'All items removed'}, status.HTTP_200_OK)
        

class OrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self): #GET REQUEST
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Managers').exists(): #admin and managers can see all orders
            return Order.objects.all()
        
        elif user.groups.filter(name = 'Delivery_Crew').exists(): #delivery crew can only see the orders assigned to them
            return Order.objects.filter(delivery_crew = user)
        
        else:
            return Order.objects.filter(user=user) #customers can only see their orders
    
    def get_permissions(self):
        if self.request.method == 'GET' or 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user = request.user)
        value_list = cart.values_list()
        if len(value_list)==0:
            return HttpResponseBadRequest()
        total = math.fsum([float(value[-1]) for value in value_list])
        order = Order.objects.create(user = request.user, status=False, total=total, date=date.today)

        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id = i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity = i['quantity'])
            orderitem.save()
        cart.delete()
        return Response({'message':f'Order placed. Order id is {str(order.id)}'}, status.HTTP_201_CREATED)


class SingleOrderView(generics.RetrieveUpdateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderMenuSerializer

    def get_permissions(self):
        user = self.request.user
        method = self.request.method
        order = Order.objects.get(pk=self.kwargs['pk'])

        if user == order.user and method =='GET':
            permission_classes = [IsAuthenticated]
        elif method == 'PUT' or method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        query = OrderItem.objects.filter(order_id = self.kwargs['pk'])
        return query
    
    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response({'message':'Status of order #'+ str(order.id)+' changed to '+str(order.status)}, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        serialized_item = OrderInsertSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return Response({'message':str(crew.username)+' was assigned to order #'+str(order.id)}, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return Response({'message':f'Order #{order_number} was deleted'}, status.HTTP_200_OK)
