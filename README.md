# Booksearch - Projeto Django

Projeto Django para busca de livros.

## Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório (se aplicável):
```bash
git clone <url-do-repositorio>
cd Booksearch
```

2. Crie e ative o ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Executando o Projeto

1. Certifique-se de que o ambiente virtual está ativado:
```bash
source venv/bin/activate
```

2. Execute as migrações (se necessário):
```bash
python manage.py migrate
```

3. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

4. Acesse o projeto em: http://127.0.0.1:8000/

## Comandos Úteis

- Criar uma nova app: `python manage.py startapp <nome_da_app>`
- Criar migrações: `python manage.py makemigrations`
- Aplicar migrações: `python manage.py migrate`
- Criar superusuário: `python manage.py createsuperuser`
- Acessar shell Django: `python manage.py shell`

## Estrutura do Projeto

```
Booksearch/
├── booksearch/          # Configurações do projeto Django
├── manage.py           # Script de gerenciamento Django
├── requirements.txt    # Dependências do projeto
├── venv/              # Ambiente virtual (não versionado)
└── README.md          # Este arquivo

```
