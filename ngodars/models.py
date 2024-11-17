from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class USER(models.Model):
    userID = models.AutoField(primary_key=True)
    username = models.TextField()
    email = models.EmailField()
    password = models.TextField()
    phone = models.TextField()

class MERCHANT(models.Model):
    merchantID  = models.AutoField(primary_key=True)
    merchantname = models.TextField()
    userID = models.ForeignKey(USER, on_delete=models.CASCADE)

class ADDRESS(models.Model):
    addressID = models.AutoField(primary_key=True)
    fullname = models.TextField()
    statearea = models.TextField()
    poscode = models.TextField()
    unit = models.TextField(default=None)
    streetname = models.TextField()
    merchantID = models.ForeignKey(MERCHANT, on_delete=models.CASCADE, default=None)
    userID = models.ForeignKey(USER, on_delete=models.CASCADE, default=None)
    

class PREMISE(models.Model):
    PREMISE = [
        {'hall','Hall'},
        {'catering', 'Catering'},
        {'food','Food'},
    ]
    def validate_image(image):
        if image.size > 5 * 1024 * 1024:  # Limit to 2 MB
            raise ValidationError("Image file too large ( > 5MB )")
        if not image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise ValidationError("Unsupported file extension. Only .png, .jpg, and .jpeg are allowed.")
    premiseID = models.AutoField(primary_key=True)
    premisename = models.TextField()
    premisetype = models.TextField(choices=PREMISE,default=None)
    premiseimage = models.ImageField(upload_to='premise_images/', validators=[validate_image])
    addressID = models.ForeignKey(ADDRESS, on_delete=models.CASCADE)
    merchantID = models.ForeignKey(MERCHANT, on_delete=models.CASCADE)

class ITEM(models.Model):
    def validate_image(image):
        if image.size > 5 * 1024 * 1024:  # Limit to 2 MB
            raise ValidationError("Image file too large ( > 5MB )")
        if not image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise ValidationError("Unsupported file extension. Only .png, .jpg, and .jpeg are allowed.")
    itemID = models.AutoField(primary_key=True)
    itemname = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    itemimage = models.ImageField(upload_to='item_images/', validators=[validate_image])
    premiseID = models.ForeignKey(PREMISE, on_delete=models.CASCADE)

class BOOKING(models.Model):
    PAY = [
        ('not pay', 'Not Pay'),
        ('paid', 'Paid'),   
    ]
    bookingID = models.AutoField(primary_key=True)
    payment = models.TextField(choices=PAY, default='not pay')
    datetime = models.DateTimeField()
    userID = models.ForeignKey(USER, on_delete=models.CASCADE)
    itemID = models.ForeignKey(ITEM, on_delete=models.CASCADE)