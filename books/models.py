from django.db import models


class Livro(models.Model):
    """Model para representar um livro no banco de dados.
    
    Nota: Este model é usado apenas para criar a estrutura da tabela.
    Todas as operações de leitura/escrita devem ser feitas com SQL puro.
    """
    titulo = models.CharField(max_length=200, verbose_name='Título')
    autor = models.CharField(max_length=200, verbose_name='Autor')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    
    class Meta:
        db_table = 'books_livro'
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
    
    def __str__(self):
        return f"{self.titulo} - {self.autor}"
