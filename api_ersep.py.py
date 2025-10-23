from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI(title="API Tarifas ERSeP", version="1.0.0")

# Permitir acceso desde cualquier origen (útil para GPT o front-end)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar el tarifario (debe estar en la misma carpeta)
df = pd.read_pickle("tarifario.pkl")

def normalizar(x: str) -> str:
    return (str(x).strip().lower()
            .replace("á","a").replace("é","e").replace("í","i")
            .replace("ó","o").replace("ú","u"))

@app.get("/tarifa")
def consultar_tarifa(origen: str = Query(...), destino: str = Query(...)):
    o, d = normalizar(origen), normalizar(destino)
    df_temp = df.copy()
    df_temp["o_norm"] = df_temp["Origen"].astype(str).map(normalizar)
    df_temp["d_norm"] = df_temp["Destino"].astype(str).map(normalizar)
    res = df_temp[(df_temp["o_norm"] == o) & (df_temp["d_norm"] == d)]
    if res.empty:
        raise HTTPException(status_code=404, detail="No se encontró tarifa para ese recorrido.")
    cols = ["Empresa", "Origen", "Destino", "KM", "Tarifa_RG13", "Tarifa_RG60", "Vigencia"]
    return {"resultados": res[cols].to_dict(orient="records")}
