from rest_framework import serializers      #This imports tools needed for serialization to take place from the restframework
from .models import Payment                 #imports the Payment class defined in models.py 

class PaymentSerializer(serializers.ModelSerializer):   #This is a class showiing that Payment is the one to be serialized and it inherits from the base class ModelSerializer in serializer module.
    class Meta:         #additional info as to how the class PaymentSerializer should behave. 
        model = Payment         #contd from above. the model its working on is Payment and the field to convert/ format into JSON or others(in otherwords--serialize) is all the fields
        fields = '__all__'
