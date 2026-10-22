# Oficina: Testes automatizados no Django com Pytest

API de uma biblioteca feita com **Django 5.2** e **Django REST Framework**, usada
como ponto de partida para a oficina de testes automatizados.

A ideia é partir de um projeto que **já funciona, mas não tem nenhum teste**, e
durante a oficina escrever os testes, medir a cobertura e fazer o GitHub
bloquear Pull Requests que quebrem alguma coisa.

## Branches

| Branch | O que tem |
|---|---|
| `inicio` | O projeto funcionando, **sem nenhum teste**. É daqui que a oficina começa. |
| `final` | O mesmo projeto com a configuração de testes, os testes da oficina, a cobertura e o workflow do GitHub Actions. Cada etapa da apresentação é um commit. |

## Como rodar

Pré-requisito: Python 3.12 ou mais novo.

```bash
# 1. Crie e ative o ambiente virtual
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Crie o banco (SQLite) e os dados de demonstração
python manage.py migrate
python manage.py seed_demo

# 4. Suba o servidor
python manage.py runserver
```

A API fica em <http://127.0.0.1:8000/api/>. Pelo navegador dá para usar a
interface do DRF: faça login em <http://127.0.0.1:8000/api-auth/login/> com um
dos usuários abaixo para navegar autenticado.

### Usuários de demonstração

O `seed_demo` pode ser executado quantas vezes você quiser: ele não duplica
nada. No final, ele imprime o token de cada usuário.

| Usuário | Senha | Papel |
|---|---|---|
| `bibliotecaria` | `senha-demo-123` | bibliotecária (grupo `Librarian`) |
| `aluno` | `senha-demo-123` | membro |

Ele também cria 3 autores e 6 livros (o livro "Laços de Família" tem só 1
exemplar, bom para demonstrar a regra de "sem exemplares disponíveis").

### Testando com curl

```bash
# Login (devolve o token)
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "aluno", "password": "senha-demo-123"}'

# Usando o token
curl http://127.0.0.1:8000/api/books/ -H "Authorization: Token <seu-token>"

# Pegando um livro emprestado
curl -X POST http://127.0.0.1:8000/api/books/1/borrow/ -H "Authorization: Token <seu-token>"
```

## Papéis

- **Bibliotecário**: usuário no grupo `Librarian` (o grupo é criado por uma
  data migration). Superusers também contam como bibliotecários.
- **Membro**: qualquer outro usuário autenticado. Quem se cadastra pela API é
  sempre membro.

## Rotas e permissões

Todas as rotas exigem autenticação, exceto cadastro e login.

### Autenticação (`/api/auth/`)

| Método | Rota | Quem pode | O que faz |
|---|---|---|---|
| POST | `/api/auth/register/` | qualquer um | Cria um membro (`username`, `email`, `password`, `password_confirm`) e devolve o token |
| POST | `/api/auth/login/` | qualquer um | Recebe `username` e `password` e devolve o token |
| POST | `/api/auth/logout/` | autenticado | Apaga o token do usuário |
| GET | `/api/auth/me/` | autenticado | Dados do usuário logado, incluindo `is_librarian` |

### Biblioteca (`/api/`)

| Método | Rota | Quem pode | O que faz |
|---|---|---|---|
| GET | `/api/authors/` | autenticado | Lista autores |
| POST/PUT/PATCH/DELETE | `/api/authors/...` | bibliotecário | CRUD de autores |
| GET | `/api/books/` | autenticado | Lista livros com `available_copies` |
| GET | `/api/books/{id}/` | autenticado | Detalhe do livro |
| POST/PUT/PATCH/DELETE | `/api/books/...` | bibliotecário | CRUD de livros |
| POST | `/api/books/{id}/borrow/` | autenticado | Pega o livro emprestado |
| GET | `/api/loans/` | autenticado | Membro vê só os seus empréstimos; bibliotecário vê todos |
| GET | `/api/loans/{id}/` | dono ou bibliotecário | Detalhe do empréstimo |
| POST | `/api/loans/{id}/return/` | dono ou bibliotecário | Devolve o livro |

## Regras de negócio

| Onde | Regra |
|---|---|
| `Book` (model) | `available_copies` = total de exemplares menos empréstimos ativos (não devolvidos) |
| `BookSerializer` | título obrigatório (espaços extras são removidos) |
| `BorrowSerializer` | não empresta se não houver exemplar disponível nem se o usuário já tiver 3 empréstimos ativos |
| `LoanViewSet.return_loan` | não devolve duas vezes o mesmo empréstimo |
| `permissions.py` | `IsLibrarianOrReadOnly` (permissão por papel) e `IsOwnerOrLibrarian` (permissão por objeto) |

O prazo do empréstimo é de 14 dias. As constantes ficam no topo de
`library/models.py`.

## O que falta

Este é o ponto de partida: o projeto **não tem nenhum teste**. Durante a
oficina vamos:

1. Instalar o Pytest e o pytest-django (e também pytest-cov e Model Bakery).
2. Configurar o `pytest.ini`.
3. Escrever os testes: validação sem banco, model e regras com banco,
   permissões e as rotas da API.
4. Medir a cobertura de testes.
5. Criar o workflow do GitHub Actions que roda os testes em cada Pull Request.

O resultado final está na branch `final`.
