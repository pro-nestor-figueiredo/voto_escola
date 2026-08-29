import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import is_staff, nivel_requerido
from .forms import AlunoForm, EleicaoForm, OpcaoForm
from .models import Aluno, Eleicao, Opcao, Perfil, Voto


# --------------------------------------------------------------------------
# Dashboard (admin / gestor / professor)
# --------------------------------------------------------------------------
@login_required
@nivel_requerido('admin', 'gestor', 'professor')
def dashboard(request):
    now = timezone.now()
    eleicoes = Eleicao.objects.all()
    abertas = [e for e in eleicoes if e.status == 'aberta']
    agendadas = [e for e in eleicoes if e.status == 'agendada']
    encerradas = [e for e in eleicoes if e.status == 'encerrada']

    total_eleitores = Aluno.objects.filter(ativo=True).count()
    total_votos = Voto.objects.count()
    participacao_media = round(total_votos / total_eleitores * 100, 1) if total_eleitores else 0

    # Dados p/ gráfico: votos por eleição (últimas 10)
    chart_eleicoes = list(eleicoes[:10])
    chart_labels = [e.titulo[:22] for e in reversed(chart_eleicoes)]
    chart_data = [e.total_votos for e in reversed(chart_eleicoes)]

    context = {
        'abertas': abertas,
        'agendadas': agendadas,
        'encerradas': encerradas,
        'total_eleicoes': eleicoes.count(),
        'total_eleitores': total_eleitores,
        'total_votos': total_votos,
        'participacao_media': participacao_media,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'votacao/dashboard.html', context)


# --------------------------------------------------------------------------
# Urna (alunos)
# --------------------------------------------------------------------------
@login_required
def urna(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil and perfil.nivel != 'aluno':
        return redirect('dashboard')

    aluno = getattr(request.user, 'aluno', None)

    if request.method == 'POST':
        if not aluno or not aluno.ativo:
            messages.error(request, 'Seu cadastro de aluno está inativo ou ausente.')
            return redirect('urna')
        eleicao = get_object_or_404(Eleicao, pk=request.POST.get('eleicao_id'))
        opcao_id = request.POST.get('opcao_id')
        if not eleicao.janela_aberta():
            messages.error(request, 'A votação não está aberta no momento.')
        elif not opcao_id:
            messages.error(request, 'Selecione uma opção para votar.')
        elif Voto.objects.filter(eleicao=eleicao, aluno=aluno).exists():
            messages.error(request, 'Você já votou nesta eleição.')
        else:
            opcao = get_object_or_404(Opcao, pk=opcao_id, eleicao=eleicao)
            Voto.objects.create(eleicao=eleicao, aluno=aluno, opcao=opcao)
            messages.success(request, f'Voto computado com sucesso em "{opcao.nome}"!')
        return redirect('urna')

    abertas = [e for e in Eleicao.objects.all() if e.janela_aberta()]
    agendadas = [e for e in Eleicao.objects.all() if e.status == 'agendada']
    ja_votou = set()
    if aluno:
        ja_votou = set(Voto.objects.filter(aluno=aluno).values_list('eleicao_id', flat=True))

    context = {
        'abertas': abertas,
        'agendadas': agendadas,
        'ja_votou': ja_votou,
        'aluno': aluno,
    }
    return render(request, 'votacao/urna.html', context)


@login_required
@nivel_requerido('aluno')
def meus_votos(request):
    aluno = getattr(request.user, 'aluno', None)
    votos = Voto.objects.filter(aluno=aluno).select_related('eleicao', 'opcao') if aluno else []
    return render(request, 'votacao/meus_votos.html', {'votos': votos})


# --------------------------------------------------------------------------
# Resultados
# --------------------------------------------------------------------------
@login_required
def resultados(request):
    perfil = getattr(request.user, 'perfil', None)
    eh_staff = is_staff(request.user)

    eleicoes = Eleicao.objects.all()
    eleicao_id = request.GET.get('eleicao')
    if eleicao_id:
        eleicao = get_object_or_404(Eleicao, pk=eleicao_id)
    else:
        eleicao = eleicoes.first()

    if eleicao is None:
        return render(request, 'votacao/resultados.html', {'sem_eleicao': True})

    # Aluno só vê se a eleição encerrou e o resultado foi publicado
    if not eh_staff and (eleicao.status != 'encerrada' or not eleicao.publicar_resultados):
        messages.error(request, 'Os resultados desta eleição ainda não foram publicados.')
        return redirect('urna')

    opcoes = list(eleicao.opcoes.all())
    total = eleicao.total_votos
    for o in opcoes:
        o.percentual = round(o.votos / total * 100, 1) if total else 0

    context = {
        'eleicao': eleicao,
        'eleicoes': eleicoes,
        'opcoes': opcoes,
        'total': total,
        'eh_staff': eh_staff,
        'chart_labels': json.dumps([o.nome for o in opcoes]),
        'chart_data': json.dumps([o.votos for o in opcoes]),
    }
    return render(request, 'votacao/resultados.html', context)


# --------------------------------------------------------------------------
# CRUD Eleições (admin)
# --------------------------------------------------------------------------
@login_required
@nivel_requerido('admin')
def eleicoes(request):
    lista = Eleicao.objects.all()
    return render(request, 'votacao/eleicoes.html', {'eleicoes': lista})


@login_required
@nivel_requerido('admin')
def eleicao_nova(request):
    if request.method == 'POST':
        form = EleicaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eleição criada com sucesso.')
            return redirect('eleicoes')
    else:
        form = EleicaoForm()
    return render(request, 'votacao/eleicao_form.html', {'form': form, 'titulo_pagina': 'Nova Eleição'})


@login_required
@nivel_requerido('admin')
def eleicao_editar(request, pk):
    eleicao = get_object_or_404(Eleicao, pk=pk)
    if request.method == 'POST':
        form = EleicaoForm(request.POST, instance=eleicao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Eleição atualizada.')
            return redirect('eleicao_detalhe', pk=eleicao.pk)
    else:
        form = EleicaoForm(instance=eleicao)
    return render(request, 'votacao/eleicao_form.html', {'form': form, 'titulo_pagina': 'Editar Eleição'})


@login_required
@nivel_requerido('admin')
def eleicao_excluir(request, pk):
    eleicao = get_object_or_404(Eleicao, pk=pk)
    if request.method == 'POST':
        eleicao.delete()
        messages.success(request, 'Eleição excluída.')
    return redirect('eleicoes')


@login_required
@nivel_requerido('admin')
def eleicao_detalhe(request, pk):
    eleicao = get_object_or_404(Eleicao, pk=pk)
    if request.method == 'POST':
        form = OpcaoForm(request.POST)
        if form.is_valid():
            opcao = form.save(commit=False)
            opcao.eleicao = eleicao
            opcao.save()
            messages.success(request, f'Opção "{opcao.nome}" adicionada.')
        return redirect('eleicao_detalhe', pk=eleicao.pk)
    form = OpcaoForm()
    opcoes = eleicao.opcoes.all()
    total = eleicao.total_votos
    for o in opcoes:
        o.percentual = round(o.votos / total * 100, 1) if total else 0
    return render(request, 'votacao/eleicao_detalhe.html', {
        'eleicao': eleicao,
        'opcoes': opcoes,
        'form': form,
        'total': total,
        'chart_labels': json.dumps([o.nome for o in opcoes]),
        'chart_data': json.dumps([o.votos for o in opcoes]),
    })


@login_required
@nivel_requerido('admin')
def opcao_excluir(request, eleicao_pk, opcao_pk):
    opcao = get_object_or_404(Opcao, pk=opcao_pk, eleicao_id=eleicao_pk)
    if request.method == 'POST':
        opcao.delete()
        messages.success(request, 'Opção excluída.')
    return redirect('eleicao_detalhe', pk=eleicao_pk)


# --------------------------------------------------------------------------
# CRUD Alunos (admin)
# --------------------------------------------------------------------------
@login_required
@nivel_requerido('admin')
def alunos(request):
    q = request.GET.get('q', '').strip()
    lista = Aluno.objects.all()
    if q:
        lista = lista.filter(nome__icontains=q) | lista.filter(ra__icontains=q)
    lista = lista.order_by('nome')
    return render(request, 'votacao/alunos.html', {'alunos': lista, 'q': q, 'total': lista.count()})


@login_required
@nivel_requerido('admin')
def aluno_novo(request):
    if request.method == 'POST':
        form = AlunoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno cadastrado.')
            return redirect('alunos')
    else:
        form = AlunoForm()
    return render(request, 'votacao/aluno_form.html', {'form': form, 'titulo_pagina': 'Novo Aluno'})


@login_required
@nivel_requerido('admin')
def aluno_editar(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno atualizado.')
            return redirect('alunos')
    else:
        form = AlunoForm(instance=aluno)
    return render(request, 'votacao/aluno_form.html', {'form': form, 'titulo_pagina': f'Editar {aluno.nome}'})


@login_required
@nivel_requerido('admin')
def aluno_toggle(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        aluno.ativo = not aluno.ativo
        aluno.save()
        messages.success(request, f'Aluno {"reativado" if aluno.ativo else "inativado"}: {aluno.nome}.')
    return redirect('alunos')


@login_required
@nivel_requerido('admin')
def aluno_criar_login(request, pk):
    """Cria a conta de login do aluno (username = RA, senha inicial = RA)."""
    aluno = get_object_or_404(Aluno, pk=pk)
    if aluno.usuario:
        messages.warning(request, f'{aluno.nome} já possui login ({aluno.usuario.username}).')
    elif User.objects.filter(username=aluno.ra).exists():
        messages.error(request, f'Já existe um usuário com username {aluno.ra}.')
    else:
        with transaction.atomic():
            user = User.objects.create_user(username=aluno.ra, password=aluno.ra, first_name=aluno.nome)
            Perfil.objects.create(user=user, nivel='aluno')
            aluno.usuario = user
            aluno.save()
        messages.success(request, f'Login criado: {aluno.ra} / senha inicial: {aluno.ra}.')
    return redirect('alunos')


@login_required
@nivel_requerido('admin')
def aluno_reset_senha(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    if request.method == 'POST':
        if not aluno.usuario:
            messages.error(request, 'Este aluno ainda não tem login. Crie o login primeiro.')
        else:
            aluno.usuario.set_password(aluno.ra)
            aluno.usuario.save()
            messages.success(request, f'Senha de {aluno.nome} resetada para o RA ({aluno.ra}).')
    return redirect('alunos')
