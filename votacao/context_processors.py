from .models import Perfil


def perfil_global(request):
    """Expõe o perfil do usuário logado em todas as templates."""
    perfil = None
    if request.user.is_authenticated:
        perfil = getattr(request.user, 'perfil', None)
        if perfil is None:
            perfil = Perfil(nivel='staff', user=request.user)
    return {'perfil': perfil}
