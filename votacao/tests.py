from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import EleicaoForm
from .models import Aluno, Eleicao, Opcao, Perfil, Voto


class VotoEscolaTestes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(username='admin', password='x')
        Perfil.objects.create(user=cls.admin, nivel='admin')

        cls.aluno = Aluno.objects.create(ra='00001106217263sp', nome='Ana Teste', ativo=True)
        u = User.objects.create_user(username=cls.aluno.ra, password=cls.aluno.ra, first_name='Ana')
        Perfil.objects.create(user=u, nivel='aluno')
        cls.aluno.usuario = u
        cls.aluno.save()

        cls.eleicao = Eleicao.objects.create(
            titulo='Grêmio 2026',
            inicio=timezone.now() - timedelta(hours=1),
            fim=timezone.now() + timedelta(hours=1),
        )
        cls.op1 = Opcao.objects.create(eleicao=cls.eleicao, nome='Chapa 1', ordem=1)
        cls.op2 = Opcao.objects.create(eleicao=cls.eleicao, nome='Chapa 2', ordem=2)

    # --- acesso e níveis ---
    def test_login_redireciona_sem_auth(self):
        r = self.client.get(reverse('urna'))
        self.assertEqual(r.status_code, 302)

    def test_admin_ve_dashboard(self):
        self.client.login(username='admin', password='x')
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_aluno_nao_ve_dashboard(self):
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.get(reverse('dashboard'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/urna/', r.url)

    def test_aluno_nao_ve_crud_eleicoes(self):
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.get(reverse('eleicoes'))
        self.assertEqual(r.status_code, 302)

    # --- urna e janela de votação ---
    def test_voto_dentro_da_janela(self):
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.post(reverse('urna'), {'eleicao_id': self.eleicao.id, 'opcao_id': self.op1.id})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(Voto.objects.filter(eleicao=self.eleicao, aluno=self.aluno).exists())

    def test_voto_duplicado_bloqueado(self):
        Voto.objects.create(eleicao=self.eleicao, aluno=self.aluno, opcao=self.op1)
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.post(reverse('urna'), {'eleicao_id': self.eleicao.id, 'opcao_id': self.op2.id})
        self.assertEqual(Voto.objects.filter(eleicao=self.eleicao, aluno=self.aluno).count(), 1)

    def test_voto_fora_da_janela_bloqueado(self):
        eleicao_futura = Eleicao.objects.create(
            titulo='Futura',
            inicio=timezone.now() + timedelta(days=1),
            fim=timezone.now() + timedelta(days=2),
        )
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.post(reverse('urna'), {'eleicao_id': eleicao_futura.id, 'opcao_id': self.op1.id})
        self.assertFalse(Voto.objects.filter(eleicao=eleicao_futura).exists())

    def test_aluno_inativo_nao_vota(self):
        self.aluno.ativo = False
        self.aluno.save()
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        self.client.post(reverse('urna'), {'eleicao_id': self.eleicao.id, 'opcao_id': self.op1.id})
        self.assertFalse(Voto.objects.filter(eleicao=self.eleicao, aluno=self.aluno).exists())

    # --- fuso horário ---
    def test_form_interpreta_horario_como_local(self):
        """Input datetime-local (sem fuso) deve ser tratado como America/Sao_Paulo."""
        form = EleicaoForm(data={
            'titulo': 'Teste fuso',
            'inicio': '2026-08-29T13:38',
            'fim': '2026-08-29T17:01',
            'ativa': True,
            'publicar_resultados': True,
        })
        self.assertTrue(form.is_valid(), form.errors)
        eleicao = form.save()
        self.assertEqual(timezone.localtime(eleicao.inicio).strftime('%H:%M'), '13:38')
        self.assertEqual(timezone.localtime(eleicao.fim).strftime('%H:%M'), '17:01')
        self.assertEqual(eleicao.status, 'agendada')

    # --- resultados ---
    def test_resultado_publicado_apos_encerrar(self):
        Voto.objects.create(eleicao=self.eleicao, aluno=self.aluno, opcao=self.op1)
        self.eleicao.fim = timezone.now() - timedelta(minutes=1)
        self.eleicao.save()
        self.client.login(username=self.aluno.ra, password=self.aluno.ra)
        r = self.client.get(reverse('resultados'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Chapa 1')
