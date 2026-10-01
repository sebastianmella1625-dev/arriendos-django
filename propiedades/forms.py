from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction

from .models import Perfil, Inmueble, Comuna, Region

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    tipo = forms.ChoiceField(label='Tipo de usuario', choices=Perfil.TIPOS)
    telefono = forms.CharField(label='Teléfono', max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Perfil.objects.create(
                user=user,
                tipo=self.cleaned_data['tipo'],
                telefono=self.cleaned_data['telefono'],
            )
        return user

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['telefono']
        labels = {'telefono': 'Teléfono'}

class InmuebleForm(forms.ModelForm):
    # propietario no va en el formulario: lo asigna la vista según el usuario logueado
    class Meta:
        model = Inmueble
        fields = ['nombre', 'descripcion', 'direccion', 'comuna', 'tipo_inmueble',
                  'precio_arriendo', 'disponibilidad']
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'direccion': 'Dirección',
            'comuna': 'Comuna',
            'tipo_inmueble': 'Tipo de inmueble',
            'precio_arriendo': 'Precio de arriendo mensual (CLP)',
            'disponibilidad': 'Disponible para arrendar',
        }
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comuna'].queryset = Comuna.objects.order_by('nombre')

    def clean_precio_arriendo(self):
        precio = self.cleaned_data['precio_arriendo']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')
        return precio

class FiltroInmueblesForm(forms.Form):
    region = forms.ModelChoiceField(
        label='Región', queryset=Region.objects.order_by('pk'),
        required=False, empty_label='Todas las regiones',
        # Al cambiar la región se recarga, para que el selector de comunas muestre solo las de esa región
        widget=forms.Select(attrs={'onchange': "this.form.comuna.value=''; this.form.submit()"}),
    )
    comuna = forms.ModelChoiceField(
        label='Comuna', queryset=Comuna.objects.order_by('nombre'),
        required=False, empty_label='Todas las comunas',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Con una región elegida, el selector de comunas solo ofrece las de esa región
        region_id = self.data.get('region')
        if region_id and region_id.isdigit():
            self.fields['comuna'].queryset = Comuna.objects.filter(region_id=region_id).order_by('nombre')

    def filtrar(self, inmuebles):
        region = self.cleaned_data.get('region')
        comuna = self.cleaned_data.get('comuna')
        if region:
            inmuebles = inmuebles.filter(comuna__region=region)
        if comuna:
            inmuebles = inmuebles.filter(comuna=comuna)
        return inmuebles
