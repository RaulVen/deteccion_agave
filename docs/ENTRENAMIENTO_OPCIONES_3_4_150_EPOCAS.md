# Opciones 3 y 4: 150 épocas completas

El usuario autorizó el 22 de octubre de 2026 los dos experimentos pendientes y el seguimiento cada 30 minutos. Se ejecutan secuencialmente en la GPU local.

| Orden | Corrida | Cambio frente a YOLO26s + SGD de referencia | Épocas |
|---|---|---|---:|
| 3 | `yolo26s_sgd_960_150e` | `imgsz: 640 → 960`; `box=7.5` | 150 |
| 4 | `yolo26s_sgd_box9_640_150e` | `box: 7.5 → 9.0`; `imgsz=640` | 150 |

La referencia es `yolo26s_sgd_640_150e` de la campaña `agave_maleza_150ep_2026-10-21`. Ambas nuevas configuraciones parten de `models/pretrained/yolo26s.pt`, con SGD, tasa inicial 0.005 y calendario coseno, usando las mismas particiones del dataset, semilla 26 y demás hiperparámetros de la referencia. No se continúa desde sus pesos entrenados.

Se conservan `epochs=150`, `patience=0`, `time=null`, `flipud=0`, `fliplr=0.5`, `hsv_h=0.02`, `hsv_s=0.55` y `hsv_v=0.35`. El batch nominal es 8; cualquier reducción automática por memoria debe quedar registrada y considerarse al interpretar la comparación. La cola verifica las épocas 1 a 150, guarda métricas por época, curvas completas, `best.pt`, `last.pt` y checkpoints cada 10 épocas.

## Comparación de resultados

El benchmark principal de los nuevos modelos usa el mismo protocolo de prueba a 640 píxeles que las primeras dos corridas. Eso permite comparar los cuatro modelos sobre las mismas 136 imágenes de prueba y con los mismos parámetros de evaluación. Cada `best.pt` se selecciona por validación durante su entrenamiento, nunca por resultados de prueba.

Además, se evalúan a 960 tanto el modelo entrenado a 960 como la referencia entrenada a 640. Los resultados adicionales se guardan separados para distinguir el efecto de entrenar a mayor resolución del de aumentar solamente la resolución de inferencia. No se mezclan esos valores con el ranking principal a 640. La validación por época del experimento a 960 usa su resolución de entrenamiento; sus curvas no constituyen por sí solas una comparación con las curvas a 640.

La resolución de selección del checkpoint y la de evaluación se registran por separado. El mejor checkpoint elegido a 960 no necesariamente es el óptimo para inferencia a 640. En el experimento `box=9.0`, el cambio de ponderación impide comparar directamente la magnitud de la pérdida de cajas con la referencia `box=7.5`; se comparan mAP, precisión, recall y ejemplos de localización.

Los resultados anteriores se conservan en sus rutas originales. Los nuevos archivos están bajo:

- Configuraciones: `configs/training/agave_maleza_150ep_opciones34_2026-10-22/`.
- Entrenamientos: `runs/detect/agave_maleza_150ep_opciones34_2026-10-22/`.
- Estado, logs y tablas: `benchmark/agave_maleza_150ep_opciones34_2026-10-22/`.
- Auditoría previa: `backups/reorganizacion_2026-10-21/prelaunch_integrity_opciones34_150.json`.

## Ejecución y seguimiento

```powershell
.\.venv\Scripts\python.exe -B scripts\train_campaign_opciones34_150.py --check
.\scripts\start_campaign_opciones34_150.ps1
```

El lanzador se ejecuta una sola vez, separado de la sesión de terminal. `launch.json` conserva el PID del lanzador y las rutas de logs; `status.json` conserva el PID del proceso de entrenamiento y el estado por modelo. Los identificadores pueden ser distintos en Windows.

El seguimiento automático de este chat se revisa cada 30 minutos, sin mensajes rutinarios mientras avance normalmente. Al completar ambos entrenamientos y sus evaluaciones se entregan tablas, gráficas y enlaces a los pesos; un fallo se informa sin reiniciar automáticamente. El seguimiento se pausa después del informe final. Mantener el equipo encendido, conectado y la aplicación abierta para el seguimiento; la prevención de suspensión automática dura solo mientras se ejecuta la cola.
