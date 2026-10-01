from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegistroForm, UsuarioForm, PerfilForm, InmuebleForm, FiltroInmueblesForm
from .models import Perfil, Inmueble, Propietario

def arrendador_requerido(vista):
    """Solo deja pasar a usuarios logueados cuyo perfil sea de arrendador."""
    @login_required
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        perfil, _ = Perfil.objects.get_or_create(user=request.user)
        if perfil.tipo != Perfil.ARRENDADOR:
            raise PermissionDenied
        return vista(request, *args, **kwargs)
    return envoltura

def inmuebles_del_usuario(user):
    # Propietario no está ligado a User: el puente es el correo
    if not user.email:
        return Inmueble.objects.none()
    return Inmueble.objects.filter(propietario__email=user.email)

def registro(request):
    if request.user.is_authenticated:
        return redirect('perfil')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cuenta creada. ¡Bienvenido!')
            return redirect('perfil')
    else:
        form = RegistroForm()

    return render(request, 'registration/registro.html', {'form': form})

@login_required
def perfil(request):
    # Usuarios creados antes de existir Perfil (fixtures, superusuario) no tienen uno
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if perfil.tipo == Perfil.ARRENDADOR:
        inmuebles = inmuebles_del_usuario(request.user)
    else:
        inmuebles = Inmueble.objects.filter(disponibilidad=True)
    inmuebles = inmuebles.select_related('comuna', 'tipo_inmueble')

    return render(request, 'perfil.html', {'perfil': perfil, 'inmuebles': inmuebles})

@login_required
def editar_perfil(request):
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST, instance=request.user)
        perfil_form = PerfilForm(request.POST, instance=perfil)
        if usuario_form.is_valid() and perfil_form.is_valid():
            usuario_form.save()
            perfil_form.save()
            messages.success(request, 'Tus datos se actualizaron correctamente.')
            return redirect('perfil')
    else:
        usuario_form = UsuarioForm(instance=request.user)
        perfil_form = PerfilForm(instance=perfil)

    return render(request, 'editar_perfil.html', {
        'usuario_form': usuario_form,
        'perfil_form': perfil_form,
    })

def inmuebles_disponibles(request):
    inmuebles = (Inmueble.objects
                 .filter(disponibilidad=True)
                 .select_related('comuna__region', 'tipo_inmueble')
                 .order_by('precio_arriendo'))

    # GET, no POST: filtrar no modifica datos y así la URL filtrada se puede compartir
    filtro = FiltroInmueblesForm(request.GET)
    filtro.is_valid()  # un valor inválido (ej. comuna de otra región) se ignora, no rompe la página
    inmuebles = filtro.filtrar(inmuebles)

    return render(request, 'inmuebles_disponibles.html', {'inmuebles': inmuebles, 'filtro': filtro})

@arrendador_requerido
def mis_inmuebles(request):
    inmuebles = (inmuebles_del_usuario(request.user)
                 .select_related('comuna', 'tipo_inmueble')
                 .order_by('nombre'))
    return render(request, 'mis_inmuebles.html', {'inmuebles': inmuebles})

@arrendador_requerido
def crear_inmueble(request):
    if not request.user.email:
        messages.error(request, 'Agrega un correo a tu perfil antes de publicar un inmueble.')
        return redirect('editar_perfil')

    if request.method == 'POST':
        form = InmuebleForm(request.POST)
        if form.is_valid():
            inmueble = form.save(commit=False)
            propietario = Propietario.objects.filter(email=request.user.email).first()
            if propietario is None:
                propietario = Propietario.objects.create(
                    nombre=request.user.first_name or request.user.username,
                    apellido=request.user.last_name,
                    telefono=request.user.perfil.telefono,
                    email=request.user.email,
                )
            inmueble.propietario = propietario
            inmueble.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" publicado.')
            return redirect('mis_inmuebles')
    else:
        form = InmuebleForm()

    return render(request, 'inmueble_form.html', {'form': form, 'titulo': 'Publicar inmueble'})

@arrendador_requerido
def editar_inmueble(request, pk):
    # Buscar dentro de los inmuebles del usuario: uno ajeno da 404, no se puede editar
    inmueble = get_object_or_404(inmuebles_del_usuario(request.user), pk=pk)

    if request.method == 'POST':
        form = InmuebleForm(request.POST, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, f'Inmueble "{inmueble.nombre}" actualizado.')
            return redirect('mis_inmuebles')
    else:
        form = InmuebleForm(instance=inmueble)

    return render(request, 'inmueble_form.html', {'form': form, 'titulo': 'Editar inmueble'})

@arrendador_requerido
def eliminar_inmueble(request, pk):
    inmueble = get_object_or_404(inmuebles_del_usuario(request.user), pk=pk)

    if request.method == 'POST':
        nombre = inmueble.nombre
        inmueble.delete()
        messages.success(request, f'Inmueble "{nombre}" eliminado.')
        return redirect('mis_inmuebles')

    return render(request, 'inmueble_confirmar_eliminar.html', {'inmueble': inmueble})
