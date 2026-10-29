# Trabajo en este repositorio

El proyecto se comparte entre dos computadoras mediante `origin/main`.

- Redacción: comenzar por `docs/tesis/README.md`. Los capítulos Markdown son las fuentes editables; los PDF son exportaciones. No sustituir cambios de redacción con borradores históricos ni regenerarlos automáticamente al sincronizar.
- Cómputo: código en `scripts/` y `src/`, parámetros en `configs/`, resultados tabulares en `benchmark/`, prototipo en `hardware/`. Conservar las rutas de las corridas y datasets existentes.
- Publicar evidencia pequeña y verificable en `docs/resultados/` para que la computadora de redacción pueda consultar resultados sin ejecutar entrenamientos. Mantener procedencia y limitaciones experimentales.
- Una solicitud de sincronizar, commit o push no autoriza cambiar cifras, entrenar modelos, conectarse a cámaras/Raspberry ni rehacer el escrito.
- Antes de sincronizar, revisar estado, remoto y diferencias con `origin/main`. Preservar los cambios locales y remotos. No usar force push, reset destructivo ni borrar trabajo ajeno para resolver divergencias.
- No incluir credenciales, archivos de entorno, instalaciones locales, datasets completos, videos, pesos ni respaldos. Consultar `.gitignore` y `docs/SINCRONIZACION.md`.
- En documentación nueva usar enlaces relativos. Las rutas absolutas de los registros históricos describen la máquina original y no son instrucciones portables.
- Para cambios de conteo ejecutar `python -B -m unittest discover -s scripts -p test_line_crossing_counter.py`; una sincronización documental no requiere entrenar ni ejecutar hardware.

El usuario solicitó publicar esta organización directamente en `main`.
