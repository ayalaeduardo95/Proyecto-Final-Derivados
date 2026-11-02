"""
Proyecto Final - Productos Derivados y Administracion de Riesgos Corporativos
EGADE Business School - Maestria en Finanzas - Equipo 6, Grupo 40
Eduardo Ayala Saldana (A01192714) | Mariann A. Morales Tobias (A01452078) | Ulises Salinas Lopez (A00814787)

Walmart Inc. (WMT.O) - Valoracion de opciones, arbol binomial americano,
griegas y estructura convertible al estilo Molson Coors (2007).

Fuente de datos: LSEG Workspace. Corte: 30-oct-2026.
"""
import math
from dataclasses import dataclass

# ============================================================
# 1. PARAMETROS DE MERCADO  (LSEG Workspace, corte 30-oct-2026)
# ============================================================
S0       = 123.51      # Precio de cierre WMT.O
DIV      = 0.25        # Dividendo trimestral declarado
T_DIV    = 40/365      # Dias al ex-dividendo (11-dic-2026), desde 01-nov-2026
T_EXP    = 47/365      # Dias al vencimiento  (18-dic-2026), desde 01-nov-2026
                       # NOTA: LSEG mide el plazo desde la fecha calendario corriente,
                       # no desde la fecha del ultimo trade. Verificado por calibracion
                       # inversa contra ImpVol Mid: el sesgo pasa de -72 pb a -6 pb.
RF       = 0.0403      # Tasa libre de riesgo a 47 dias, interpolada de la curva
                       # del Tesoro (LSEG/TRADEWEB 01-nov-2026): 1M 3.97%, 2M 4.08%
SIGMA_LP = 0.29        # Volatilidad de largo plazo (LEAPs 2028-2029)

# ============================================================
# 2. BLACK-SCHOLES-MERTON con dividendo discreto (modelo escrow)
# ============================================================
def _norm_cdf(x):
    return 0.5*(1.0+math.erf(x/math.sqrt(2.0)))

def _norm_pdf(x):
    return math.exp(-0.5*x*x)/math.sqrt(2.0*math.pi)

def pv_dividendos(divs, r):
    """Valor presente de los dividendos discretos anteriores al vencimiento."""
    return sum(d*math.exp(-r*t) for d, t in divs)

def black_scholes(S, K, T, r, sigma, tipo="call", divs=()):
    """Precio europeo. Los dividendos discretos se descuentan del spot (Hull, cap. 15)."""
    S_adj = S - pv_dividendos(divs, r)
    if T <= 0 or sigma <= 0:
        intr = max(S_adj-K, 0.0) if tipo == "call" else max(K-S_adj, 0.0)
        return intr
    d1 = (math.log(S_adj/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    if tipo == "call":
        return S_adj*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)
    return K*math.exp(-r*T)*_norm_cdf(-d2) - S_adj*_norm_cdf(-d1)

def griegas_bs(S, K, T, r, sigma, tipo="call", divs=()):
    """Griegas analiticas. Theta por dia natural, vega y rho por punto porcentual."""
    S_adj = S - pv_dividendos(divs, r)
    d1 = (math.log(S_adj/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    disc = math.exp(-r*T)
    delta = _norm_cdf(d1) if tipo == "call" else _norm_cdf(d1)-1.0
    gamma = _norm_pdf(d1)/(S_adj*sigma*math.sqrt(T))
    vega  = S_adj*_norm_pdf(d1)*math.sqrt(T)/100.0
    if tipo == "call":
        theta = (-S_adj*_norm_pdf(d1)*sigma/(2*math.sqrt(T)) - r*K*disc*_norm_cdf(d2))/365.0
        rho   =  K*T*disc*_norm_cdf(d2)/100.0
    else:
        theta = (-S_adj*_norm_pdf(d1)*sigma/(2*math.sqrt(T)) + r*K*disc*_norm_cdf(-d2))/365.0
        rho   = -K*T*disc*_norm_cdf(-d2)/100.0
    return dict(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)

def vol_implicita(precio, S, K, T, r, tipo="call", divs=(), lo=1e-4, hi=5.0, tol=1e-10):
    """Volatilidad implicita por biseccion sobre Black-Scholes."""
    f = lambda s: black_scholes(S, K, T, r, s, tipo, divs) - precio
    if f(lo)*f(hi) > 0:
        return None
    for _ in range(200):
        mid = 0.5*(lo+hi)
        if abs(hi-lo) < tol:
            break
        if f(lo)*f(mid) <= 0: hi = mid
        else:                 lo = mid
    return 0.5*(lo+hi)

# ============================================================
# 3. ARBOL BINOMIAL COX-ROSS-RUBINSTEIN
# ============================================================
@dataclass
class ResultadoArbol:
    europea: float
    americana: float
    premio_ejercicio: float
    delta: float
    gamma: float
    theta: float
    nodos_ejercicio: int

def arbol_crr(S, K, T, r, sigma, N, tipo="call", americana=True, divs=()):
    """
    Arbol CRR con dividendos discretos por el metodo de escrow (Hull, cap. 21).
    El arbol se construye sobre S* = S - VP(dividendos); el dividendo se
    reincorpora en los nodos anteriores a la fecha ex-dividendo, de modo que el
    valor intrinseco en cada nodo refleja el precio observable de la accion.
    """
    dt = T/N
    u  = math.exp(sigma*math.sqrt(dt))
    d  = 1.0/u
    p  = (math.exp(r*dt) - d)/(u - d)
    disc = math.exp(-r*dt)
    S_star = S - pv_dividendos(divs, r)

    def escrow(i):
        """VP al paso i de los dividendos que aun no se pagan."""
        t = i*dt
        return sum(dv*math.exp(-r*(td-t)) for dv, td in divs if td > t)

    precios = [[S_star*(u**(j))*(d**(i-j)) + escrow(i) for j in range(i+1)] for i in range(N+1)]
    intr = (lambda s: max(s-K, 0.0)) if tipo == "call" else (lambda s: max(K-s, 0.0))

    V = [intr(s) for s in precios[N]]
    nodos_ej = 0
    guardar = {}
    for i in range(N-1, -1, -1):
        Vn = []
        for j in range(i+1):
            cont = disc*(p*V[j+1] + (1-p)*V[j])
            if americana:
                ex = intr(precios[i][j])
                if ex > cont:
                    nodos_ej += 1
                    Vn.append(ex)
                else:
                    Vn.append(cont)
            else:
                Vn.append(cont)
        V = Vn
        if i <= 2:
            guardar[i] = (list(V), list(precios[i]))
    return V[0], nodos_ej, guardar, dict(u=u, d=d, p=p, dt=dt)

def valuar_arbol(S, K, T, r, sigma, N, tipo="call", divs=()):
    """Europea, americana, premio de ejercicio y griegas tomadas del arbol."""
    eur, _, _, _   = arbol_crr(S, K, T, r, sigma, N, tipo, False, divs)
    ame, nej, g, par = arbol_crr(S, K, T, r, sigma, N, tipo, True, divs)
    (V0,_), (V1,P1), (V2,P2) = g[0], g[1], g[2]
    # Delta y gamma del paso 1 y 2; theta del nodo central del paso 2
    delta = (V1[1]-V1[0])/(P1[1]-P1[0])
    d1 = (V2[2]-V2[1])/(P2[2]-P2[1])
    d2 = (V2[1]-V2[0])/(P2[1]-P2[0])
    gamma = (d1-d2)/(0.5*(P2[2]-P2[0]))
    theta = (V2[1]-V0[0])/(2*par['dt'])/365.0
    return ResultadoArbol(eur, ame, ame-eur, delta, gamma, theta, nej)

def griegas_arbol(S, K, T, r, sigma, N, tipo="call", divs=(), h_s=0.01, h_v=0.01, h_r=0.0001):
    """Vega y rho por revaluacion; delta, gamma y theta del propio arbol."""
    base = valuar_arbol(S, K, T, r, sigma, N, tipo, divs)
    up   = arbol_crr(S, K, T, r, sigma+h_v, N, tipo, True, divs)[0]
    dn   = arbol_crr(S, K, T, r, max(sigma-h_v,1e-6), N, tipo, True, divs)[0]
    rup  = arbol_crr(S, K, T, r+h_r, sigma, N, tipo, True, divs)[0]
    rdn  = arbol_crr(S, K, T, r-h_r, sigma, N, tipo, True, divs)[0]
    return dict(precio=base.americana, europea=base.europea,
                premio=base.premio_ejercicio, nodos_ejercicio=base.nodos_ejercicio,
                delta=base.delta, gamma=base.gamma, theta=base.theta,
                vega=(up-dn)/(2*h_v)/100.0, rho=(rup-rdn)/(2*h_r)/100.0)

# ============================================================
# 4. VALIDACION CONTRA HULL (cap. 21, ejemplo de referencia)
# ============================================================
def validar_hull():
    """Put americana: S=50, K=50, r=10%, sigma=40%, T=5 meses, N=5 -> 4.4886 (Hull)."""
    r_ = valuar_arbol(50, 50, 5/12, 0.10, 0.40, 5, "put")
    return r_.americana

# ============================================================
# 5. REPORTE
# ============================================================
def _cargar_cadena(ruta="opciones/dec18.csv"):
    import csv
    return {float(r["strike"]): r for r in csv.DictReader(open(ruta))}

def main():
    D = ((DIV, T_DIV),)
    N = 2000
    print("="*78)
    print("WALMART INC. (WMT.O) - Valoracion de opciones y arbol binomial americano")
    print(f"Spot {S0}  |  Vencimiento 18-dic-2026 ({T_EXP*365:.0f} dias)  |  "
          f"Dividendo ${DIV} ex-{T_DIV*365:.0f}d  |  rf {RF:.2%}")
    print("="*78)

    print("\n[1] VALIDACION DEL MODELO")
    print(f"  Put americana de Hull (cap.21): {validar_hull():.4f}  | referencia 4.4886")
    bs = black_scholes(S0, 125, T_EXP, RF, 0.3189, "call", D)
    tr = arbol_crr(S0, 125, T_EXP, RF, 0.3189, 2000, "call", False, D)[0]
    print(f"  Convergencia arbol -> Black-Scholes (K=125): {tr:.6f} vs {bs:.6f}"
          f"  dif {tr-bs:+.6f}")

    cad = _cargar_cadena()
    print("\n[2] VOLATILIDAD IMPLICITA: modelo propio vs LSEG")
    difs = []
    for K in (115, 120, 125, 130, 135):
        for t, p in (("call", "c"), ("put", "p")):
            iv = float(cad[K][p+"_iv"])
            mid = (float(cad[K][p+"_bid"]) + float(cad[K][p+"_ask"]))/2
            o = vol_implicita(mid, S0, K, T_EXP, RF, t, D)
            difs.append(abs(o*100 - iv)*100)
    print(f"  Diferencia media absoluta sobre 10 contratos: {sum(difs)/len(difs):.1f} pb de volatilidad")

    print("\n[3] PREMIO DE EJERCICIO ANTICIPADO")
    print(f"  {'K':>4} {'tipo':>5} {'europea':>9} {'americana':>10} {'premio':>9} {'%':>7}")
    for K in (115, 120, 125, 130, 135):
        for t, p in (("call", "c"), ("put", "p")):
            iv = float(cad[K][p+"_iv"])/100
            r_ = valuar_arbol(S0, K, T_EXP, RF, iv, N, t, D)
            print(f"  {K:>4} {t:>5} {r_.europea:>9.5f} {r_.americana:>10.5f} "
                  f"{r_.premio_ejercicio:>9.5f} {r_.premio_ejercicio/r_.americana*100:>6.3f}%")

    print("\n[4] EXPERIMENTO CONTROLADO: el dividendo es la unica fuente de valor")
    print("    de ejercicio anticipado en una call americana (call K=125)")
    iv = float(cad[125]["c_iv"])/100
    for d in (0.00, 0.25, 0.75, 1.50, 2.50, 4.00):
        dv = ((d, T_DIV),) if d > 0 else ()
        r_ = valuar_arbol(S0, 125, T_EXP, RF, iv, N, "call", dv)
        print(f"    dividendo ${d:>5.2f}  premio = {r_.premio_ejercicio:.6f}")
    print("\n    Con dividendo cero el premio es exactamente cero: la call americana")
    print("    vale lo mismo que la europea (Merton, 1973). Con el dividendo real de")
    print("    Walmart el premio aparece, y crece monotonamente con su magnitud.")


# ============================================================
# 6. CURVA DE TASAS Y VALORACION DEL CONVERTIBLE
# ============================================================
CURVA_UST = [(0.0833,3.9715),(0.1667,4.0835),(0.25,4.0820),(0.3333,4.1905),
             (0.5,4.2690),(1,4.3755),(2,4.6030),(3,4.6710),(5,4.7320),
             (7,4.8230),(10,4.9350),(20,5.3420),(30,5.3145)]  # LSEG/TRADEWEB 01-nov-2026

def ust(T):
    """Tasa del Tesoro interpolada linealmente, en decimal."""
    C = CURVA_UST
    if T <= C[0][0]:  return C[0][1]/100
    if T >= C[-1][0]: return C[-1][1]/100
    for (t0,y0),(t1,y1) in zip(C, C[1:]):
        if t0 <= T <= t1:
            return (y0 + (y1-y0)*(T-t0)/(t1-t0))/100

def bono_recto(cupon, anios, ytm, face=100.0, freq=2):
    """Valor presente de un bono bullet con cupones semestrales."""
    n = int(round(anios*freq)); c = face*cupon/freq; y = ytm/freq
    return sum(c/(1+y)**k for k in range(1, n+1)) + face/(1+y)**n

def bs_call_q(S, K, T, r, sigma, q):
    """Call europea con dividend yield continuo (Merton 1973)."""
    d1 = (math.log(S/K) + (r - q + 0.5*sigma**2)*T)/(sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    return S*math.exp(-q*T)*_norm_cdf(d1) - K*math.exp(-r*T)*_norm_cdf(d2)

def convertible(S, anios, ytm_recto, sigma, q, prima_conv, cupon, face=100.0):
    """
    Convertible = bono recto + opcion call sobre la accion.
    prima_conv: prima de conversion sobre el spot (0.25 = 25%).
    Devuelve los componentes por cada 100 de valor nominal.
    """
    K   = S*(1+prima_conv)                 # precio de conversion
    ratio = face/K                         # acciones por cada 100 de nominal
    r   = ust(anios)
    bono = bono_recto(cupon, anios, ytm_recto, face)
    opc  = ratio*bs_call_q(S, K, anios, r, sigma, q)
    return dict(precio_conversion=K, ratio=ratio, bono=bono, opcion=opc,
                total=bono+opc, r=r, ytm_recto=ytm_recto)

def cupon_a_la_par(S, anios, ytm_recto, sigma, q, prima_conv, face=100.0):
    """Cupon que hace que el convertible cotice exactamente a la par."""
    lo, hi = 0.0, ytm_recto*1.5
    for _ in range(200):
        mid = (lo+hi)/2
        v = convertible(S, anios, ytm_recto, sigma, q, prima_conv, mid, face)["total"]
        if v > face: hi = mid
        else:        lo = mid
    return (lo+hi)/2

def call_spread(S, anios, sigma, q, prima_compra, prima_venta, acciones):
    """
    Estructura Molson Coors: se compra la call al strike de conversion y se vende
    un warrant a un strike mas alto. El neto eleva la prima de conversion efectiva
    sin pagar el costo de una call sola.
    """
    r  = ust(anios)
    K1 = S*(1+prima_compra); K2 = S*(1+prima_venta)
    c1 = bs_call_q(S, K1, anios, r, sigma, q)
    c2 = bs_call_q(S, K2, anios, r, sigma, q)
    return dict(K_compra=K1, K_venta=K2, prima_pagada=c1*acciones,
                prima_cobrada=c2*acciones, costo_neto=(c1-c2)*acciones,
                costo_unitario=c1-c2)

# ============================================================
# 7. PARAMETROS DEL CONVERTIBLE PROPUESTO
# ============================================================
CV_PLAZO   = 6          # anios, mismo plazo que la emision de Molson Coors 2007
CV_SIGMA   = 0.29       # volatilidad implicita de los LEAPs (ene-2029)
CV_Q       = 0.0081     # dividend yield prospectivo FY ene-2027 (LSEG)
CV_YTM     = 0.0514     # rendimiento de deuda recta WMT a 6 anios
                        # interpolado: nota 4.15% 2031 (5a) 5.019% / 5.35% 2033 (7a) 5.255%
CV_PRIMA   = 0.25       # prima de conversion, igual que Molson Coors
CV_EMISION = 1500.0     # millones de dolares
CS_PRIMA_V = 0.60       # prima del warrant vendido, igual que Molson Coors

def main_convertible():
    print("\n[5] CURVA DEL TESORO (LSEG/TRADEWEB, 01-nov-2026)")
    print("    " + "  ".join(f"{t}:{y:.3f}%" for t, y in
          [(l, v) for (k, v), l in zip(CURVA_UST,
           ["1M","2M","3M","4M","6M","1Y","2Y","3Y","5Y","7Y","10Y","20Y","30Y"])]))
    print(f"    Pendiente 1M-30Y: {(CURVA_UST[-1][1]-CURVA_UST[0][1])*100:.0f} pb"
          f"  |  20Y por encima de 30Y: inversion de "
          f"{(CURVA_UST[-2][1]-CURVA_UST[-1][1])*100:.1f} pb")

    c = cupon_a_la_par(S0, CV_PLAZO, CV_YTM, CV_SIGMA, CV_Q, CV_PRIMA)
    r = convertible(S0, CV_PLAZO, CV_YTM, CV_SIGMA, CV_Q, CV_PRIMA, c)
    print(f"\n[6] CONVERTIBLE A {CV_PLAZO} ANIOS, PRIMA DE CONVERSION {CV_PRIMA:.0%}")
    print(f"    Precio de conversion   ${r['precio_conversion']:.2f}")
    print(f"    Cupon a la par         {c:.3%}   (deuda recta: {CV_YTM:.3%})")
    print(f"    Bono recto {r['bono']:.3f}  +  Opcion {r['opcion']:.3f}  =  {r['total']:.3f}")

    print("\n[7] NO HAY FREE LUNCH")
    af = sum(1/(1+CV_YTM/2)**k for k in range(1, CV_PLAZO*2+1))
    pv = (CV_YTM-c)*CV_EMISION/2*af
    opc = r["opcion"]/100*CV_EMISION
    print(f"    VP del ahorro de cupon   ${pv:,.1f} M")
    print(f"    Valor de la opcion dada  ${opc:,.1f} M")
    print(f"    Diferencia               ${pv-opc:,.1f} M")
    print("    El descuento de cupon equivale, peso por peso, a la opcion entregada.")

    print("\n    Sensibilidad a la prima de conversion:")
    for p in (0.15, 0.20, 0.25, 0.30, 0.40, 0.50):
        cc = cupon_a_la_par(S0, CV_PLAZO, CV_YTM, CV_SIGMA, CV_Q, p)
        rr = convertible(S0, CV_PLAZO, CV_YTM, CV_SIGMA, CV_Q, p, cc)
        print(f"      prima {p:>4.0%}  precio conv ${rr['precio_conversion']:>7.2f}  "
              f"cupon {cc:>6.3%}  opcion {rr['opcion']:>6.2f}")

    acc = CV_EMISION*1e6/(S0*(1+CV_PRIMA))/1e6
    cs = call_spread(S0, CV_PLAZO, CV_SIGMA, CV_Q, CV_PRIMA, CS_PRIMA_V, acc)
    print(f"\n[8] CALL SPREAD (comprar {CV_PRIMA:.0%} / vender {CS_PRIMA_V:.0%})")
    print(f"    Strikes ${cs['K_compra']:.2f} / ${cs['K_venta']:.2f}   sobre {acc:,.2f} M acciones")
    print(f"    Pagado ${cs['prima_pagada']:,.1f} M  -  Cobrado ${cs['prima_cobrada']:,.1f} M"
          f"  =  Neto ${cs['costo_neto']:,.1f} M")

if __name__ == "__main__":
    main()
    main_convertible()
