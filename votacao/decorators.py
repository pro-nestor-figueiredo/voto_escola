from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def nivel_requerido(*niveis):
    """Permite acesso apenas a usuários com perfil nos níveis informados
    (superusuário sempre passa). Redireciona conforme o papel do usuário."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect('login')
            if user.is_superuser:
                return view_func(request, *args, **kwargs)
            nivel = getattr(getattr(user, 'perfil', None), 'nivel', None)
            if nivel in niveis:
                return view_func(request, *args, **kwargs)
            if nivel == 'aluno':
                # aluno em área de staff → volta silenciosamente pra urna
                return redirect('urna')
            messages.error(request, 'Acesso negado: seu nível de permissão não permite esta ação.')
            return redirect('dashboard')
        return _wrapped
    return decorator


def is_staff(user):
    return user.is_superuser or getattr(getattr(user, 'perfil', None), 'nivel', None) in ('admin', 'gestor', 'professor')
