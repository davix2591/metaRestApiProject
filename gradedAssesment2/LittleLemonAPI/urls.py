from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/category', views.CategoriesView.as_view()),
    path('menu-items/', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItem.as_view()),
    path('groups/manager/users', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagerDeleteView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewDelete.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    
]