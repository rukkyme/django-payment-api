from django.urls import path        #path allows us define URL routes
from . import views         #this imports views.py file so we can  easily connect URL to view fxns like the create_payment

urlpatterns = [                 #a list to define all the URLs for this app
    path('payments', views.create_payment, name='create_payment'),      #this is saying: if anyone visit /payments(as in makes a POST request) django should run the create_payment view
    path('payments/<int:pk>', views.get_payment, name='get_payment'),  #this is for other users who makes POST requests. django allocaes a pk to them e.g 1,2,3 so we'll have, payments/1
    path('paystack/webhook', views.paystack_webhook, name='paystack_webhook'),
    
]
