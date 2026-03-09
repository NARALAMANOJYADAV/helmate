from django.db import models

class Challan(models.Model):
    vehicle_no = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    image_path = models.CharField(max_length=255)
    status = models.CharField(max_length=20, default='Pending')

    def __str__(self):
        return f"{self.vehicle_no} - {self.timestamp}"
