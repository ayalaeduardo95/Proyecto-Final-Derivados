# Walmart Inc. (WMT.O) — Estructura de deuda, derivados y estrategia de cobertura

**Proyecto Final · Productos Derivados y Administración de Riesgos Corporativos**
EGADE Business School · Maestría en Finanzas · Dr. Raymundo Díaz Robles

**Equipo 6 · Grupo 40**

| Integrante | Matrícula |
|---|---|
| Eduardo Ayala Saldaña | A01192714 |
| Mariann Antonelli Morales Tobias | A01452078 |
| Ulises Salinas López | A00814787 |

Fecha de corte de datos: **1 de noviembre de 2026** · Fuente: **LSEG Workspace**

---

## De qué trata

El proyecto replica, para una empresa real, la decisión que enfrentó Molson Coors en junio de
2007: cómo financiarse más barato y cubrir riesgos de tesorería usando bonos convertibles,
opciones, futuros y swaps. El caso del curso *Molson Coors Brewing Co.: Valuing a Convertible
Bond* (NE90-06-107) es la referencia de método.

La empresa elegida es **Walmart Inc.**, que cotiza en NASDAQ bajo el símbolo WMT
(ISIN US9311421039, CUSIP 931142103).

## Hallazgos principales

1. **El convertible no genera ahorro económico.** Para una emisión a seis años con 25 % de prima
   de conversión, el cupón que deja el instrumento a la par es 0.918 % frente al 5.140 % de la
   deuda recta. Ese aparente ahorro de 422 puntos base tiene un valor presente de **323.4 millones
   de dólares**, idéntico al valor de la opción de conversión entregada al tenedor: **323.4
   millones**. La diferencia es cero. Es la demostración de que no hay *free lunch*.

2. **El dividendo es la única fuente de ejercicio anticipado en una opción de compra americana.**
   Con dividendo cero el premio sobre la europea es exactamente cero, lo que verifica el resultado
   de Merton (1973) con datos de mercado. Con el dividendo real de Walmart el premio aparece y
   crece de forma monótona con su magnitud.

3. **Walmart ya ejecuta el manual de Molson Coors.** De 62,502 millones emitidos históricamente,
   16,604 millones —el 26.6 %— ya fueron retirados, y el patrón no es aleatorio: cerca de la mitad
   del papel con cupón superior al 3 % contra solo 7.2 % del papel de cupón inferior.

4. **La colocación en dólares canadienses exige un cross-currency swap.** Los tramos a 2033 en
   dólares y en dólares canadienses, emitidos el mismo día por el mismo emisor, muestran una
   ventaja de 94 puntos base en rendimiento. Pero el Z-spread va al revés, lo que implica que la
   ventaja es de curva (129 pb) y no de crédito.

5. **Un hallazgo de convención en LSEG.** La plataforma mide el plazo al vencimiento desde la fecha
   calendario corriente, no desde la última operación. Medirlo desde el último trade sesga todas
   las volatilidades implícitas en 72 puntos base.

## Estructura del repositorio

| Carpeta | Entregable | Contenido |
|---|---|---|
| `01_reporte_ejecutivo/` | 1 | Reporte en Word y PDF, 9 páginas |
| `02_dashboard/` | 2 | Dashboard HTML autocontenido con nueve visualizaciones |
| `03_reporte_reproducible/` | 3 | R Markdown y su HTML compilado |
| `04_calculadora/` | 4 | Calculadora interactiva de valoración |
| `05_codigo_python/` | 5 | Módulo de Python y notebook de Colab con salidas |
| `06_prompt_ia/` | 6 | Prompt de IA y nota de correcciones |
| `07_anexo_capturas/` | 7 | Capturas de LSEG con ticker y fecha |
| `08_datos/` | — | Datos originales con su fuente y fecha de corte |

## Cómo reproducir

**Código de Python** — no requiere instalar nada, solo biblioteca estándar:

```bash
python 05_codigo_python/wmt_derivados.py
```

Imprime la validación contra el ejemplo de Hull, la convergencia del árbol a Black-Scholes, la
validación de volatilidades implícitas contra LSEG, el premio de ejercicio anticipado, la
valoración del convertible y el call spread.

**Notebook de Colab** — `05_codigo_python/WMT_Derivados_Colab.ipynb`, con las salidas ya
ejecutadas.

**Reporte en R** — abrir `03_reporte_reproducible/Reporte_Walmart.Rmd` y usar *Knit*. El documento
es autocontenido: los datos van embebidos en el propio código y el único paquete necesario es
`knitr`. Compila sin error ni advertencias en R 4.3.3 con knitr 1.45 y en R 4.6.1 con knitr 1.52.

**Dashboard y calculadora** — abrir los archivos `.html` con doble clic. No requieren internet:
las librerías van embebidas.

## Validación del modelo

| Prueba | Resultado | Referencia |
|---|---|---|
| Put americana del ejemplo de Hull, cap. 21 | 4.4885 | 4.4886 |
| Convergencia del árbol a Black-Scholes, N = 2000 | +0.0004 | — |
| Volatilidad implícita propia contra LSEG, 12 contratos | 20.4 pb de error medio | — |
| Delta del árbol contra LSEG, call K = 125 | 0.4947 | 0.4938 |
| Gamma del árbol contra LSEG, call K = 125 | 0.0285 | 0.0289 |

El modelo está implementado de forma independiente en Python y en R, y ambas implementaciones
convergen al mismo resultado.

## Limitaciones declaradas

- Las calificaciones por agencia a nivel emisor no se obtuvieron de LSEG. El reporte acota el rango
  a partir del Z-spread observado (38.6 pb promedio ponderado) en lugar de afirmar una calificación
  sin fuente.
- Los montos nocionales de derivados del 10-K quedaron pendientes: los campos correspondientes del
  módulo Company Fundamentals vienen vacíos para Walmart en todos los trimestres consultados.
- La volatilidad de 29 % empleada para el convertible proviene de LEAPs a 2.2 años. Extrapolarla a
  seis años es un supuesto, no un dato observado; el reporte presenta la sensibilidad en el rango
  de 20 % a 40 %.

## Fuentes

LSEG Workspace: Company Fundamentals, Government and Corporate Bonds Advanced Search, Option Watch,
Government Bond Prices (fuente de precios TRADEWEB) y Overview.

Hull, J. *Options, Futures and Other Derivatives*, capítulos 15, 19 y 21.
Merton, R. (1973), para la condición de ejercicio anticipado.
Caso del curso: *Molson Coors Brewing Co.: Valuing a Convertible Bond*, notas NE90-06-107.
