# Dos entrenamientos de 150 epocas completas

Solicitud aprobada el 21 de octubre de 2026: entrenar las dos primeras opciones con 150 epocas, sin parada por falta de mejora, para estudiar las curvas durante todo ese intervalo.

| Orden | Corrida | Modelo | Optimizador declarado | Resolucion | Epocas |
|---|---|---|---|---:|---:|
| 1 | yolo26s_sgd_640_150e | YOLO26s | SGD, lr inicial 0.005, cosine LR | 640 | 150 |
| 2 | yolo26n_campo_640_150e | YOLO26n | auto (se registra el optimizador efectivo) | 640 | 150 |

Ambas usan `epochs=150`, `patience=0`, `time=null`, `flipud=0.0`, `fliplr=0.5`, `hsv_h=0.02`, `hsv_s=0.55`, `hsv_v=0.35`, `scale=0.35`, batch nominal 8 y semilla 26. Los demas hiperparametros proceden de los dos experimentos seleccionados. En Ultralytics 8.4.57, `patience=0` se convierte en infinito y desactiva EarlyStopping. No hay limite temporal configurado.

La opcion `auto` del Nano elige tambien el learning rate: con este dataset y 150 epocas se espera AdamW con lr 0.002. El log y los argumentos efectivos del entrenador tienen prioridad sobre esa expectativa. Si el entrenador ajusta el batch por memoria, el cambio se registra.

## Dataset y trazabilidad

Entrada: `datasets/prepared/agave_maleza_2026-10-21/data.yaml`. Clase unica `agave`; 1493 imagenes de entrenamiento, 435 de validacion y 136 de prueba. Las 166 reservas quedan fuera. Se usan las anotaciones actuales, conservando los dos casos de revision visual documentados en `docs/dataset_2026-10-21/REVISION_ETIQUETAS.md` como limitacion conocida.

La verificacion previa de hashes esta en `backups/reorganizacion_2026-10-21/prelaunch_integrity_150.json`; no se corrigieron etiquetas automaticamente. Estas corridas parten de los pesos base preentrenados, igual que el protocolo anterior.

## Archivos de cada corrida

Raiz: `runs/detect/agave_maleza_150ep_2026-10-21/`.

- `results.csv`: metricas y perdidas de cada una de las 150 epocas.
- `results.png`: graficas completas al finalizar.
- `weights/best.pt`: peso seleccionado por validacion; puede corresponder a una epoca anterior a la 150 sin detener el entrenamiento.
- `weights/last.pt`: peso final tras completar las 150 epocas.
- Checkpoints periodicos cada 10 epocas para recuperacion y trazabilidad.
- `args.yaml`: argumentos efectivos de la corrida.

No se marca un entrenamiento completo hasta comprobar que `results.csv` contiene exactamente las epocas 1 a 150. Los errores de ejecucion o un apagado del equipo pueden interrumpirlo; se conservan logs y checkpoints para recuperar el trabajo. Desactivar EarlyStopping no oculta errores.

Los dos modelos se ejecutan secuencialmente en la GPU. El segundo empieza al terminar el entrenamiento del primero. Los resultados nuevos quedan separados del benchmark historico y de la propuesta anterior de once entrenamientos.

## Ejecutor y lanzamiento

Configuraciones: `configs/training/agave_maleza_150ep_2026-10-21/`.

```powershell
# Verificar sin entrenar
.\.venv\Scripts\python.exe scripts\train_campaign_150.py --check

# Lanzar una sola vez en un proceso separado
.\scripts\start_campaign_150.ps1
```

El lanzador conserva PID y rutas de logs en `benchmark/agave_maleza_150ep_2026-10-21/launch.json`. No volver a lanzarlo mientras la cola este activa. El ejecutor registra el estado y los avances de cada modelo en esa carpeta.

La peticion de impedir suspension automatica se limita al proceso de entrenamiento y se retira al terminar. Mantener el equipo encendido y conectado a corriente; cerrar la tapa o apagarlo puede interrumpir el proceso.
