"""
Módulo para cache local de hashmap de livros.
Armazena dicionários indexados por ID e por título para busca rápida.
"""

# Cache global para hashmap indexado por título
_hashmap_titulo = None

# Cache global para hashmap indexado por ID
_hashmap_id = None


def get_hashmap_titulo():
    """Retorna o hashmap indexado por título, ou None se não existir."""
    return _hashmap_titulo


def set_hashmap_titulo(mapa):
    """Define o hashmap indexado por título no cache."""
    global _hashmap_titulo
    _hashmap_titulo = mapa


def get_hashmap_id():
    """Retorna o hashmap indexado por ID, ou None se não existir."""
    return _hashmap_id


def set_hashmap_id(mapa):
    """Define o hashmap indexado por ID no cache."""
    global _hashmap_id
    _hashmap_id = mapa


def clear_cache():
    """Limpa todo o cache (útil para testes ou reset)."""
    global _hashmap_titulo, _hashmap_id
    _hashmap_titulo = None
    _hashmap_id = None


