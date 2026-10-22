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

## Rodando os testes

Com o ambiente virtual ativado e as dependências instaladas
(`pip install -r requirements.txt`):

```bash
# Roda todos os testes, mostrando o nome de cada um
pytest -v

# Roda só um arquivo, ou só os testes cujo nome contém uma palavra
pytest library/tests/test_models.py
pytest -k borrow

# Mede a cobertura e falha se ela ficar abaixo de 80%
pytest --cov=authentication --cov=library --cov-report=term-missing --cov-fail-under=80
```

A coluna `Missing` do relatório de cobertura mostra as linhas que nenhum teste
executou.

Os testes usam um banco SQLite temporário, criado pelo pytest-django a partir
das migrations, e não dependem do `seed_demo` nem da ordem em que rodam. As
fixtures compartilhadas (clientes da API, usuários e livro) ficam no
`conftest.py` da raiz.

### Os tipos de teste da oficina

| Arquivo | Tipo de teste | O que mostra |
|---|---|---|
| `library/tests/test_serializers.py` | unitário, **sem banco** | chamar `validate_title` direto, `pytest.raises` e `parametrize` |
| `library/tests/test_models.py` | model, **com banco** | Model Bakery (`prepare`, `make`, `_quantity`) e fixtures |
| `library/tests/test_serializers.py` | regra de negócio, **com banco** | `BorrowSerializer`: `is_valid()` e `errors` |
| `library/tests/test_permissions.py` | permissão isolada | `APIRequestFactory`, permissão por papel e por objeto |
| `library/tests/test_api.py` e `authentication/tests/test_api.py` | rotas da API | `APIClient`, `force_authenticate`, status 200/201/400/401/403 |

### Model Bakery em 30 segundos

```python
baker.prepare(Book)                  # só na memória: não salva, nem precisa de banco
baker.make(Book)                     # salva no banco, inventando os campos obrigatórios
baker.make(Book, title="Django")     # fixa só o que importa para o teste
baker.make(Loan, user=member, _quantity=3)  # cria vários de uma vez
```

Os FKs obrigatórios são criados sozinhos: `baker.make(Loan)` já cria um
`User` e um `Book` (que, por sua vez, ganha um `Author`).

### Etapas da oficina no histórico

Cada etapa da apresentação é um commit desta branch, então dá para
acompanhar com `git log --oneline inicio..final` e `git checkout <commit>`:

1. Configura pytest e pytest-django
2. Testa validação sem banco
3. Adiciona fixtures com Model Bakery
4. Testa permissões
5. Testa as rotas da API
6. Adiciona workflow do GitHub Actions

### GitHub Actions

O workflow `.github/workflows/tests.yml` (**Django Tests**) roda a cada Pull
Request: instala o Python 3.12 e as dependências, executa os testes e mede a
cobertura. Se algum teste falhar ou a cobertura ficar abaixo de 80%, o check
fica vermelho.

O check vermelho, sozinho, só **avisa**: o botão de merge continua liberado.
Para o PR ser **bloqueado de verdade**, configure a proteção da branch:

1. No repositório, vá em **Settings → Branches → Add branch protection rule**
   (ou **Settings → Rules → Rulesets**, na interface nova).
2. Em *Branch name pattern*, coloque a branch que recebe os PRs (por exemplo
   `inicio`).
3. Marque **Require status checks to pass before merging** e procure o check
   do workflow **Django Tests** (o job aparece como `tests`).
4. Salve.

O check só aparece na busca depois que o workflow rodou pelo menos uma vez,
então abra um PR de teste antes de configurar.
