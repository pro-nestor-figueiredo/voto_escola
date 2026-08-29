from django.contrib import admin

from .models import Aluno, Eleicao, Opcao, Perfil, Voto


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'nivel')
    list_filter = ('nivel',)


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('ra', 'nome', 'turma', 'serie', 'escola', 'ativo', 'usuario')
    list_filter = ('ativo', 'escola')
    search_fields = ('ra', 'nome')


class OpcaoInline(admin.TabularInline):
    model = Opcao
    extra = 1


@admin.register(Eleicao)
class EleicaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'inicio', 'fim', 'ativa', 'status', 'total_votos')
    list_filter = ('ativa',)
    search_fields = ('titulo',)
    inlines = [OpcaoInline]


@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('eleicao', 'aluno', 'opcao', 'criado_em')
    list_filter = ('eleicao',)
    search_fields = ('aluno__nome', 'aluno__ra')
