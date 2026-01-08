import pandas as pd
import os
import unicodedata

# ---------------------------
# Função para normalizar texto
# ---------------------------
def normalizar(texto):
    if pd.isna(texto):
        return texto
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.strip().upper()

# ---------------------------
# Ler planilha geral
# ---------------------------
geral = pd.read_csv("geral.csv", sep=";")

geral["Cliente"] = geral["Cliente"].apply(normalizar)

# Criar coluna Vendedor (numérica)
geral["Vendedor"] = pd.Series(dtype="Int64")

# ---------------------------
# Pasta com planilhas dos vendedores
# ---------------------------
pasta_vendedores = "vendedores"
numero_vendedor = 1

for arquivo in sorted(os.listdir(pasta_vendedores)):
    if arquivo.endswith(".csv"):
        caminho = os.path.join(pasta_vendedores, arquivo)

        df_vendedor = pd.read_csv(caminho, sep=";")
        df_vendedor["Cliente"] = df_vendedor["Cliente"].apply(normalizar)

        mask = geral["Cliente"].isin(df_vendedor["Cliente"]) & geral["Vendedor"].isna()

        geral.loc[mask, "Vendedor"] = numero_vendedor

        print(f"Vendedor {numero_vendedor} atribuído para {mask.sum()} clientes")

        numero_vendedor += 1

# ---------------------------
# Salvar resultado
# ---------------------------
geral.to_excel("geral_com_vendedor_numero.xlsx", index=False)

print("Processo finalizado com sucesso!")
