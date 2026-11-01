# Evidence → E3 → Edge: contrato de aceptación (PLAN)

**Alcance documental, no validación de ejecución.** Repositorio canónico de esta propuesta: `Traky12/castuo-evidence` (rama `master`). Autoridad del ecosistema: `Traky12/Castuo-system`.

## Contratos de origen
- `castuo-agro-edge`: origen de evento, `org_id`, `device_id`, secuencia, cadena y esquema, conflictos preservados, sin simulados presentados como reales.
- `castuo-offline-field-operations`: operación humana offline, lote y limitaciones, estado `LOCAL_ONLY` hasta evento explícito de sincronización.
- `castuo-evidence`: `source_commit`, fixture congelado, `hash_scope`, resultados, metadatos de reproducción, SHA-256 y afirmaciones acotadas.
- `castuo-e3-001`: verificaciones del manifiesto y firmas con claves Ed25519 fijadas externamente, rechazando alias Base64, duplicidad de claves y claves revocadas.
- `Castuo-system`: autorización y segregación real por organización, maker-checker, decisiones registradas. Ningún módulo externo aprueba por sí solo.
- `goldfish`: prueba de recuperación y diagnóstico reproducible, no solo un dashboard verde.

## Invariantes
No modificar la evidencia histórica `EVID-EVT-0002`. No afirmar que `hash_scope` nuevo valida paquetes antiguos. Una firma prueba posesión de una clave y bytes firmados; no verdad ni atribución real sin confianza externa. Rechazar timestamps no atestados como cronología certificada, duplicados, cadenas alteradas, replay, firmas inválidas, misma clave bajo otro ID y archivos inesperados.

## Pruebas obligatorias de aceptación
1. Git HEAD literal, SHA-256 por archivo y agregado global sin auto-hashear el manifiesto.
2. Pytest, Ruff, Gitleaks, pip-audit y workflows/HTTP cuando sean aplicables, con logs y código de salida.
3. Paridad con CLI **oficial** E3, Action y tres navegadores; rechazo semántico auténtico del candidato sin firmas, no por dependencia ausente.
4. Reproducción aislada externa, firmada y vinculada al origen exacto, y dos revisiones independientes distintas del autor.
5. Gobernanza: decisiones `APPROVE` humanas autenticadas; no autoejecución ni promoción automática.
6. Tratamiento ISO 22000/22005/27001 y objetivo Six Sigma ≤0,3 DPMO como planes hasta medición real y auditoría competente.

**Resultado por defecto:** `DOCUMENTED/PLAN`; `G1=BLOCKED`, `G2=BLOCKED`, `MERGE/RELEASE/PRODUCTION=BLOCKED`. No exportar secretos ni información privada al repositorio público.
