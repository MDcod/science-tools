from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
from scipy.optimize import curve_fit
from typing import List

app = FastAPI()

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mdcod.github.io/"],  # Разрешить запросы с любых доменов (можно указать конкретные)
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешить все заголовки
)

# Функция модели Бертотти для подгонки
def bertotti_model(x, kh, kc, ke):
    f, Bm, d, rho = x
    Ph = kh * f * Bm**2
    Pc = kc * (f * Bm * d)**2 / rho
    Pa = ke * (f * Bm)**1.5
    return Ph + Pc + Pa

# API модель для входных данных
class LossesInput(BaseModel):
    f: float
    Bm: float
    kh: float
    kc: float
    ke: float
    d: float
    rho: float

# API модель для данных подгонки коэффициентов
class FitDataInput(BaseModel):
    data: List[List[float]]  # [[f, Bm, d, rho, P], ...]

@app.post("/calculate_losses")
def calculate_losses(input_data: LossesInput):
    Ph = input_data.kh * input_data.f * input_data.Bm**2
    Pc = input_data.kc * (input_data.f * input_data.Bm * input_data.d)**2 / input_data.rho
    Pa = input_data.ke * (input_data.f * input_data.Bm)**1.5
    P_total = Ph + Pc + Pa
    return {"Ph": Ph, "Pc": Pc, "Pa": Pa, "P_total": P_total}

@app.post("/fit_coefficients")
def fit_coefficients(input_data: FitDataInput):
    try:
        f_data, Bm_data, d_data, rho_data, P_data = zip(*input_data.data)
        x_data = np.array([f_data, Bm_data, d_data, rho_data])
        y_data = np.array(P_data)

        popt, _ = curve_fit(bertotti_model, x_data, y_data, p0=[0.02, 0.0001, 0.001])
        kh_fit, kc_fit, ke_fit = popt

        return {"kh": kh_fit, "kc": kc_fit, "ke": ke_fit}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
