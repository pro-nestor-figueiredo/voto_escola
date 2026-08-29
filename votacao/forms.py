from django import forms
from django.utils import timezone

from .models import Aluno, Eleicao, Opcao


class EleicaoForm(forms.ModelForm):
    """Criação/edição de eleição com janela de votação (início–fim)."""

    class Meta:
        model = Eleicao
        fields = ['titulo', 'descricao', 'inicio', 'fim', 'ativa', 'publicar_resultados']
        widgets = {
            'inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'fim': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M',
            ),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: Escolha do Grêmio Estudantil'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Converte datetime p/ o formato aceito pelo input datetime-local
        for f in ('inicio', 'fim'):
            if self.instance and getattr(self.instance, f, None):
                self.initial[f] = getattr(self.instance, f).strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get('inicio')
        fim = cleaned.get('fim')
        # O input datetime-local envia horário sem fuso → assume horário local (America/Sao_Paulo)
        for f in ('inicio', 'fim'):
            v = cleaned.get(f)
            if v is not None and timezone.is_naive(v):
                cleaned[f] = timezone.make_aware(v, timezone.get_current_timezone())
        if inicio and fim and fim <= inicio:
            raise forms.ValidationError('O fim da votação deve ser depois do início.')
        return cleaned


class OpcaoForm(forms.ModelForm):
    class Meta:
        model = Opcao
        fields = ['nome', 'descricao', 'ordem']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da opção/chapa'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ordem': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['ra', 'nome', 'turma', 'serie', 'escola', 'ativo']
        widgets = {
            'ra': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex.: 1234567'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'turma': forms.TextInput(attrs={'class': 'form-control'}),
            'serie': forms.TextInput(attrs={'class': 'form-control'}),
            'escola': forms.TextInput(attrs={'class': 'form-control'}),
        }
