# +Aula — Sistema de Gestão de Aulas

Aplicação web de gestão escolar desenvolvida em Python, Flask, Flask-SQLAlchemy, SQLite/MySQL, HTML, CSS e JavaScript. O sistema organiza usuários, turmas, atividades e entregas em uma arquitetura separada por responsabilidades.

## Como executar

Requisitos: Python 3.10 ou superior.

```bash
cd backend
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

**Linux/macOS:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abra `http://localhost:5000` no navegador. Por padrão, o sistema usa SQLite e cria/atualiza `backend/mais_aulas.db`.

### Configurar MySQL (opcional)

Copie `backend/.env.example` para `backend/.env` e configure `DATABASE_URL` com os dados do seu ambiente. Crie o banco usando `backend/database/create_database.sql`. Não publique o arquivo `.env` nem credenciais no repositório.

## Arquitetura

```text
backend/
  controllers/   # recebem requisições HTTP e devolvem respostas
  services/      # validam e coordenam cada caso de uso
  models/        # entidades SQLAlchemy e persistência CRUD
  repositories/  # consultas específicas, filtros e relatórios
  database/      # script de criação do banco
frontend/
  templates/     # páginas HTML
  static/css/    # estilos
  static/js/     # consumo da API e interações
 docs/
  diagrama-classes.mmd
```

O fluxo das operações é **Interface → API Flask → Controller → Service → Model/Repository → Banco de Dados**. As Controllers são classes, cada caso de uso possui um Service específico, as Models concentram a persistência CRUD e o Repository encapsula consultas especializadas.

## Funcionalidades Implementadas

### Usuários
1. Cadastrar usuário.
2. Listar usuários.
3. Atualizar usuário.
4. Excluir usuário.
5. Buscar usuários pelo nome, com correspondência parcial e sem diferenciar maiúsculas/minúsculas.

### Turmas
6. Cadastrar turma e associar um responsável.
7. Listar turmas.
8. Atualizar turma.
9. Excluir turma.
10. Filtrar turmas pelo responsável selecionado.

### Atividades
11. Cadastrar atividade e associá-la a uma turma.
12. Listar atividades.
13. Atualizar atividade.
14. Excluir atividade.
15. Filtrar atividades por intervalo de data de entrega.

### Entregas
16. Registrar entrega associada a uma atividade e a um usuário.
17. Listar entregas.
18. Atualizar entrega, status e nota.
19. Excluir entrega.
20. Filtrar entregas pelo status.
21. Filtrar entregas por intervalo de data.

### Dashboard e relatórios
22. Consultar resumo do dashboard com contagens de usuários, turmas, atividades, entregas e pendências.
23. Gerar relatório de entregas por atividade, com total, concluídas, atrasadas e média das notas; a interface permite selecionar a atividade e imprimir o relatório.

Os filtros são processados na API e consultam o banco por meio de Services e Repository; não dependem apenas de filtrar os registros já carregados no navegador.

### Acesso

A tela inicial pede login ou cadastro de conta para entrar no aplicativo. A senha fica apenas como hash. Depois do acesso, o token é enviado em `Authorization: Bearer`. A lista de usuários da escola continua no modal da página Usuários e não substitui essa conta.

### Configurações

A tela de configurações salva preferências locais de apresentação no navegador (`localStorage`); esse recurso não foi contado entre as funcionalidades integradas ao banco. As preferências valem nesta instalação e passam a alterar a interface:

- nome, função e mensagem da saudação, com as iniciais no avatar
- nome da escola e ano letivo exibidos no topo
- tema claro, escuro ou igual ao sistema
- densidade confortável ou compacta nas listas
- confirmação antes de excluir um registro
- quantidade de itens nos painéis do início
- exibir ou ocultar os cartões da página de turmas
- prévia imediata e restauração dos padrões

## Diagrama de classes

O diagrama de classes do domínio está em [`docs/diagrama-classes.mmd`](docs/diagrama-classes.mmd). Ele representa as Models, seus principais atributos e relacionamentos.

## Rotas da API

| Método | Rota | Finalidade |
|---|---|---|
| POST | `/api/auth/cadastro` | Criar conta e entrar; público |
| POST | `/api/auth/login` | Entrar com e-mail e senha; público |
| POST | `/api/auth/logout` | Encerrar a sessão atual |
| GET | `/api/auth/me` | Dados da conta autenticada |
| GET, POST | `/api/usuarios` | Listar/cadastrar usuários; aceita `?nome=` para busca |
| PUT, DELETE | `/api/usuarios/<id>` | Atualizar/excluir usuário |
| GET, POST | `/api/turmas` | Listar/cadastrar turmas; aceita `?user_id=` |
| PUT, DELETE | `/api/turmas/<id>` | Atualizar/excluir turma |
| GET, POST | `/api/atividades` | Listar/cadastrar atividades; aceita `?data_inicio=&data_fim=` |
| PUT, DELETE | `/api/atividades/<id>` | Atualizar/excluir atividade |
| GET, POST | `/api/entregas` | Listar/cadastrar entregas; aceita `?status=&data_inicio=&data_fim=` |
| PUT, DELETE | `/api/entregas/<id>` | Atualizar/excluir entrega |
| GET | `/api/dashboard` | Resumo de indicadores |
| GET | `/api/relatorios?atividade_id=` | Relatório geral ou por atividade |
| GET | `/api/health` | Verificar disponibilidade da API; público |

As demais rotas `/api` exigem o token. Sem ele, a resposta é `401`.

## Banco de dados

O sistema cria as tabelas a partir das Models com `db.create_all()`. O script SQL para criação do banco MySQL está em `backend/database/create_database.sql`. A aplicação utiliza SQLite por padrão, facilitando a execução local.
