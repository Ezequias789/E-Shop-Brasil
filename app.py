
import os
from pathlib import Path
from urllib.parse import quote_plus
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError


# =====================================================
# 1. CONFIGURACAO E VARIAVEIS DE AMBIENTE
# =====================================================

st.set_page_config(
    page_title="E-Shop Brasil",
    page_icon="🛒",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env", override=False)

MONGO_USER = os.getenv("MONGO_USER", "eshop")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "eshop_brasil")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

if not MONGO_PASSWORD:
    st.error(
        "Senha do MongoDB não encontrada. "
        "Verifique o arquivo .env."
    )
    st.stop()

MONGO_URI = (
    f"mongodb://{quote_plus(MONGO_USER)}:"
    f"{quote_plus(MONGO_PASSWORD)}"
    f"@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin"
)


# =====================================================
# 2. CONEXAO COM MONGODB
# =====================================================

@st.cache_resource
def conectar_mongodb():

    cliente = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    cliente.admin.command("ping")

    return cliente


try:

    cliente_mongo = conectar_mongodb()

    banco = cliente_mongo[MONGO_DATABASE]

    clientes = banco["clientes"]
    produtos = banco["produtos"]
    pedidos = banco["pedidos"]

    st.success("MongoDB conectado com sucesso!")

except PyMongoError as erro:

    st.error(f"Erro ao conectar ao MongoDB: {erro}")
    st.stop()


# =====================================================
# 3. FUNCOES AUXILIARES
# =====================================================

def carregar_dados(colecao):

    dados = list(colecao.find())

    for item in dados:

        item["_id"] = str(item["_id"])

        for campo, valor in item.items():

            if isinstance(valor, ObjectId):
                item[campo] = str(valor)

    return pd.DataFrame(dados)


def formatar_moeda(valor):

    return (
        f"R$ {float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def obter_mapa(registros):

    return {
        str(registro["_id"]): registro
        for registro in registros
    }


def excluir_pedido(id_pedido):

    pedido = pedidos.find_one({
        "_id": ObjectId(id_pedido)
    })

    if not pedido:
        return False

    # Recuperar estoque se o pedido nao estiver cancelado
    if pedido.get("status") != "Cancelado":

        resultado = produtos.update_one(

            {
                "_id": ObjectId(pedido["produto_id"])
            },

            {
                "$inc": {
                    "estoque": int(pedido["quantidade"])
                }
            }

        )

        if resultado.matched_count == 0:
            return False

    pedidos.delete_one({
        "_id": ObjectId(id_pedido)
    })

    return True


# =====================================================
# 4. DADOS DE DEMONSTRACAO
# =====================================================

def inserir_dados_exemplo():

    if (
        clientes.count_documents({}) > 0
        or produtos.count_documents({}) > 0
        or pedidos.count_documents({}) > 0
    ):

        st.warning(
            "Já existem dados cadastrados. "
            "Os exemplos não foram inseridos para evitar duplicações."
        )

        return

    lista_clientes = [

        {
            "nome": "João Silva",
            "email": "joao@email.com",
            "cidade": "Fortaleza",
            "estado": "CE"
        },

        {
            "nome": "Maria Santos",
            "email": "maria@email.com",
            "cidade": "Sobral",
            "estado": "CE"
        },

        {
            "nome": "Pedro Oliveira",
            "email": "pedro@email.com",
            "cidade": "Tianguá",
            "estado": "CE"
        },

        {
            "nome": "Ana Costa",
            "email": "ana@email.com",
            "cidade": "São Paulo",
            "estado": "SP"
        },

        {
            "nome": "Lucas Souza",
            "email": "lucas@email.com",
            "cidade": "Recife",
            "estado": "PE"
        }

    ]

    lista_produtos = [

        {
            "nome": "Notebook",
            "categoria": "Eletrônicos",
            "preco": 3500.00,
            "estoque": 15
        },

        {
            "nome": "Smartphone",
            "categoria": "Eletrônicos",
            "preco": 2200.00,
            "estoque": 30
        },

        {
            "nome": "Teclado Mecânico",
            "categoria": "Periféricos",
            "preco": 250.00,
            "estoque": 40
        },

        {
            "nome": "Mouse Gamer",
            "categoria": "Periféricos",
            "preco": 150.00,
            "estoque": 50
        },

        {
            "nome": "Monitor",
            "categoria": "Eletrônicos",
            "preco": 1200.00,
            "estoque": 20
        }

    ]

    resultado_clientes = clientes.insert_many(
        lista_clientes
    )

    resultado_produtos = produtos.insert_many(
        lista_produtos
    )

    ids_clientes = resultado_clientes.inserted_ids
    ids_produtos = resultado_produtos.inserted_ids

    lista_pedidos = []

    for i in range(5):

        quantidade = i + 1

        lista_pedidos.append({

            "cliente_id": str(ids_clientes[i]),

            "produto_id": str(ids_produtos[i]),

            "quantidade": quantidade,

            "valor_total": (
                lista_produtos[i]["preco"] * quantidade
            ),

            "status": "Concluído",

            "data": datetime.now()

        })

        produtos.update_one(

            {"_id": ids_produtos[i]},

            {
                "$inc": {
                    "estoque": -quantidade
                }
            }

        )

    pedidos.insert_many(lista_pedidos)

    st.success(
        "Dados de demonstração inseridos com sucesso!"
    )


# =====================================================
# 5. CABECALHO E MENU
# =====================================================

st.title("🛒 E-Shop Brasil")

st.subheader(
    "Sistema de Gestão e Análise de Dados"
)

st.caption(
    "Gerenciamento de clientes, produtos, pedidos e análise de dados"
)

st.sidebar.title("🛒 Menu de navegação")

pagina = st.sidebar.radio(

    "Selecione uma área:",

    [
        "Dashboard",
        "Clientes",
        "Produtos",
        "Pedidos",
        "Análise e Consultas"
    ]

)

st.sidebar.divider()

st.sidebar.subheader("Dados de demonstração")

if st.sidebar.button("Inserir dados de exemplo"):

    try:

        inserir_dados_exemplo()
        st.rerun()

    except PyMongoError as erro:

        st.sidebar.error(
            f"Erro ao inserir dados: {erro}"
        )

st.sidebar.caption(
    "Os dados utilizados na demonstração são fictícios."
)


# =====================================================
# 6. DASHBOARD
# =====================================================

if pagina == "Dashboard":

    st.header("📊 Dashboard geral")

    df_clientes = carregar_dados(clientes)
    df_produtos = carregar_dados(produtos)
    df_pedidos = carregar_dados(pedidos)

    total_clientes = len(df_clientes)
    total_produtos = len(df_produtos)
    total_pedidos = len(df_pedidos)

    faturamento = 0

    if not df_pedidos.empty:

        pedidos_validos = df_pedidos[
            df_pedidos["status"] != "Cancelado"
        ]

        faturamento = float(
            pedidos_validos["valor_total"].sum()
        )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Clientes",
        total_clientes
    )

    col2.metric(
        "Produtos",
        total_produtos
    )

    col3.metric(
        "Pedidos",
        total_pedidos
    )

    col4.metric(
        "Faturamento",
        formatar_moeda(faturamento)
    )

    st.divider()

    # Grafico de categorias

    if not df_produtos.empty:

        st.subheader("Produtos por categoria")

        dados_categoria = (

            df_produtos
            .groupby("categoria")
            .size()
            .reset_index(name="quantidade")

        )

        grafico = px.pie(

            dados_categoria,

            names="categoria",

            values="quantidade",

            title="Distribuição de produtos por categoria",

            hole=0.4

        )

        st.plotly_chart(
            grafico,
            use_container_width=True
        )

    # Grafico de vendas

    if not df_pedidos.empty:

        st.subheader("Valores dos pedidos")

        dados_grafico = df_pedidos.copy()

        dados_grafico = dados_grafico[
            dados_grafico["status"] != "Cancelado"
        ]

        if not dados_grafico.empty:

            dados_grafico["pedido"] = (
                dados_grafico["_id"].str[-6:]
            )

            grafico_vendas = px.bar(

                dados_grafico,

                x="pedido",

                y="valor_total",

                color="status",

                title="Valor dos pedidos",

                labels={

                    "pedido": "Pedido",

                    "valor_total": "Valor (R$)",

                    "status": "Status"

                }

            )

            st.plotly_chart(
                grafico_vendas,
                use_container_width=True
            )

    # Controle de estoque

    if not df_produtos.empty:

        st.subheader("Controle de estoque")

        st.dataframe(

            df_produtos[
                ["nome", "categoria", "estoque"]
            ],

            use_container_width=True,

            hide_index=True

        )


# =====================================================
# 7. GERENCIAMENTO DE CLIENTES
# =====================================================

elif pagina == "Clientes":

    st.header("👥 Gerenciamento de clientes")

    cadastrar, editar, excluir, consultar = st.tabs(

        [
            "Cadastrar",
            "Editar",
            "Excluir",
            "Consultar"
        ]

    )

    # Cadastro

    with cadastrar:

        st.subheader("Cadastrar novo cliente")

        with st.form("form_cliente"):

            nome = st.text_input("Nome completo")

            email = st.text_input("E-mail")

            cidade = st.text_input("Cidade")

            estado = st.text_input("Estado (UF)")

            enviar = st.form_submit_button(
                "Cadastrar cliente"
            )

            if enviar:

                if (
                    nome.strip()
                    and email.strip()
                    and cidade.strip()
                    and estado.strip()
                ):

                    email_normalizado = email.strip().lower()

                    if "@" not in email_normalizado:

                        st.warning(
                            "Informe um e-mail válido."
                        )

                    elif clientes.count_documents({
                        "email": email_normalizado
                    }) > 0:

                        st.warning(
                            "Este e-mail já está cadastrado."
                        )

                    else:

                        try:

                            clientes.insert_one({

                                "nome": nome.strip(),

                                "email": email_normalizado,

                                "cidade": cidade.strip(),

                                "estado": estado.strip().upper()

                            })

                            st.success(
                                "Cliente cadastrado com sucesso!"
                            )

                            st.rerun()

                        except PyMongoError as erro:

                            st.error(
                                f"Erro ao cadastrar cliente: {erro}"
                            )

                else:

                    st.warning(
                        "Preencha todos os campos."
                    )

    # Edicao

    with editar:

        st.subheader("Editar cliente")

        lista = list(
            clientes.find().sort("nome", 1)
        )

        mapa_clientes = obter_mapa(lista)

        if lista:

            id_cliente = st.selectbox(

                "Selecione o cliente",

                list(mapa_clientes.keys()),

                format_func=lambda x: mapa_clientes[x]["nome"],

                key="editar_cliente"

            )

            cliente_escolhido = mapa_clientes[id_cliente]

            with st.form("form_editar_cliente"):

                novo_nome = st.text_input(

                    "Nome",

                    value=cliente_escolhido.get("nome", "")

                )

                novo_email = st.text_input(

                    "E-mail",

                    value=cliente_escolhido.get("email", "")

                )

                nova_cidade = st.text_input(

                    "Cidade",

                    value=cliente_escolhido.get("cidade", "")

                )

                novo_estado = st.text_input(

                    "Estado",

                    value=cliente_escolhido.get("estado", "")

                )

                salvar = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar:

                    email_normalizado = (
                        novo_email.strip().lower()
                    )

                    if (
                        novo_nome.strip()
                        and "@" in email_normalizado
                    ):

                        email_existente = clientes.count_documents({

                            "email": email_normalizado,

                            "_id": {
                                "$ne": ObjectId(id_cliente)
                            }

                        })

                        if email_existente > 0:

                            st.warning(
                                "Este e-mail pertence a outro cliente."
                            )

                        else:

                            clientes.update_one(

                                {
                                    "_id": ObjectId(id_cliente)
                                },

                                {
                                    "$set": {

                                        "nome": novo_nome.strip(),

                                        "email": email_normalizado,

                                        "cidade": nova_cidade.strip(),

                                        "estado": novo_estado.strip().upper()

                                    }
                                }

                            )

                            st.success(
                                "Cliente atualizado com sucesso!"
                            )

                            st.rerun()

                    else:

                        st.warning(
                            "Informe nome e e-mail válido."
                        )

        else:

            st.info(
                "Nenhum cliente cadastrado."
            )

    # Exclusao

    with excluir:

        st.subheader("Excluir cliente")

        lista = list(clientes.find())

        mapa_clientes = obter_mapa(lista)

        if lista:

            id_cliente = st.selectbox(

                "Escolha o cliente para excluir",

                list(mapa_clientes.keys()),

                format_func=lambda x: mapa_clientes[x]["nome"],

                key="excluir_cliente"

            )

            st.warning(
                "Clientes vinculados a pedidos não podem ser excluídos."
            )

            if st.button("Confirmar exclusão do cliente"):

                quantidade_pedidos = pedidos.count_documents({

                    "cliente_id": id_cliente

                })

                if quantidade_pedidos > 0:

                    st.error(
                        "Este cliente possui pedidos vinculados. "
                        "Exclua os pedidos antes."
                    )

                else:

                    clientes.delete_one({

                        "_id": ObjectId(id_cliente)

                    })

                    st.success(
                        "Cliente excluído com sucesso!"
                    )

                    st.rerun()

        else:

            st.info(
                "Nenhum cliente cadastrado."
            )

    # Consulta

    with consultar:

        st.subheader("Lista de clientes")

        df = carregar_dados(clientes)

        if not df.empty:

            pesquisa = st.text_input(
                "Pesquisar cliente por nome"
            )

            if pesquisa:

                df = df[
                    df["nome"].str.contains(
                        pesquisa,
                        case=False,
                        na=False
                    )
                ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhum cliente cadastrado."
            )


# =====================================================
# 8. GERENCIAMENTO DE PRODUTOS
# =====================================================

elif pagina == "Produtos":

    st.header("📦 Gerenciamento de produtos")

    cadastrar, editar, excluir, consultar = st.tabs(

        [
            "Cadastrar",
            "Editar",
            "Excluir",
            "Consultar"
        ]

    )

    categorias = [

        "Eletrônicos",

        "Periféricos",

        "Moda",

        "Casa",

        "Outros"

    ]

    # Cadastro

    with cadastrar:

        st.subheader("Cadastrar produto")

        with st.form("form_produto"):

            nome = st.text_input("Nome do produto")

            categoria = st.selectbox(
                "Categoria",
                categorias
            )

            preco = st.number_input(

                "Preço (R$)",

                min_value=0.01,

                value=100.00

            )

            estoque = st.number_input(

                "Quantidade em estoque",

                min_value=0,

                step=1

            )

            enviar = st.form_submit_button(
                "Cadastrar produto"
            )

            if enviar:

                if nome.strip():

                    produtos.insert_one({

                        "nome": nome.strip(),

                        "categoria": categoria,

                        "preco": float(preco),

                        "estoque": int(estoque)

                    })

                    st.success(
                        "Produto cadastrado com sucesso!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "Informe o nome do produto."
                    )

    # Edicao

    with editar:

        st.subheader("Editar produto")

        lista = list(
            produtos.find().sort("nome", 1)
        )

        mapa_produtos = obter_mapa(lista)

        if lista:

            id_produto = st.selectbox(

                "Selecione o produto",

                list(mapa_produtos.keys()),

                format_func=lambda x: mapa_produtos[x]["nome"],

                key="editar_produto"

            )

            produto_escolhido = mapa_produtos[id_produto]

            categoria_atual = produto_escolhido.get(
                "categoria",
                "Outros"
            )

            with st.form("form_editar_produto"):

                novo_nome = st.text_input(

                    "Nome",

                    value=produto_escolhido.get("nome", "")

                )

                nova_categoria = st.selectbox(

                    "Categoria",

                    categorias,

                    index=(
                        categorias.index(categoria_atual)
                        if categoria_atual in categorias
                        else categorias.index("Outros")
                    )

                )

                novo_preco = st.number_input(

                    "Preço",

                    min_value=0.01,

                    value=max(
                        0.01,
                        float(produto_escolhido.get("preco", 1.0))
                    )

                )

                novo_estoque = st.number_input(

                    "Estoque",

                    min_value=0,

                    value=max(
                        0,
                        int(produto_escolhido.get("estoque", 0))
                    )

                )

                salvar = st.form_submit_button(
                    "Salvar alterações"
                )

                if salvar:

                    if novo_nome.strip():

                        produtos.update_one(

                            {
                                "_id": ObjectId(id_produto)
                            },

                            {
                                "$set": {

                                    "nome": novo_nome.strip(),

                                    "categoria": nova_categoria,

                                    "preco": float(novo_preco),

                                    "estoque": int(novo_estoque)

                                }
                            }

                        )

                        st.success(
                            "Produto atualizado com sucesso!"
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "Informe o nome do produto."
                        )

        else:

            st.info(
                "Nenhum produto cadastrado."
            )

    # Exclusao

    with excluir:

        st.subheader("Excluir produto")

        lista = list(produtos.find())

        mapa_produtos = obter_mapa(lista)

        if lista:

            id_produto = st.selectbox(

                "Escolha o produto",

                list(mapa_produtos.keys()),

                format_func=lambda x: mapa_produtos[x]["nome"],

                key="excluir_produto"

            )

            st.warning(
                "Produtos vinculados a pedidos não podem ser excluídos."
            )

            if st.button("Confirmar exclusão do produto"):

                quantidade_pedidos = pedidos.count_documents({

                    "produto_id": id_produto

                })

                if quantidade_pedidos > 0:

                    st.error(
                        "Este produto possui pedidos vinculados. "
                        "Exclua os pedidos antes."
                    )

                else:

                    produtos.delete_one({

                        "_id": ObjectId(id_produto)

                    })

                    st.success(
                        "Produto excluído com sucesso!"
                    )

                    st.rerun()

        else:

            st.info(
                "Nenhum produto cadastrado."
            )

    # Consulta

    with consultar:

        st.subheader("Lista de produtos")

        df = carregar_dados(produtos)

        if not df.empty:

            pesquisa = st.text_input(
                "Pesquisar produto"
            )

            if pesquisa:

                df = df[
                    df["nome"].str.contains(
                        pesquisa,
                        case=False,
                        na=False
                    )
                ]

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhum produto cadastrado."
            )


# =====================================================
# 9. GERENCIAMENTO DE PEDIDOS
# =====================================================

elif pagina == "Pedidos":

    st.header("🛍️ Gerenciamento de pedidos")

    cadastrar, editar, excluir, consultar = st.tabs(

        [
            "Cadastrar",
            "Editar status",
            "Excluir",
            "Consultar"
        ]

    )

    # Cadastro

    with cadastrar:

        st.subheader("Registrar novo pedido")

        lista_clientes = list(
            clientes.find().sort("nome", 1)
        )

        lista_produtos = list(
            produtos.find().sort("nome", 1)
        )

        mapa_clientes = obter_mapa(lista_clientes)

        mapa_produtos = obter_mapa(lista_produtos)

        if lista_clientes and lista_produtos:

            with st.form("form_pedido"):

                id_cliente = st.selectbox(

                    "Cliente",

                    list(mapa_clientes.keys()),

                    format_func=lambda x: mapa_clientes[x]["nome"]

                )

                id_produto = st.selectbox(

                    "Produto",

                    list(mapa_produtos.keys()),

                    format_func=lambda x: (

                        mapa_produtos[x]["nome"]

                        + " - "

                        + formatar_moeda(
                            mapa_produtos[x]["preco"]
                        )

                    )

                )

                quantidade = st.number_input(

                    "Quantidade",

                    min_value=1,

                    value=1,

                    step=1

                )

                produto_atual = mapa_produtos[id_produto]

                total = (
                    float(produto_atual["preco"])
                    * int(quantidade)
                )

                st.write(
                    f"**Valor total: {formatar_moeda(total)}**"
                )

                st.write(
                    f"Estoque disponível: {produto_atual['estoque']}"
                )

                enviar = st.form_submit_button(
                    "Registrar pedido"
                )

                if enviar:

                    try:

                        resultado_estoque = produtos.update_one(

                            {

                                "_id": ObjectId(id_produto),

                                "estoque": {
                                    "$gte": int(quantidade)
                                }

                            },

                            {

                                "$inc": {
                                    "estoque": -int(quantidade)
                                }

                            }

                        )

                        if resultado_estoque.modified_count == 0:

                            st.error(
                                "Estoque insuficiente ou produto indisponível."
                            )

                        else:

                            try:

                                pedidos.insert_one({

                                    "cliente_id": id_cliente,

                                    "produto_id": id_produto,

                                    "quantidade": int(quantidade),

                                    "valor_total": total,

                                    "status": "Pendente",

                                    "data": datetime.now()

                                })

                                st.success(
                                    "Pedido registrado com sucesso!"
                                )

                                st.rerun()

                            except PyMongoError:

                                produtos.update_one(

                                    {
                                        "_id": ObjectId(id_produto)
                                    },

                                    {
                                        "$inc": {
                                            "estoque": int(quantidade)
                                        }
                                    }

                                )

                                st.error(
                                    "Erro ao registrar o pedido. "
                                    "O estoque foi restaurado."
                                )

                    except PyMongoError as erro:

                        st.error(
                            f"Erro ao registrar pedido: {erro}"
                        )

        else:

            st.warning(
                "Cadastre pelo menos um cliente e um produto primeiro."
            )

    # Edicao do status

    with editar:

        st.subheader("Atualizar status do pedido")

        lista = list(
            pedidos.find().sort("data", -1)
        )

        mapa_pedidos = obter_mapa(lista)

        if lista:

            id_pedido = st.selectbox(

                "Selecione o pedido",

                list(mapa_pedidos.keys()),

                format_func=lambda x: x[-8:],

                key="editar_pedido"

            )

            pedido_escolhido = mapa_pedidos[id_pedido]

            status_atual = pedido_escolhido.get(
                "status",
                "Pendente"
            )

            opcoes_status = [

                "Pendente",

                "Em preparação",

                "Enviado",

                "Concluído",

                "Cancelado"

            ]

            if status_atual not in opcoes_status:
                opcoes_status.append(status_atual)

            with st.form("form_status"):

                novo_status = st.selectbox(

                    "Novo status",

                    opcoes_status,

                    index=opcoes_status.index(status_atual)

                )

                salvar = st.form_submit_button(
                    "Atualizar pedido"
                )

                if salvar:

                    estoque_ok = True

                    quantidade = int(
                        pedido_escolhido["quantidade"]
                    )

                    id_produto = pedido_escolhido["produto_id"]

                    if (
                        status_atual != "Cancelado"
                        and novo_status == "Cancelado"
                    ):

                        resultado = produtos.update_one(

                            {
                                "_id": ObjectId(id_produto)
                            },

                            {
                                "$inc": {
                                    "estoque": quantidade
                                }
                            }

                        )

                        if resultado.matched_count == 0:
                            estoque_ok = False

                    elif (
                        status_atual == "Cancelado"
                        and novo_status != "Cancelado"
                    ):

                        resultado = produtos.update_one(

                            {

                                "_id": ObjectId(id_produto),

                                "estoque": {
                                    "$gte": quantidade
                                }

                            },

                            {

                                "$inc": {
                                    "estoque": -quantidade
                                }

                            }

                        )

                        if resultado.modified_count == 0:
                            estoque_ok = False

                    if not estoque_ok:

                        st.error(
                            "Não foi possível atualizar o pedido "
                            "porque o produto não existe ou não há estoque suficiente."
                        )

                    else:

                        pedidos.update_one(

                            {
                                "_id": ObjectId(id_pedido)
                            },

                            {
                                "$set": {
                                    "status": novo_status
                                }
                            }

                        )

                        st.success(
                            "Status atualizado com sucesso!"
                        )

                        st.rerun()

        else:

            st.info(
                "Nenhum pedido cadastrado."
            )

    # Exclusao

    with excluir:

        st.subheader("Excluir pedido")

        lista = list(
            pedidos.find().sort("data", -1)
        )

        mapa_pedidos = obter_mapa(lista)

        if lista:

            id_pedido = st.selectbox(

                "Selecione o pedido",

                list(mapa_pedidos.keys()),

                format_func=lambda x: x[-8:],

                key="excluir_pedido"

            )

            st.warning(
                "A exclusão de um pedido não pode ser desfeita."
            )

            if st.button("Confirmar exclusão do pedido"):

                try:

                    resultado = excluir_pedido(id_pedido)

                    if resultado:

                        st.success(
                            "Pedido excluído e estoque atualizado!"
                        )

                        st.rerun()

                    else:

                        st.error(
                            "Não foi possível excluir o pedido. "
                            "Verifique se o produto ainda existe."
                        )

                except PyMongoError as erro:

                    st.error(
                        f"Erro ao excluir pedido: {erro}"
                    )

        else:

            st.info(
                "Nenhum pedido cadastrado."
            )

    # Consulta

    with consultar:

        st.subheader("Lista de pedidos")

        df = carregar_dados(pedidos)

        if not df.empty:

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Nenhum pedido cadastrado."
            )


# =====================================================
# 10. ANALISE, CONSULTAS E CONCATENACAO
# =====================================================

elif pagina == "Análise e Consultas":

    st.header("🔎 Análise e consultas de dados")

    df_clientes = carregar_dados(clientes)

    df_produtos = carregar_dados(produtos)

    df_pedidos = carregar_dados(pedidos)

    # Pesquisa por status

    st.subheader("Pesquisa de pedidos")

    if not df_pedidos.empty:

        status_lista = sorted(
            df_pedidos["status"]
            .dropna()
            .unique()
            .tolist()
        )

        status_filtro = st.selectbox(

            "Filtrar pedidos por status",

            ["Todos"] + status_lista

        )

        resultado = df_pedidos.copy()

        if status_filtro != "Todos":

            resultado = resultado[
                resultado["status"] == status_filtro
            ]

        st.dataframe(
            resultado,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "Não existem pedidos para consultar."
        )

    st.divider()

    # Concatenacao dos dados

    st.subheader("Concatenação de dados")

    if (
        not df_pedidos.empty
        and not df_clientes.empty
        and not df_produtos.empty
    ):

        clientes_merge = df_clientes.rename(

            columns={

                "_id": "cliente_doc_id",

                "nome": "nome_cliente"

            }

        )

        produtos_merge = df_produtos.rename(

            columns={

                "_id": "produto_doc_id",

                "nome": "nome_produto"

            }

        )

        dados_combinados = df_pedidos.merge(

            clientes_merge,

            left_on="cliente_id",

            right_on="cliente_doc_id",

            how="left"

        )

        dados_combinados = dados_combinados.merge(

            produtos_merge,

            left_on="produto_id",

            right_on="produto_doc_id",

            how="left"

        )

        colunas = [

            "nome_cliente",

            "email",

            "cidade",

            "nome_produto",

            "categoria",

            "quantidade",

            "valor_total",

            "status"

        ]

        st.write(
            "Dados combinados de clientes, produtos e pedidos:"
        )

        st.dataframe(

            dados_combinados[colunas],

            use_container_width=True,

            hide_index=True

        )

        st.download_button(

            "📥 Baixar relatório CSV",

            dados_combinados[colunas].to_csv(
                index=False
            ).encode("utf-8-sig"),

            file_name="relatorio_eshop.csv",

            mime="text/csv"

        )

    else:

        st.info(
            "Cadastre clientes, produtos e pedidos "
            "para visualizar a concatenação."
        )

    st.divider()

    # Resumo estatistico

    st.subheader("Resumo estatístico")

    if not df_pedidos.empty:

        pedidos_validos = df_pedidos[
            df_pedidos["status"] != "Cancelado"
        ]

        if not pedidos_validos.empty:

            estatisticas = (

                pedidos_validos["valor_total"]
                .describe()
                .to_frame()

            )

            st.write(
                "Estatísticas dos valores dos pedidos:"
            )

            st.dataframe(
                estatisticas,
                use_container_width=True
            )

        else:

            st.info(
                "Não existem pedidos ativos para análise."
            )

    else:

        st.info(
            "Ainda não existem dados suficientes para análise."
        )


# =====================================================
# 11. RODAPE
# =====================================================

st.divider()

st.caption(
    "E-Shop Brasil | Projeto acadêmico de Advanced Databases and Big Data"
)
