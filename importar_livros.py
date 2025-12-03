#!/usr/bin/env python
"""
Script para importar livros da API Open Library para o banco de dados.
Busca 5.000 livros e insere diretamente no banco SQLite usando Django.
"""

import os
import sys
import time
import textwrap

# Adicionar o diretório do projeto ao Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import django

# Configurar Django antes de importar models/connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

import requests
import sqlite3
from django.db import connection, transaction
from django.conf import settings

BASE_URL = "https://openlibrary.org/search.json"
TOTAL_LIVROS = 5000
LIMITE_POR_PAGINA = 100  # máximo padrão da Search API
CONSULTA = "subject:fiction"  # busca por assunto para trazer muitos livros


def buscar_pagina(offset: int):
    """Busca uma página de resultados no Open Library usando offset."""
    params = {
        "q": CONSULTA,
        "limit": LIMITE_POR_PAGINA,
        "offset": offset,
    }
    try:
        resp = requests.get(BASE_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return data.get("docs", [])
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar offset {offset}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Resposta da API: {e.response.text[:200]}")
        return []


def gerar_descricao(titulo: str, autor: str) -> str:
    """Gera uma descrição curta, original, em português."""
    base = (
        f'"{titulo}" é um livro real, registrado no catálogo público do Open Library, '
        f'escrito por {autor}. Este registro foi gerado para testes de sistemas de '
        f'biblioteca, focando em consultas, buscas e desempenho em bancos de dados.'
    )
    # garante descrição não muito longa
    return textwrap.shorten(base, width=300, placeholder="...")


def validar_e_truncar(texto: str, max_length: int, campo: str) -> str:
    """Valida e trunca texto para o tamanho máximo permitido."""
    if not texto:
        return ""
    texto = texto.strip()
    if len(texto) > max_length:
        print(f"  Aviso: {campo} truncado de {len(texto)} para {max_length} caracteres")
        return texto[:max_length]
    return texto


def inserir_livros_batch(livros: list):
    """Insere múltiplos livros no banco usando conexão SQLite direta para evitar problemas com % nos dados."""
    if not livros:
        return 0
    
    # Preparar dados validados
    dados_validos = []
    for titulo, autor, descricao in livros:
        # Validar e truncar campos
        titulo = validar_e_truncar(titulo, 200, "Título")
        autor = validar_e_truncar(autor, 200, "Autor")
        
        # Pular se título ou autor estiverem vazios após validação
        if not titulo or not autor:
            continue
        
        desc = descricao if descricao else None
        dados_validos.append((titulo, autor, desc))
    
    if not dados_validos:
        return 0
    
    inseridos = 0
    # Usar conexão SQLite direta para evitar problemas com debug SQL do Django
    db_path = str(settings.DATABASES['default']['NAME'])
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for titulo, autor, desc in dados_validos:
            try:
                cursor.execute(
                    "INSERT INTO books_livro (titulo, autor, descricao) VALUES (?, ?, ?)",
                    (titulo, autor, desc)
                )
                inseridos += 1
            except Exception as e:
                # Escapar % para evitar problemas na formatação da mensagem
                titulo_safe = str(titulo[:50]).replace('%', '%%')
                print(f"  Erro ao inserir livro '{titulo_safe}...': {str(e)}")
                continue
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro na transação: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
    
    return inseridos


def main():
    """Função principal para importar livros."""
    print("=" * 60)
    print("Importador de Livros - Open Library API")
    print("=" * 60)
    print(f"Objetivo: Importar {TOTAL_LIVROS} livros")
    print()
    
    livros_coletados = []
    offset = 0
    total_inseridos = 0
    inicio = time.time()
    
    # Verificar quantos livros já existem
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM books_livro")
        livros_existentes = cursor.fetchone()[0]
    
    print(f"Livros já cadastrados no banco: {livros_existentes}")
    print()
    
    while len(livros_coletados) < TOTAL_LIVROS:
        print(f"Buscando offset {offset}...", end=" ")
        docs = buscar_pagina(offset)
        
        if not docs:
            print("Sem mais resultados na API. Interrompendo.")
            break
        
        print(f"Encontrados {len(docs)} resultados")
        
        # Processar documentos da página
        livros_pagina = []
        for doc in docs:
            titulo = doc.get("title")
            autores = doc.get("author_name") or []
            
            if not titulo or not autores:
                continue
            
            autor = autores[0]
            descricao = gerar_descricao(titulo, autor)
            
            livros_pagina.append((titulo, autor, descricao))
            livros_coletados.append((titulo, autor, descricao))
            
            if len(livros_coletados) >= TOTAL_LIVROS:
                break
        
        # Inserir em lotes para melhor performance
        if livros_pagina:
            inseridos = inserir_livros_batch(livros_pagina)
            total_inseridos += inseridos
            print(f"  → Inseridos {inseridos} livros desta página")
        
        print(f"  Total acumulado: {len(livros_coletados)} coletados, {total_inseridos} inseridos")
        print()
        
        if len(livros_coletados) >= TOTAL_LIVROS:
            break
        
        offset += LIMITE_POR_PAGINA
        
        # Evitar bater muito rápido na API
        time.sleep(0.3)
    
    tempo_total = time.time() - inicio
    
    print("=" * 60)
    print("Importação concluída!")
    print("=" * 60)
    print(f"Total de livros coletados: {len(livros_coletados)}")
    print(f"Total de livros inseridos: {total_inseridos}")
    print(f"Tempo total: {tempo_total:.2f} segundos")
    
    # Verificar total final no banco
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM books_livro")
        total_final = cursor.fetchone()[0]
    
    print(f"Total de livros no banco após importação: {total_final}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nImportação interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

