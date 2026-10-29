# Identificación del modelo NCNN

Se versionan `metadata.yaml`, `model.ncnn.param` y `sha256.json`. El archivo `model.ncnn.bin` (37,887,876 bytes) se conserva en el respaldo computacional local, fuera de Git. Esta carpeta no contiene un modelo ejecutable hasta añadir ese binario.

Recuperar `model.ncnn.bin` del respaldo original `rpi_restore/best_ncnn_model/` y copiarlo junto a los otros archivos antes de desplegar el visor. Comprobar su SHA256 contra `sha256.json`:

```powershell
Get-FileHash hardware/raspberry/restore/best_ncnn_model/model.ncnn.bin -Algorithm SHA256
```

No sustituirlo por otro archivo del mismo nombre sin comprobar el hash. Las pruebas históricas usaron esta exportación NCNN de entrada 320 × 320. Los pesos originales `best.pt` tampoco se incluyen en esta carpeta.
