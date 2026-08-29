from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('urna/', views.urna, name='urna'),
    path('meus-votos/', views.meus_votos, name='meus_votos'),
    path('resultados/', views.resultados, name='resultados'),

    path('eleicoes/', views.eleicoes, name='eleicoes'),
    path('eleicoes/nova/', views.eleicao_nova, name='eleicao_nova'),
    path('eleicoes/<int:pk>/', views.eleicao_detalhe, name='eleicao_detalhe'),
    path('eleicoes/<int:pk>/editar/', views.eleicao_editar, name='eleicao_editar'),
    path('eleicoes/<int:pk>/excluir/', views.eleicao_excluir, name='eleicao_excluir'),
    path('eleicoes/<int:eleicao_pk>/opcoes/<int:opcao_pk>/excluir/', views.opcao_excluir, name='opcao_excluir'),

    path('alunos/', views.alunos, name='alunos'),
    path('alunos/novo/', views.aluno_novo, name='aluno_novo'),
    path('alunos/<int:pk>/editar/', views.aluno_editar, name='aluno_editar'),
    path('alunos/<int:pk>/toggle/', views.aluno_toggle, name='aluno_toggle'),
    path('alunos/<int:pk>/criar-login/', views.aluno_criar_login, name='aluno_criar_login'),
    path('alunos/<int:pk>/reset-senha/', views.aluno_reset_senha, name='aluno_reset_senha'),
]
