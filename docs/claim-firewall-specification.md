# Especificación Técnica del Claim Firewall y Objetos de Evidencia v2.0

## 1. Introducción y Principios de Diseño

El **Claim Firewall** es el mecanismo de control determinista implementado en el ecosistema **CASTÚO-SYSTEM™** para garantizar que ningún reclamo técnico, comercial o regulatorio pueda ser emitido o publicado sin estar respaldado por un artefacto de evidencia criptográficamente verificable [1]. 

Bajo la disciplina *Evidence-First*, el sistema opera bajo una premisa estricta: **Implementación ≠ Validación**. La existencia de código funcional en un repositorio privado no otorga por sí sola ningún derecho a realizar afirmaciones públicas sobre madurez, seguridad, cumplimiento normativo (como el EU AI Act) o preparación para producción.

```text
┌─────────────────────────┐
│  Intento de Reclamación │
└────────────┬────────────┘
             ▼
┌─────────────────────────┐
│     Claim Firewall      │ ───► ¿Existe Objeto de Evidencia v2.0?
└────────────┬────────────┘      ¿Es el Hash SHA-256 válido?
             │                   ¿Supera el benchmark objetivo?
             ├── (No / Fallo) ──► ⛔ CLAIM DENY / PROMOTION BLOCKED
             └── (Sí / Éxito) ──► ✅ LOCAL_RESULT_WITHIN_DECLARED_SCOPE
```

---

## 2. Estructura de los Objetos de Evidencia v2.0

Los objetos de evidencia v2.0 definen el esquema JSON canónico utilizado para registrar los resultados de ejecuciones locales, pruebas de benchmark (como S-001A) y auditorías de cumplimiento. Cada objeto es inmutable y está vinculado a un commit SHA específico.

### Esquema Canónico (`schema.json`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "CastuoEvidenceObjectV2",
  "type": "object",
  "properties": {
    "evidence_id": { "type": "string", "pattern": "^EVID-[A-Z]+-[0-9]{4}$" },
    "schema_version": { "type": "string", "enum": ["2.0"] },
    "timestamp": { "type": "string", "format": "date-time" },
    "git_commit_sha": { "type": "string", "pattern": "^[0-9a-f]{40}$" },
    "benchmark_target": { "type": "string" },
    "execution_result": {
      "type": "object",
      "properties": {
        "status": { "enum": ["SUCCESS", "FAILURE", "DEGRADED"] },
        "score": { "type": "number" },
        "threshold": { "type": "number" }
      },
      "required": ["status", "score", "threshold"]
    },
    "cryptographic_proof": {
      "type": "object",
      "properties": {
        "algorithm": { "type": "string", "enum": ["SHA-256"] },
        "hash": { "type": "string", "pattern": "^[0-9a-f]{64}$" }
      },
      "required": ["algorithm", "hash"]
    }
  },
  "required": ["evidence_id", "schema_version", "timestamp", "git_commit_sha", "execution_result", "cryptographic_proof"]
}
```

---

## 3. Reglas de Validación del Claim Firewall

El motor de validación evalúa cada artefacto basándose en una matriz de decisión binaria. Si alguna condición falla, el sistema bloquea automáticamente la promoción de cualquier reclamo asociado.

| Condición Evaluada | Estado Esperado | Comportamiento en Caso de Fallo |
| :--- | :--- | :--- |
| **Estructura JSON** | Cumplimiento estricto con `schema.json` v2.0 | Rechazo inmediato (`INVALID_SCHEMA`) |
| **Integridad Criptográfica** | El hash SHA-256 coincide con el payload ejecutable | Denegación de reclamo (`HASH_MISMATCH`) |
| **Trazabilidad de Commit** | El SHA pertenece a una rama oficial congelada | Bloqueo de promoción (`UNVERIFIED_COMMIT`) |
| **Cumplimiento de Umbral** | `score >= threshold` en el benchmark | Rechazo por rendimiento (`BENCHMARK_BELOW_TARGET`) |
| **Expiración de Evidencia** | Antigüedad menor al período de validez | Caducidad de evidencia (`EXPIRED_EVIDENCE`) |

---

## 4. Referencias

1. CASTÚO-SYSTEM™ Governance Framework. *EvOS v13.0 Evidence Fabric Architecture*. Repositorio público: `Traky12/castuo-evidence`, 2026.
