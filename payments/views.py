import hashlib
import hmac
import json

import requests
from django.conf import settings

from rest_framework import status       #imports the status module from DRF. shortcuts for HTTP status code. e.g HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.response import Response        #imports the Response class from DRF. allows you to return data(E.g dictionaries, lists) which DRF renders into JSON for the API client
from rest_framework.decorators import api_view      #imports a decorator turns regular python fx into REST API views.is there to mark the django fxn as an APTView that should only respond to specific HTTP methods e.g GET, POST, PUT,DELETE
from .models import Payment
from .serializers import PaymentSerializer

""" All of these works for the endpoints but the customers data is stored in data base and paystack is not integrated with the API
#Endpoint for Making Payment.
@api_view(['POST'])         #Its a decorator telling us that the next fxn is an APIView and should respond only to HTTP POST requests
def create_payment(request):    #Defines the function to handle incoming requests.
    serializer = PaymentSerializer(data=request.data)   #this takes user's data(name, email, amount) and passes to serializer to convert to JSON or validate
    if serializer.is_valid():       #checks if data is valid. is email an email, is amount a number?
        payment = serializer.save()     #if data is valid, it save the serialized data to payment.
        return Response({               #here gives an already serialized data(converted data to dictionary) plus the appropriate HTTP response
            "payment": serializer.data,
            "status": "success",
            "message": "Payment initiated successfully."
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      #in an instance of bad data(e.g wrong or missing email) it sends
"""


#Endpoint for Getting Payment from 
@api_view(['GET'])              #This view only handles GET requests.
def get_payment(request, pk):     #pk means “primary key” or ID of the payment you want to look up. 
    try:
        payment = Payment.objects.get(pk=pk)        #this tries to fetch the payment from the database using the given ID.
    except Payment.DoesNotExist:        #If the payment with that ID doesn't exist, sends back a 404 error.
        return Response({"status": "error", "message": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)     #otherwise it does the next line
    
    serializer = PaymentSerializer(payment)     #Converts the payment object into JSON.
    return Response({                             # and then sends back the payment info in JSON with a success message
        "payment": serializer.data,
        "status": "success",
        "message": "Payment details retrieved successfully."
    })


#For the integration of a payment gateway to function, we replace the "create_payment function above with this:

@api_view(['POST'])
def create_payment(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        payment = serializer.save()

        # Send data to Paystack
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "email": payment.customer_email,
            "amount": int(payment.amount * 100),  # Paystack uses kobo
            "reference": f"PAY-{payment.id}",
            "callback_url": "http://localhost:8000/api/v1/payments/verify/"
        }

        response = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        res_data = response.json()

        if response.status_code == 200:
            return Response({
                "payment": serializer.data,
                "status": "success",
                "message": "Payment initiated successfully.",
                "authorization_url": res_data['data']['authorization_url']
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": "error",
                "message": "Failed to initiate payment with Paystack.",
                "details": res_data
            }, status=status.HTTP_400_BAD_REQUEST)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def paystack_webhook(request):
    paystack_secret = settings.PAYSTACK_SECRET_KEY.encode('utf-8')
    signature = request.headers.get('X-Paystack-Signature')

    payload = request.body
    expected_signature = hmac.new(paystack_secret, payload, hashlib.sha512).hexdigest()

    if signature != expected_signature:
        return Response({"status": "error", "message": "Invalid signature"}, status=400)

    data = json.loads(payload)

    if data['event'] == 'charge.success':
        reference = data['data']['reference']
        try:
            payment_id = int(reference.split('-')[-1])  # Extract ID from reference
            payment = Payment.objects.get(id=payment_id)
            payment.status = 'completed'
            payment.save()
        except Payment.DoesNotExist:
            pass  # Log error in real app

    return Response({"status": "success"}, status=200)