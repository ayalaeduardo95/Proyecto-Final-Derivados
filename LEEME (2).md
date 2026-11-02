# Datos

Todos los archivos provienen de LSEG Workspace. Fechas de corte indicadas por archivo.

| Archivo | Contenido | Aplicativo | Corte |
|---|---|---|---|
| `LSEG_Fundamentales_WMT.xlsx` | 24 trimestres de estados financieros, razones, segmentos | Company Fundamentals | FY2027 Q2, 31-jul-2026 |
| `LSEG_Deuda_WMT.xlsx` | 53 notas y 26 papel comercial, con YTM, Z-spread y precio | Government and Corporate Bonds | 23-oct-2026 |
| `LSEG_Curva_Tesoro_formulas.xlsx` | Curva del Tesoro, 13 plazos | Government Bond Prices (TRADEWEB) | 1-nov-2026 |
| `curva_tesoro.csv` | La misma curva, ya con valores | — | 1-nov-2026 |
| `opciones_18dic2026.csv` | Cadena del vencimiento 18-dic-2026, 11 ejercicios, con griegas | Option Watch | 1-nov-2026 |

**Nota sobre `LSEG_Curva_Tesoro_formulas.xlsx`:** el exportador de LSEG genera fórmulas
en vivo (`=TR(...)`) en lugar de valores. El archivo solo se resuelve al abrirlo en Excel
con el complemento de LSEG conectado. Por eso se incluye `curva_tesoro.csv` con los valores
ya fijados al corte.
