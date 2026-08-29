# 🗳️ VoteEscola — Sistema de Votação Escolar

Sistema web de votação escolar construído com **Django 4.2 + Bootstrap 5** (responsivo) e **MySQL/MariaDB**.

Permite cadastrar os alunos da escola, criar eleições com **tema** e **janela de votação (início–fim)**, e realizar a votação digital com **1 voto por aluno por eleição**, com painel de resultados e dashboard.

## ✨ Funcionalidades

- 🔐 **Login com níveis de autorização**: Administrador, Gestor, Professor e Aluno
  - **Admin**: gestão completa (eleições, opções, alunos, resultados)
  - **Gestor/Professor**: dashboard, eleições e resultados (somente leitura de dados)
  - **Aluno**: urna digital + consulta dos próprios votos e resultados publicados
- 🗳️ **Urna digital**: valida a **janela de votação** (início–fim) no servidor — fora do horário não vota
- ✅ **1 voto por aluno por eleição** (constraint de unicidade no banco)
- 📊 **Dashboard** com cards (votações abertas/agendadas, eleitores aptos, votos, participação) e gráfico de votos por eleição (Chart.js)
- 📈 **Resultados** com apuração por opção (votos + %) e gráfico de rosca; publicação para alunos opcional após encerrar
- 👥 **Cadastro de alunos**: CRUD completo, busca por nome/RA, ativar/inativar, criação de login (username = RA) e reset de senha
- 📦 **Importação automática** dos alunos do banco `escola` (dashboard_escolar): `python3 manage.py import_alunos`

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13 · Django 4.2 |
| Frontend | Bootstrap 5.3 (CDN) · Chart.js 4 · ícones Bootstrap Icons |
| Banco | MySQL/MariaDB (`voto_escola`) |
| Serviço | systemd (`voto-escola.service`, porta **8013**) |

## 🚀 Executando

```bash
cd /home/pi/python/escola/voto_escola
python3 manage.py migrate
python3 manage.py import_alunos        # opcional: importa alunos do banco escola
python3 manage.py createsuperuser      # perfil admin é criado automaticamente? não — crie via shell ou admin
python3 manage.py runserver 0.0.0.0:8013
```

### Importação de alunos

O comando `import_alunos` lê o banco `escola` (dashboard_escolar) e cria/atualiza os alunos.
As credenciais do banco de origem ficam em **`escola_db.json`** (gitignored):

```json
{ "NAME": "escola", "USER": "escola", "PASSWORD": "...", "HOST": "localhost", "PORT": "3306" }
```

### Testes

```bash
python3 manage.py test   # 9 testes: níveis, janela de votação, voto único, resultados
```

## 🗂️ Estrutura

```
voto_escola/
├── manage.py
├── voto_escola/            # settings/urls do projeto
├── votacao/                # app principal (models, views, forms, testes)
│   └── management/commands/import_alunos.py
├── templates/              # base.html + telas (Bootstrap 5)
├── static/                 # css personalizado
├── legacy/                 # protótipo estático original (17/Jun/2026)
└── escola_db.json          # (gitignored) credenciais do banco escola p/ import
```

## 🧩 Modelo de dados

- **Aluno**: RA (único), nome, turma, série, escola, ativo, usuário vinculado
- **Eleicao**: tema, descrição, **início**, **fim** (janela de votação), ativa, publicar resultados
- **Opcao**: opção/chapa vinculada a uma eleição (nome, descrição, ordem)
- **Voto**: eleição + aluno + opção (único por par eleição/aluno)
- **Perfil**: nível de autorização do usuário (admin/gestor/professor/aluno)

## 🔒 Segurança

- Senhas: hash padrão do Django (PBKDF2)
- Janela de votação validada **no servidor** (não confia no cliente)
- Voto único garantido por constraint `unique_together(eleicao, aluno)`
- Permissões por nível via decorator `@nivel_requerido(...)`

## 📝 Notas

- Rodando com `runserver` (padrão dos apps do pip5). Para produção real, trocar por gunicorn/uWSGI + nginx.
- Repositório: `https://github.com/pro-nestor-figueiredo/voto_escola` (privado)
