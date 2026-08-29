"""Importa os alunos do banco 'escola' (dashboard_escolar) para o voto_escola.

Uso:
    python3 manage.py import_alunos [--dry-run]

As credenciais do banco origem ficam em escola_db.json (gitignored).
RA = campo identificacao (RA SED completo). Alunos já existentes são atualizados.
"""

import json
from pathlib import Path

import MySQLdb
from django.core.management.base import BaseCommand

from votacao.models import Aluno


class Command(BaseCommand):
    help = 'Importa/atualiza alunos do banco escola (dashboard_escolar).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Apenas mostra o que seria feito.')
        parser.add_argument('--escola', type=str, default='',
                            help='Importa apenas alunos desta escola (ex.: "Santa Olimpia").')

    def handle(self, *args, **opts):
        cfg_path = Path(__file__).resolve().parent.parent.parent.parent / 'escola_db.json'
        if not cfg_path.exists():
            self.stderr.write(self.style.ERROR(
                f'escola_db.json não encontrado em {cfg_path}. Crie com as credenciais do banco escola.'
            ))
            return

        cfg = json.loads(cfg_path.read_text())
        conn = MySQLdb.connect(
            host=cfg.get('HOST', 'localhost'),
            port=int(cfg.get('PORT', 3306)),
            user=cfg['USER'],
            passwd=cfg['PASSWORD'],
            db=cfg['NAME'],
            charset='utf8mb4',
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT a.identificacao, a.nome, a.ativo, e.nome
            FROM core_aluno a JOIN core_escola e ON e.id = a.escola_id
            WHERE a.identificacao <> ''
            ORDER BY a.nome
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        escola_filtro = opts.get('escola', '').strip()
        if escola_filtro:
            antes = len(rows)
            rows = [r for r in rows if r[3] == escola_filtro]
            self.stdout.write(f'Filtro por escola "{escola_filtro}": {antes} -> {len(rows)} linhas.')

        criados = atualizados = ignorados = 0
        for ra, nome, ativo, escola in rows:
            ra = ra.strip()
            if not ra:
                ignorados += 1
                continue
            defaults = dict(nome=nome.strip(), ativo=bool(ativo), escola=escola)
            aluno, created = Aluno.objects.update_or_create(ra=ra, defaults=defaults)
            if created:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(self.style.SUCCESS(
            f'Importação concluída: {criados} criados, {atualizados} atualizados, {ignorados} ignorados '
            f'(total de linhas lidas: {len(rows)}).'
        ))
