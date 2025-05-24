from django.db import models # this ask Django to bring in models module containing all the tools and building blocks for creating Django models that interacts with the database am creating

# Create your models here.
class Payment(models.Model): #payment class is defined. It as Model as all model created are defined as a class , it is inheriting from models.Model
    customer_name = models.CharField(max_length=100)
    customer_email =models. EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')
    
    def __str__(self):      #This returns the string representation of the object in the payment class.
        return f'{self.customer_name} - {self.amount} - {self.status}'
    
