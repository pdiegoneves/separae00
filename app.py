import streamlit as st
import pandas as pd
import numpy as np

def definir_deposito(endereco : str) -> str:
    if endereco in ["TUBOS", "D10TELHAS", "TELHAS"]:
        return "08"
    elif endereco in ["BLOCADOP7", "BLOCTINTASS", "BLOCPORTAS", "TUBOS", "D10TELHAS", "TELHAS"]:
        return "BLOCADO"
    else:
        return endereco[:2]

def definir_nivel(endereco : str) -> str:
    deposito = definir_deposito(endereco)
    rua = endereco[2:4]
    predio = endereco[4:7]
    nivel = endereco[7:9]
    palete = endereco[9:11]
    apartamento = endereco[11:13]

    if endereco in ["BLOCADOP7", "BLOCTINTASS", "BLOCPORTAS", "D10TELHAS", "TELHAS"]:
        return "BLOCADO"
    elif deposito == "04":
        return "PISO"
    elif endereco == "DOCA":
        return "CORTE"
    elif endereco == "RECEBIMENTO":
        return "RECEBIMENTO"
    elif endereco in ["DOCA", "RECECEBIMENTO"]:
        return ""
    elif deposito == "10":
        return "PICKING"
    elif deposito == "01" and rua >= "16" and nivel > "00":
        return "AEREO"
    elif deposito == "01" and rua >= "18" and nivel > "00":
        return "AEREO"
    elif deposito == "05" and nivel > "00":
        return "AEREO"
    elif deposito == "06" and nivel > "00":
        return "AEREO"
    elif deposito == "07" and nivel > "01":
        return "AEREO"
    elif nivel > "02":
        return "AEREO"
    else:
        return "PICKING"

st.set_page_config(
    page_title="E00 - Transferências para lojas", 
    page_icon="📦", 
    layout="wide")

col1, col2 = st.columns([1, 11])

col1.image("./assets/logo.svg")
col2.write("<h1 style='text-align: center;'>E00 - Transferências para lojas</h1>", unsafe_allow_html=True)

file = st.file_uploader("Escolha o arquivo", type="xlsx")

if file:
    df = pd.read_excel(file, header=1, dtype="object")
    df["Deposito"] = df["Endereco"].apply(lambda x: definir_deposito(x))
    df["Nivel"] = df["Endereco"].apply(lambda x: definir_nivel(x))
    df = df.groupby(["Nivel", "Deposito"]).size().reset_index(name="qtd")
    df.set_index("Nivel", inplace=True)
    df_pivot = df.pivot_table(index='Nivel', columns='Deposito', values='qtd', aggfunc='sum')
    df_pivot.fillna(0, inplace=True)
    df_pivot.replace({np.nan: 0}, inplace=True)
    df_pivot = df_pivot.astype(int)
    df_pivot["Total"] = df_pivot.sum(axis=1)
    df_pivot.loc['Totais'] = df_pivot.sum()

    col1 , col2 = st.columns(2)
    
    with col1:
        col1_1, col1_2 = st.columns([1, 4])
        col1_1.image("./assets/logo.svg")
        col1_2.subheader("Separação de E00")
        st.dataframe(df_pivot, use_container_width=True)

    with col2:
        st.subheader("Total de E00 por Nível")
        df_bar = df_pivot.drop(["Totais"], axis=0) 
        st.bar_chart(df_bar.reset_index(), x="Nivel", y = "Total")


    df_bar = df_pivot.drop(["Total"], axis=1).T
    st.bar_chart(df_bar.reset_index(), x="Deposito", y = "Totais")
