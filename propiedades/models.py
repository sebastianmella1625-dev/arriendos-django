from django.conf import settings
from django.db import models

class Perfil(models.Model):
    ARRENDATARIO = 'arrendatario'
    ARRENDADOR = 'arrendador'
    TIPOS = [
        (ARRENDATARIO, 'Arrendatario'),
        (ARRENDADOR, 'Arrendador'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    tipo = models.CharField(max_length=20, choices=TIPOS, default=ARRENDATARIO)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_tipo_display()})'

class Region(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Comuna(models.Model):
    nombre = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='comunas')

    def __str__(self):
        return self.nombre

class TipoInmueble(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Propietario(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class Inmueble(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField()
    direccion = models.CharField(max_length=200)
    comuna = models.ForeignKey(Comuna, on_delete=models.SET_NULL, null=True)
    tipo_inmueble = models.ForeignKey(TipoInmueble, on_delete=models.SET_NULL, null=True)
    propietario = models.ForeignKey(Propietario, on_delete=models.PROTECT)
    precio_arriendo = models.DecimalField(max_digits=10, decimal_places=2)
    disponibilidad = models.BooleanField(default=True)

    def __str__(self):
        return self.direccion
