# 🛒 E-Shop Brasil — Advanced Databases and Big Data

## 1. Introdução

A E-Shop Brasil é uma empresa fictícia de comércio eletrônico que enfrenta desafios relacionados ao gerenciamento de grandes volumes de dados, controle de estoque, personalização da experiência dos clientes e eficiência logística.

Com o crescimento das operações, torna-se necessário utilizar tecnologias capazes de armazenar, organizar, manipular e analisar grandes quantidades de informações.

Este projeto apresenta uma aplicação desenvolvida para simular o gerenciamento de dados de uma empresa de comércio eletrônico, utilizando tecnologias de banco de dados NoSQL, programação Python e ferramentas de análise e visualização de dados.

## 2. Objetivo

Desenvolver uma aplicação funcional capaz de armazenar, manipular, consultar e visualizar informações de clientes, produtos e pedidos.

A solução utiliza MongoDB para armazenamento dos dados, Docker para executar o banco de dados em um container e Streamlit para disponibilizar uma interface gráfica interativa.

O projeto também demonstra como a manipulação e a análise de dados podem contribuir para melhorar o controle de estoque, acompanhar vendas e apoiar a tomada de decisões.

## 3. Tecnologias utilizadas

- **Python:** linguagem de programação utilizada no desenvolvimento da aplicação.
- **MongoDB:** banco de dados não relacional (NoSQL) utilizado para armazenar clientes, produtos e pedidos.
- **Docker Desktop:** ferramenta utilizada para executar o MongoDB em um container.
- **Docker Compose:** utilizado para configurar e iniciar o ambiente do banco de dados.
- **Streamlit:** framework utilizado para desenvolver a interface gráfica da aplicação.
- **Pandas:** biblioteca utilizada para manipulação, organização e combinação dos dados.
- **Plotly:** biblioteca utilizada para criação de gráficos interativos.
- **PyMongo:** biblioteca responsável pela comunicação entre Python e MongoDB.
- **Python-dotenv:** utilizado para carregar as configurações e credenciais do arquivo `.env`.
- **GitHub:** plataforma utilizada para disponibilização do código-fonte.

## 4. Descrição da aplicação

A aplicação E-Shop Brasil possui uma interface administrativa desenvolvida com Streamlit e integrada ao MongoDB.

O sistema permite gerenciar informações de clientes, produtos e pedidos, além de realizar consultas e apresentar indicadores e gráficos.

### 4.1. Gerenciamento de clientes

- Cadastro de novos clientes.
- Edição de informações cadastradas.
- Exclusão de clientes que não possuem pedidos vinculados.
- Consulta de clientes.
- Pesquisa por nome.
- Armazenamento das informações no MongoDB.

### 4.2. Gerenciamento de produtos

- Cadastro de produtos.
- Edição de informações.
- Exclusão de produtos sem pedidos vinculados.
- Consulta de produtos.
- Organização por categorias.
- Controle de estoque.

### 4.3. Gerenciamento de pedidos

- Registro de novos pedidos.
- Associação entre clientes e produtos.
- Cálculo automático do valor total.
- Atualização automática do estoque após uma venda.
- Alteração do status dos pedidos.
- Consulta e exclusão de pedidos.
- Recuperação do estoque quando um pedido é cancelado ou excluído.

### 4.4. Dashboard e análise de dados

O sistema possui um painel administrativo com indicadores e gráficos interativos.

São apresentados:

- Quantidade total de clientes.
- Quantidade total de produtos.
- Quantidade total de pedidos.
- Faturamento dos pedidos não cancelados.
- Distribuição de produtos por categoria.
- Gráfico dos valores dos pedidos.
- Informações sobre o estoque.

### 4.5. Manipulação e concatenação de dados

A aplicação realiza consultas ao MongoDB e utiliza Pandas para organizar e combinar informações provenientes das coleções de clientes, produtos e pedidos.

Essa funcionalidade permite visualizar em uma única tabela informações como:

- Nome e e-mail do cliente.
- Cidade.
- Nome e categoria do produto.
- Quantidade comprada.
- Valor total do pedido.
- Status do pedido.

Também é possível exportar os dados combinados para um arquivo CSV.

### 4.6. Dados de demonstração

A aplicação possui uma funcionalidade para inserir dados fictícios de demonstração no MongoDB.

Os dados incluem clientes, produtos e pedidos, permitindo testar as funcionalidades de cadastro, edição, exclusão, consultas, concatenação e visualização.

A inserção de exemplos é realizada somente quando as coleções estão vazias, evitando duplicações dos dados.

## 5. Estrutura do projeto

O projeto está organizado da seguinte maneira:

```text
E-Shop-Brasil/
│
├── README.md
├── app.py
├── requirements.txt
├── docker-compose.yml
├── .env.example
├── .gitignore
│
└── exemplos/
    ├── dashboard.png
    ├── clientes.png
    ├── cadastro_cliente.png
    ├── produtos.png
    ├── cadastro_produto.png
    ├── pedidos.png
    ├── cadastro_pedido.png
    └── concatenacao.png
```

**Observação:** o arquivo `.env` e a pasta `.venv` são configurações locais e não devem ser enviados ao GitHub.

## 6. Como executar o projeto

### 6.1. Pré-requisitos

Para executar a aplicação, é necessário possuir:

- Python instalado.
- Visual Studio Code.
- Docker Desktop.
- Docker Compose.

### 6.2. Obter o projeto

Clone o repositório do GitHub ou faça o download dos arquivos do projeto.

Abra a pasta `E-Shop-Brasil` no Visual Studio Code.

### 6.3. Configurar as variáveis de ambiente

Crie uma cópia do arquivo de exemplo:

```powershell
Copy-Item .env.example .env
```

Abra o arquivo `.env` e configure as credenciais utilizadas pelo MongoDB.

Exemplo:

```env
MONGO_USER=eshop
MONGO_PASSWORD=sua_senha_aqui
MONGO_DATABASE=eshop_brasil
MONGO_PORT=27017
MONGO_HOST=localhost
```

Substitua `sua_senha_aqui` pela senha definida para o banco de dados.

O arquivo `.env` contém informações privadas e não deve ser publicado no GitHub.

### 6.4. Iniciar o MongoDB pelo Docker

Abra o Docker Desktop e execute o seguinte comando no terminal do projeto:

```powershell
docker compose up -d
```

Esse comando realiza o download da imagem do MongoDB, quando necessário, e inicia o container configurado no Docker Compose.

Para verificar se o container está funcionando:

```powershell
docker ps
```

O container do MongoDB deverá aparecer com o nome `eshop-mongodb`.

### 6.5. Criar o ambiente virtual Python

Execute:

```powershell
py -m venv .venv
```

Ative o ambiente virtual no Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Caso o PowerShell bloqueie a execução do script, utilize:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Depois tente ativar novamente.

### 6.6. Instalar as dependências

Com o ambiente virtual ativado, execute:

```powershell
pip install -r requirements.txt
```

Esse comando instala todas as bibliotecas necessárias para executar a aplicação.

### 6.7. Executar a aplicação Streamlit

Com o MongoDB em execução e as dependências instaladas, execute:

```powershell
python -m streamlit run app.py
```

A aplicação será disponibilizada localmente no endereço:

```text
http://localhost:8501
```

O navegador poderá abrir automaticamente a interface do sistema.

## 7. Testes realizados

Foram realizados testes das principais funcionalidades da aplicação:

- Inserção de clientes no MongoDB.
- Edição de informações dos clientes.
- Exclusão de clientes sem pedidos vinculados.
- Pesquisa e consulta de clientes.
- Cadastro e edição de produtos.
- Consulta de produtos e controle de estoque.
- Registro de pedidos.
- Cálculo automático do valor das compras.
- Atualização automática do estoque após a venda.
- Alteração do status dos pedidos.
- Consulta e exclusão de pedidos.
- Combinação de informações de diferentes coleções.
- Exportação de relatórios em CSV.
- Visualização de indicadores e gráficos no Dashboard.
- Verificação da conexão entre Python e MongoDB.

## 8. Evidências do funcionamento

As capturas de tela das funcionalidades estão disponíveis na pasta `exemplos`.

Os arquivos demonstram o funcionamento do Dashboard, gerenciamento de clientes, gerenciamento de produtos, gerenciamento de pedidos e concatenação de dados.

## 9. Segurança e proteção das informações

O projeto utiliza um arquivo `.env` para armazenar as configurações de conexão com o MongoDB, evitando manter as credenciais diretamente no código Python.

O arquivo `.gitignore` impede que configurações privadas, ambiente virtual e arquivos temporários sejam publicados no repositório.

Os dados utilizados na demonstração são fictícios e não representam informações reais de clientes.

Em um ambiente de produção, também seriam necessárias medidas adicionais de autenticação, autorização, criptografia, controle de acesso e proteção de dados pessoais, considerando os princípios da Lei Geral de Proteção de Dados (LGPD).

## 10. Considerações finais

O desenvolvimento do projeto permitiu aplicar conhecimentos relacionados a bancos de dados não relacionais, armazenamento de informações, manipulação de dados e ferramentas de Big Data.

A integração entre MongoDB, Docker, Python, Pandas, Plotly e Streamlit demonstra como diferentes tecnologias podem trabalhar em conjunto para desenvolver uma solução de gerenciamento de dados para uma empresa de comércio eletrônico.

A aplicação desenvolvida representa uma proposta prática para melhorar a organização das informações, o controle de estoque, o acompanhamento de pedidos e a visualização de indicadores importantes para a tomada de decisões.

**Projeto acadêmico desenvolvido para a disciplina Advanced Databases and Big Data.**