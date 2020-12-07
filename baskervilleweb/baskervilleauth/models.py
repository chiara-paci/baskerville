from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass
    # date_of_birth = models.DateField()
    # gender = models.CharField(max_length=128,choices=[ ("male","male"),
    #                                                    ("female","female") ])
    # height = models.PositiveIntegerField(verbose_name='height (cm)',default=160)
    # # https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation
    # lifestyle = models.CharField(max_length=128,choices=[ ("sedentary","sedentary"),     
    #                                                       ("active","active"),           
    #                                                       ("very active","very active")])

    
    # class Meta:
    #     db_table='auth_user'

