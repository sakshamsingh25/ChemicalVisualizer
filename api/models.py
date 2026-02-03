from django.db import models

class UploadHistory(models.Model):
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    total_count = models.IntegerField()
    avg_pressure = models.FloatField()
    avg_temp = models.FloatField()
    avg_flowrate = models.FloatField(default=0.0) 

    def __str__(self):
        return self.filename