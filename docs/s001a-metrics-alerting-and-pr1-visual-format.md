# Slack, validación local y formato visual para PR #1 / P0

## 1. Configurar `SLACK_WEBHOOK_URL` sin comprometer la seguridad

### 1.1 Crear el webhook en Slack

Un administrador del workspace debe crear o autorizar una integración de **Incoming Webhook** para el canal técnico de alertas. El webhook debe apuntar a un canal de incidentes o CI, no a un canal público. La URL resultante es un secreto equivalente a una credencial: no debe aparecer en commits, issues, logs, screenshots, documentos, prompts o comandos compartidos.

### 1.2 Opción preferida: interfaz de GitHub

En `https://github.com/Traky12/castuo-evidence/settings/secrets/actions`:

| Campo | Valor |
|---|---|
| Name | `SLACK_WEBHOOK_URL` |
| Secret | La URL completa del Incoming Webhook, pegada sólo en el campo secreto |
| Scope | Repository secret, o preferiblemente environment `s001a-alerts` |

Si se usa un environment protegido, el job de notificación debe referenciarlo:

```yaml
  notify-failure:
    environment: s001a-alerts
```

No otorgar permisos de escritura al job de notificación. El workflow sólo necesita `contents: read`; el secret sólo se inyecta en el paso que ejecuta `curl`.

### 1.3 Opción CLI sin dejar el valor en el historial

No poner la URL directamente después de `--body`. Leerla de forma interactiva y enviarla por stdin:

```bash
read -rsp 'Slack webhook URL: ' SLACK_WEBHOOK_URL
printf '\n'
printf '%s' "$SLACK_WEBHOOK_URL" | \
  gh secret set SLACK_WEBHOOK_URL \
    --repo traky12/castuo-evidence \
    --body -
unset SLACK_WEBHOOK_URL
```

Si se usa un environment protegido:

```bash
read -rsp 'Slack webhook URL: ' SLACK_WEBHOOK_URL
printf '\n'
printf '%s' "$SLACK_WEBHOOK_URL" | \
  gh secret set SLACK_WEBHOOK_URL \
    --repo traky12/castuo-evidence \
    --env s001a-alerts \
    --body -
unset SLACK_WEBHOOK_URL
```

La integración actual no permite consultar los valores de secrets; esa limitación es deseable. Sólo debe verificarse el nombre desde la interfaz o con una cuenta con permisos adecuados, nunca intentar recuperar el valor.

### 1.4 Verificar sin filtrar el secreto

La primera validación debe ser estática: confirmar que el workflow referencia exactamente `${{ secrets.SLACK_WEBHOOK_URL }}` y que el valor no aparece en el repositorio:

```bash
git grep -n 'SLACK_WEBHOOK_URL' -- . ':!*.md'
git grep -nE '(hooks\.slack\.com/services|https://[^ ]*slack[^ ]*)' || true
```

Después, ejecutar un fallo controlado en una rama de prueba o lanzar el workflow con un fixture que falle. Verificar sólo que el job `notify-failure` terminó correctamente y que el mensaje llegó al canal. No imprimir el entorno, hacer `set -x`, usar `echo "$SLACK_WEBHOOK_URL"` ni incluir payloads completos.

### 1.5 Rotación y respuesta ante exposición

Si la URL aparece en un log, commit, captura o mensaje, revocarla inmediatamente desde Slack, crear un webhook nuevo y actualizar el secret. No basta con borrar el texto del archivo actual: el valor puede permanecer en el historial Git y en los logs de Actions. Tras rotar, repetir el fallo controlado y confirmar que sólo el webhook nuevo recibe mensajes.

## 2. Integrar métricas y alertas en la validación local

La validación local debe producir el mismo contrato de métricas que CI, pero debe permanecer **sin red por defecto**. La secuencia recomendada es:

```text
fixture + seed
→ local S-001A runner
→ result.json + events.jsonl
→ metrics validator
→ evidence envelope local
→ gate BLOCKED
→ PR report
```

### 2.1 Añadir un validador local de métricas

Crear `validators/validate_s001a_metrics.py` con estas responsabilidades:

```python
from __future__ import annotations
import json
import sys
from pathlib import Path

LATENCY_LIMITS = {
    "fault_detection": {"p95": 1000, "max": 5000},
    "policy_decision": {"p95": 250, "max": 1000},
    "buffer_enqueue": {"p95": 500, "max": 2000},
    "recovery_time": {"p95": 5000, "max": 30000},
}

ZERO_COUNTERS = {
    "evidence_loss_count",
    "semantic_duplicate_count",
    "policy_violation_count",
    "recovery_failure_count",
}


def validate_metrics(path: str) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    metrics = data.get("metrics", {})
    failures = []
    for name, limits in LATENCY_LIMITS.items():
        values = metrics.get("latency_ms", {}).get(name)
        if not values:
            failures.append(f"missing latency metric: {name}")
            continue
        for key, limit in limits.items():
            if values.get(key) is None or values[key] > limit:
                failures.append(f"{name}.{key}={values.get(key)} > {limit}")
    counters = metrics.get("counters", {})
    for name in ZERO_COUNTERS:
        if counters.get(name) != 0:
            failures.append(f"{name}={counters.get(name)}; expected 0")
    if failures:
        for failure in failures:
            print(f"[ERROR] {failure}", file=sys.stderr)
        return 1
    print("[OK] S-001A metrics satisfy controlled-stress thresholds")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_metrics(sys.argv[1]))
```

Los límites son controles iniciales y deben versionarse como `controlled-stress-v1`; no deben presentarse como SLO comercial hasta disponer de una baseline suficiente.

### 2.2 Crear un comando pre-PR único

Añadir un script o `Makefile` que haga imposible olvidar una validación:

```bash
#!/usr/bin/env bash
set -euo pipefail

OUT="${1:-out/pre-pr-$(date -u +%Y%m%dT%H%M%SZ)}"
python runners/s001a_runner.py \
  --profile pr-smoke \
  --fixture evidence/local/EVID-EVT-0002.json \
  --seed 20260819 \
  --output "$OUT/run"
python validators/validate_s001a_result.py "$OUT/run/result.json"
python validators/validate_s001a_metrics.py "$OUT/run/result.json"
python tools/build_evidence_envelope.py \
  --result "$OUT/run/result.json" \
  --commit "$(git rev-parse HEAD)" \
  --output "$OUT/envelope"
python tools/evaluate_gate.py \
  --envelope "$OUT/envelope" \
  --expected BLOCKED
printf '[OK] pre-PR S-001A validation complete: %s\n' "$OUT"
```

El script debe fallar en el primer control roto y devolver un directorio de artefactos para adjuntarlo a la PR. No debe llamar Slack por defecto.

### 2.3 Política de alertas locales

La alerta local debe ser un **informe de terminal y archivo**, no un webhook automático. Así se evita filtrar datos o crear ruido mientras se desarrolla. Si se necesita una alerta explícita desde un entorno autorizado, hacerla opt-in:

```bash
S001A_NOTIFY=slack ./scripts/pre_pr_s001a.sh
```

El script sólo debe habilitar el webhook cuando `S001A_NOTIFY=slack` y `SLACK_WEBHOOK_URL` existe en el entorno; nunca debe leer `.env` no auditado ni guardar la URL en el artifact. Para el flujo normal, la notificación Slack debe permanecer en GitHub Actions, donde el secret está gestionado por GitHub.

## 3. Alertas CI recomendadas

El job `notify-failure` debe depender de `preflight`, `contract-and-negative`, `functional`, `controlled-stress` y `evidence-and-gate`, ejecutarse con `always()`, y enviar sólo en `failure()` o `cancelled()`. Para pull requests de forks, no usar secrets; las notificaciones nativas de GitHub son el fallback.

El mensaje Slack debe contener únicamente:

| Campo | Ejemplo |
|---|---|
| Repositorio | `traky12/castuo-evidence` |
| Workflow | `S-001A stress and evidence` |
| Run ID | `32215420819` |
| Rama | `master` o `ci/...` |
| Commit | SHA corto |
| Estado | `failure`, `cancelled` o `blocked` |
| Enlace | URL de Actions |

Nunca enviar a Slack el contenido completo de `semantic.json`, events, fixtures, payloads o información de identidad.

## 4. Formato visual recomendado para la presentación

La presentación debe utilizar una **retícula horizontal de seis columnas**, fondo claro, tipografía negra de alto contraste, azul cobalto para estados y amarillo de seguridad para marcas de atención. El texto debe anclarse a una línea base inferior, con numeración grande y una marca geométrica en las esquinas.

### Diapositiva 1 — Estado de PR #1

**Visual:** una columna izquierda con `#1`, una banda central con `OPEN · CLEAN`, y una columna derecha con `e8c4c41`, `master` y checks verdes.
**Mensaje:** la PR está técnicamente lista para revisión, pero aún no está fusionada.

### Diapositiva 2 — Qué pasó en CI

**Visual:** cinco segmentos horizontales: `preflight`, `contract`, `functional`, `stress`, `evidence/gate`. El segmento stress debe aparecer como `SKIPPED / manual-nightly`, no como fallo.
**Mensaje:** la omisión del estrés en PR es una decisión de cadencia.

### Diapositiva 3 — Métricas de estrés

**Visual:** dos zonas. A la izquierda, latencia p50/p95/p99/max; a la derecha, throughput y contadores críticos. Destacar en amarillo `evidence_loss=0`, `semantic_duplicate=0`, `policy_violation=0`, `recovery_failure=0`.
**Mensaje:** medir la preservación de invariantes, no vender throughput.

### Diapositiva 4 — Secret boundary

**Visual:** flujo `Slack webhook → GitHub secret → notify-failure`, con el valor del webhook oculto y una línea roja que prohíbe logs, commits, artifacts y forks.
**Mensaje:** el secret sólo existe en GitHub y sólo se inyecta en el paso de notificación.

### Diapositiva 5 — Mitigación P0

**Visual:** matriz de cuatro filas: `P0-R1`, `P0-R2`, `P0-R3`, `P0-R4`; columna de control CI, columna de evidencia local y columna de blocker residual.
**Mensaje:** CI reduce y hace visible el riesgo, pero foreign replay, vendor exit y revisión siguen siendo gates separados.

### Diapositiva 6 — Ruta de merge y siguiente gate

**Visual:** `review diff → checks → approve → squash merge → run on master → controlled stress → foreign replay → review`. Marcar `PROMOTION BLOCKED` hasta el último tramo.
**Mensaje:** el merge documental no es promoción operacional.

### Diapositiva 7 — Cierre

**Visual:** tres líneas grandes: `AUTOMATE TEST`, `PRESERVE EVIDENCE`, `REVIEW CLAIM`.
**Mensaje:** `EVIDENCE FIRST · FAIL CLOSED · CLAIM LAST`.

## Referencias

[1]: https://docs.github.com/actions/security-guides/using-secrets-in-github-actions "GitHub Docs — Using secrets in GitHub Actions"

[2]: https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks "Slack Developer Docs — Sending messages using incoming webhooks"

[3]: https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs "GitHub Docs — Notifications for workflow runs"
