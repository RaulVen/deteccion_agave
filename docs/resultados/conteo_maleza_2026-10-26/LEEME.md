# Videos con línea central y conteo — 26 de octubre de 2026

| Video fuente | Intervalo del original | Duración de salida | Fotogramas | Cruces automáticos |
|---|---|---:|---:|---:|
| `20.05.00-20.10.00[R][0@0][0][-21600].dav` | 01:00–01:36 | 36 s | 540 | 35 |
| `19.44.14-19.50.00[R][0@0][0][-21600].dav` | 01:02–03:20 | 138 s | 2,070 | 139 |

El primer archivo contiene los primeros 36 segundos del fragmento de un minuto
entregado anteriormente. Los intervalos excluyen el extremo final: el último
fotograma del segundo video está en 03:19.933 y completa una duración de 138 s.

## Regla de conteo

Se conserva el criterio histórico: línea horizontal al 50% de la altura,
cruce del centro de la caja **de arriba hacia abajo**, una vez por ID.
La línea está en y=810 sobre el original de 2880×1620, y en y=360 sobre
la salida de 1280×720. Aparecer inicialmente debajo no suma un cruce.
Cada fragmento comienza con el tracker y el contador vacíos.

La caja se pone naranja durante un segundo al contar; se muestran IDs,
trayectorias, confianza y el total acumulado. No se suman todas las detecciones
de cada fotograma. El indicador `Video` es el tiempo en la fuente y `Clip`
es el tiempo transcurrido en el fragmento.

Se utilizó YOLO26s + SGD, `best.pt` de `yolo26s_sgd_640_150e`, entrada 640,
confianza 0.30, FP32 y BoT-SORT persistente con la configuración histórica
`configs/tracking/botsort_agave.yaml`. Sin ReID; buffer de 90 cuadros.
Los detalles y hashes están en los respectivos `inferencia.json`.

## Archivos

- `anterior_0100_0136/conteo_agaves.mp4`: anterior recortado y con conteo.
- `nuevo_0102_0320/conteo_agaves.mp4`: nuevo intervalo y conteo.
- En cada carpeta, `cruces.csv` y `cruces.json` registran los eventos;
  `cruce_*.jpg` muestra cada incremento y `resumen_final.jpg` el resultado final.
- `predicciones.jsonl` conserva observaciones e IDs por fotograma.
- `verificacion.json` resume la comprobación de salidas.

Ambos MP4 H.264 a 15 fps pasaron la decodificación completa con FFmpeg sin
errores. Las duraciones, cuadros, IDs contados, registros CSV/JSON y totales
visibles coinciden. Una reproducción independiente de la regla sobre los
centros guardados obtiene los mismos 35 y 139 eventos.

## Alcance y observaciones

Son conteos automáticos de cruces por ID, todavía sin comparación con un
conteo manual completo. Un ID no garantiza identidad física perfecta.
Los dos videos pertenecen a la salida utilizada para el dataset: el anterior
aportó imágenes de validación y el nuevo aportó imágenes de entrenamiento.
Estos clips no son una evaluación independiente del modelo.

Si hay interrupciones en la detección, el cruce se infiere entre la última
observación y la actual del mismo ID. En el primer clip la separación máxima
entre esas observaciones fue de 3 cuadros (0.20 s). En el segundo, los eventos
97, 104, 114 y 117 tienen separaciones mayores de un segundo; la máxima es
46 cuadros (3.07 s). Esos cuatro eventos requieren especial atención al
contrastar con un conteo manual; su tiempo interpolado es una estimación.

No se modificaron fuentes, pesos ni etiquetas. Para reproducir, usar
`scripts/predict_video_fragment.py` con `--tracker`, `--line-ratio 0.5`,
`--direction down`, `--start 60 --duration 36` o `--start 62 --duration 138`.
