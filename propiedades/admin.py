from django.contrib import admin
from .models import Inmueble, Propietario, TipoInmueble, Perfil

class InmuebleAdmin(admin.ModelAdmin):
    list_display = ["tipo_inmueble", "precio_arriendo", "direccion"] 
    search_fields = ["direccion"]
    list_filter = ["tipo_inmueble", "propietario", "disponibilidad"]

class PropietarioAdmin(admin.ModelAdmin):
    list_display = ["nombre","apellido","telefono","email"] 
    search_fields = ["nombre","apellido","email"]
    list_filter = []

admin.site.register(Inmueble, InmuebleAdmin)
admin.site.register(Propietario, PropietarioAdmin)
admin.site.register(TipoInmueble)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ["user", "tipo", "telefono"]
    list_filter = ["tipo"]
    search_fields = ["user__username", "user__email"]

# Register your models here.
