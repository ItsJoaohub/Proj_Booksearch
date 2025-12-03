import time

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection

from books import local_cache


def home(request):
    """View para exibir a página inicial do projeto."""
    return render(request, 'books/home.html')


def listar_livros(request):
    """View para listar todos os livros cadastrados usando SQL puro."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro ORDER BY id")
        livros = cursor.fetchall()
    
    # Converter tuplas em dicionários para facilitar no template
    livros_list = []
    for livro in livros:
        livros_list.append({
            'id': livro[0],
            'titulo': livro[1],
            'autor': livro[2],
            'descricao': livro[3] if livro[3] else 'Sem descrição',
        })
    
    return render(request, 'books/listar.html', {'livros': livros_list})


def buscar_livro(request):
    """View para exibir a página de busca de livros e executar os três métodos de busca."""
    query = request.GET.get('q', '').strip()
    context = {'query': query}
    resultados = {}
    
    if query:
        # Detectar se o termo é numérico (ID) ou texto (título)
        is_id = query.isdigit()
        
        # Busca Sequencial
        resultado_seq, tempo_seq = _busca_sequencial(query, is_id)
        resultados['sequencial'] = {
            'resultado': resultado_seq,
            'tempo_execucao': f"{tempo_seq:.4f}",
            'metodo': 'Busca Sequencial'
        }
        
        # Busca Indexada
        resultado_idx, tempo_idx = _busca_indexada(query, is_id)
        resultados['indexada'] = {
            'resultado': resultado_idx,
            'tempo_execucao': f"{tempo_idx:.4f}",
            'metodo': 'Busca Indexada'
        }
        
        # Busca HashMap
        resultado_hash, tempo_hash = _busca_hashmap(query, is_id)
        resultados['hashmap'] = {
            'resultado': resultado_hash,
            'tempo_execucao': f"{tempo_hash:.4f}",
            'metodo': 'Busca com HashMap'
        }
    
    context['resultados'] = resultados
    return render(request, 'books/buscar.html', context)


def _busca_sequencial(termo, is_id):
    """Executa busca sequencial percorrendo todos os livros."""
    resultado = None
    start_time = time.time()
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro")
        livros = cursor.fetchall()
        
        for livro in livros:
            # Comparar por ID se for numérico, senão por título
            if is_id:
                if str(livro[0]) == termo:
                    resultado = {
                        'id': livro[0],
                        'titulo': livro[1],
                        'autor': livro[2],
                        'descricao': livro[3] if livro[3] else 'Sem descrição',
                    }
                    break
            else:
                if livro[1] and livro[1].lower() == termo.lower():
                    resultado = {
                        'id': livro[0],
                        'titulo': livro[1],
                        'autor': livro[2],
                        'descricao': livro[3] if livro[3] else 'Sem descrição',
                    }
                    break
    
    end_time = time.time()
    tempo_execucao = (end_time - start_time) * 1000  # Convertendo para ms
    
    return resultado, tempo_execucao


def _busca_indexada(termo, is_id):
    """Executa busca indexada usando SQL com WHERE (aproveita índices do banco)."""
    resultado = None
    start_time = time.time()
    
    with connection.cursor() as cursor:
        if is_id:
            cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro WHERE id = %s", [int(termo)])
        else:
            cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro WHERE LOWER(titulo) = LOWER(%s)", [termo])
        
        row = cursor.fetchone()
        if row:
            resultado = {
                'id': row[0],
                'titulo': row[1],
                'autor': row[2],
                'descricao': row[3] if row[3] else 'Sem descrição',
            }
    
    end_time = time.time()
    tempo_execucao = (end_time - start_time) * 1000  # Convertendo para ms
    
    return resultado, tempo_execucao


def _busca_hashmap(termo, is_id):
    """
    Executa busca usando HashMap (dicionário Python).
    
    COMO O PYTHON IMPLEMENTA UM HASH MAP (DICIONÁRIO):
    
    1. Estrutura Base: O Python aloca um array contíguo de memória (vetor).
    2. Função de Hash: Ao acessar `dict[chave]`, o Python calcula `hash(chave)`.
    3. Índice: O valor do hash é transformado em um índice do array.
    4. Acesso O(1): O programa pula diretamente para esse endereço de memória,
       sem precisar percorrer a lista (como na busca sequencial).
    """
    resultado = None
    start_time = time.time()
    
    if is_id:
        # Buscar hashmap indexado por ID
        mapa_livros = local_cache.get_hashmap_id()
        
        if mapa_livros is None:
            # Construir o hashmap se não existir
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro")
                livros = cursor.fetchall()
                
                # Construindo o HashMap indexado por ID
                mapa_livros = {str(livro[0]): livro for livro in livros}
                
                # Salva no cache local
                local_cache.set_hashmap_id(mapa_livros)
        
        if termo in mapa_livros:
            livro = mapa_livros[termo]
            resultado = {
                'id': livro[0],
                'titulo': livro[1],
                'autor': livro[2],
                'descricao': livro[3] if livro[3] else 'Sem descrição',
            }
    else:
        # Buscar hashmap indexado por título
        mapa_livros = local_cache.get_hashmap_titulo()
        
        if mapa_livros is None:
            # Construir o hashmap se não existir
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, titulo, autor, descricao FROM books_livro")
                livros = cursor.fetchall()
                
                # Construindo o HashMap indexado por título (case-insensitive)
                mapa_livros = {livro[1].lower(): livro for livro in livros if livro[1]}
                
                # Salva no cache local
                local_cache.set_hashmap_titulo(mapa_livros)
        
        if termo.lower() in mapa_livros:
            livro = mapa_livros[termo.lower()]
            resultado = {
                'id': livro[0],
                'titulo': livro[1],
                'autor': livro[2],
                'descricao': livro[3] if livro[3] else 'Sem descrição',
            }
    
    end_time = time.time()
    tempo_execucao = (end_time - start_time) * 1000  # Convertendo para ms
    
    return resultado, tempo_execucao


def cadastrar_livro(request):
    """View para exibir o formulário de cadastro de livros."""
    return render(request, 'books/cadastrar.html')


def limpar_cache(request):
    """View para limpar o cache do HashMap."""
    local_cache.clear_cache()
    messages.success(request, 'Cache do HashMap limpo com sucesso! O cache será reconstruído na próxima busca.')
    return redirect('buscar_livro')


def salvar_livro(request):
    """View para processar e salvar um novo livro no banco usando SQL puro."""
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        autor = request.POST.get('autor', '').strip()
        descricao = request.POST.get('descricao', '').strip()
        
        # Validação básica
        if not titulo:
            messages.error(request, 'O título é obrigatório.')
            return render(request, 'books/cadastrar.html', {
                'titulo': titulo,
                'autor': autor,
                'descricao': descricao,
            })
        
        if not autor:
            messages.error(request, 'O autor é obrigatório.')
            return render(request, 'books/cadastrar.html', {
                'titulo': titulo,
                'autor': autor,
                'descricao': descricao,
            })
        
        # Inserir no banco usando SQL puro
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO books_livro (titulo, autor, descricao) VALUES (%s, %s, %s)",
                    [titulo, autor, descricao if descricao else None]
                )
            messages.success(request, f'Livro "{titulo}" cadastrado com sucesso!')
            return redirect('cadastrar_livro')
        except Exception as e:
            messages.error(request, f'Erro ao salvar o livro: {str(e)}')
            return render(request, 'books/cadastrar.html', {
                'titulo': titulo,
                'autor': autor,
                'descricao': descricao,
            })
    
    # Se não for POST, redireciona para o formulário
    return redirect('cadastrar_livro')
