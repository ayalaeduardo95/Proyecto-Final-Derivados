# Prompt de IA

Aquí va el PDF de la conversación completa con la herramienta de IA utilizada,
conforme al entregable 6 del enunciado: *"Prompt completo, código recibido y
nota de lo que se corrigió y validó."*

Archivos a colocar en esta carpeta:

- `Prompt_Claude.pdf` — exportación de la conversación
- `Prompt_TecGPT.pdf` — si se usó también TecGPT

## Correcciones y validaciones realizadas sobre el código recibido

Nota para el reporte: el código generado fue corregido y validado en estos puntos.

1. **Convención de plazo.** Las volatilidades implícitas calculadas con el plazo medido
   desde la última operación salían 72 pb por debajo de las de LSEG. Se detectó por
   calibración inversa que LSEG mide el plazo desde la fecha calendario corriente.
   Corregido de 49 a 47 días; el sesgo pasó de −72 pb a −6 pb.
2. **Tasa libre de riesgo.** Se sustituyó el valor heredado de la actividad previa
   (3.94 %) por la tasa interpolada de la curva del Tesoro al plazo exacto (4.03 %).
3. **Volatilidad del convertible.** Se rechazó la implícita del mes cercano (41 %) por
   estar contaminada por el reporte trimestral, y se adoptó la de LEAPs (29 %).
4. **Filtrado de la cadena.** Se excluyeron los ejercicios fuera de la banda 100–150,
   donde LSEG reporta implícitas de hasta 124 % con postura de compra en cero.
5. **Validación cruzada.** El modelo se implementó por separado en Python y en R; ambas
   implementaciones reproducen el ejemplo de Hull (4.4885 contra 4.4886 de referencia)
   y convergen entre sí.
