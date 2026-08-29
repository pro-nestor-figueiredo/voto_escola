from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class Perfil(models.Model):
    """Nível de autorização do usuário no sistema de votação."""
    NIVEL_CHOICES = [
        ('admin', 'Administrador'),
        ('gestor', 'Gestor'),
        ('professor', 'Professor'),
        ('aluno', 'Aluno'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nivel = models.CharField('Nível', max_length=20, choices=NIVEL_CHOICES, default='aluno')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.user.username} ({self.get_nivel_display()})'


class Aluno(models.Model):
    """Dados dos alunos da escola que votam."""
    ra = models.CharField('RA', max_length=30, unique=True)
    nome = models.CharField('Nome', max_length=100)
    turma = models.CharField('Turma', max_length=20, blank=True)
    serie = models.CharField('Série', max_length=30, blank=True)
    escola = models.CharField('Escola', max_length=50, blank=True)
    ativo = models.BooleanField('Ativo', default=True, help_text='Alunos inativos não podem votar')
    usuario = models.OneToOneField(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name='aluno', help_text='Conta de login vinculada (username = RA)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    def __str__(self):
        return f'{self.nome} ({self.ra})'


class Eleicao(models.Model):
    """Votação com tema e janela de votação (início–fim)."""
    titulo = models.CharField('Tema', max_length=120)
    descricao = models.TextField('Descrição', blank=True)
    inicio = models.DateTimeField('Início da votação')
    fim = models.DateTimeField('Fim da votação')
    ativa = models.BooleanField('Ativa', default=True, help_text='Desative para suspender a votação')
    publicar_resultados = models.BooleanField(
        'Publicar resultados', default=True,
        help_text='Alunos podem consultar o resultado após o encerramento'
    )
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-inicio']
        verbose_name = 'Eleição / Votação'
        verbose_name_plural = 'Eleições / Votações'

    def __str__(self):
        return self.titulo

    @property
    def status(self):
        now = timezone.now()
        if not self.ativa:
            return 'suspensa'
        if now < self.inicio:
            return 'agendada'
        if now > self.fim:
            return 'encerrada'
        return 'aberta'

    def janela_aberta(self):
        return self.ativa and self.inicio <= timezone.now() <= self.fim

    @property
    def total_votos(self):
        return self.votos.count()

    @property
    def total_eleitores(self):
        return Aluno.objects.filter(ativo=True).count()

    @property
    def participacao(self):
        total = self.total_eleitores
        if total == 0:
            return 0
        return round(self.total_votos / total * 100, 1)


class Opcao(models.Model):
    """Opção/chapa/candidato de uma eleição."""
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='opcoes')
    nome = models.CharField('Nome', max_length=120)
    descricao = models.TextField('Descrição', blank=True)
    ordem = models.PositiveIntegerField('Ordem', default=0)

    class Meta:
        ordering = ['ordem', 'id']
        verbose_name = 'Opção'
        verbose_name_plural = 'Opções'

    def __str__(self):
        return self.nome

    @property
    def votos(self):
        return self.votos_rel.count()


class Voto(models.Model):
    """Registro do voto (1 voto por aluno por eleição)."""
    eleicao = models.ForeignKey(Eleicao, on_delete=models.CASCADE, related_name='votos')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='votos')
    opcao = models.ForeignKey(Opcao, on_delete=models.CASCADE, related_name='votos_rel')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('eleicao', 'aluno')
        ordering = ['criado_em']
        verbose_name = 'Voto'
        verbose_name_plural = 'Votos'

    def __str__(self):
        return f'{self.aluno.nome} → {self.opcao.nome}'
