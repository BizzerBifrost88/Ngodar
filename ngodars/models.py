from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class USER(models.Model):
    userID = models.AutoField(primary_key=True)
    username = models.TextField(default=None)
    email = models.EmailField(default=None)
    password = models.TextField(default=None)
    phone = models.TextField(default=None)
    def __str__(self):
        return f"{self.username}"

class MERCHANT(models.Model):
    merchantID  = models.AutoField(primary_key=True)
    merchantname = models.TextField(default=None)
    userID = models.ForeignKey(USER, on_delete=models.CASCADE, default=None)
    def __str__(self):
        return f"{self.merchantname}"

class ADDRESS(models.Model):
    addressID = models.AutoField(primary_key=True)
    fullname = models.TextField(default=None)
    statearea = models.TextField(default=None)
    poscode = models.TextField(default=None)
    unit = models.TextField(default=None)
    streetname = models.TextField(default=None)
    userID = models.ForeignKey(USER, on_delete=models.CASCADE, default=None)
    is_used = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.fullname}"
    

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
    premiseimage = models.ImageField(upload_to='premise_images/', validators=[validate_image], default=None)
    statearea = models.TextField(default=None)
    poscode = models.TextField(default=None)
    unit = models.TextField(default=None)
    streetname = models.TextField(default=None)
    merchantID = models.ForeignKey(MERCHANT, on_delete=models.CASCADE, default=None)
    def __str__(self):
        return f"{self.premisename}"

class ITEM(models.Model):
    def validate_image(image):
        if image.size > 5 * 1024 * 1024:  # Limit to 2 MB
            raise ValidationError("Image file too large ( > 5MB )")
        if not image.name.endswith(('.png', '.jpg', '.jpeg')):
            raise ValidationError("Unsupported file extension. Only .png, .jpg, and .jpeg are allowed.")
    itemID = models.AutoField(primary_key=True)
    itemname = models.TextField(default=None)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    itemimage = models.ImageField(upload_to='item_images/', validators=[validate_image], default=None)
    premiseID = models.ForeignKey(PREMISE, on_delete=models.CASCADE, default=None)
    def __str__(self):
        return f"{self.itemname}"

class BOOKING(models.Model):
    PAY = [
        ('not pay', 'Not Pay'),
        ('paid', 'Paid'),   
    ]
    bookingID = models.AutoField(primary_key=True)
    payment = models.TextField(choices=PAY, default='not pay')
    datetime = models.DateTimeField(default=None)
    userID = models.ForeignKey(USER, on_delete=models.CASCADE, default=None)
    itemID = models.ForeignKey(ITEM, on_delete=models.CASCADE, default=None)