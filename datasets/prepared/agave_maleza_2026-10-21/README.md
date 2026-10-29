# Dataset combinado de agave

404 imagenes historicas y 1826 nuevas de maleza. Una clase: `agave`.

`data.yaml` es la entrada para Ultralytics; `manifest.csv` conserva procedencia, hashes, cajas y split. `summary.json` contiene los conteos verificados y `split_policy.json` la regla reproducible.

`images/reserve` y sus etiquetas conservan las guardas temporales de 60 s; no aparecen en data.yaml. No se modificaron ni redimensionaron las imagenes o cajas.

La evaluacion nueva es interna a la misma salida de campo; no prueba generalizacion a otro campo. La particion historica se conserva para trazabilidad, con su posible correlacion temporal original.
