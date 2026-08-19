# PR #1, controlled-stress y guion de exposición

## 1. Estado de partida

La PR [traky12/castuo-evidence#1](https://github.com/Traky12/castuo-evidence/pull/1) sigue abierta sobre `master` con rama `ci/s001a-stress-pipeline-2026-08`, commit `e8c4c41` y `mergeStateStatus: CLEAN`. Los checks `preflight`, `contract-and-negative`, `functional` y `evidence-and-gate` están en `SUCCESS`. El job `controlled-stress` aparece como `SKIPPED` en la ejecución de pull request porque el workflow lo reserva para `workflow_dispatch` y `schedule`.

## 2. Comandos exactos para revisar y fusionar

### 2.1 Preparar un checkout local limpio

```bash
gh repo clone traky12/castuo-evidence ~/castuo-evidence-merge
cd ~/castuo-evidence-merge
git fetch --all --prune
git status --short --branch
```

### 2.2 Revisar la PR y sus checks

```bash
gh pr view 1 --repo traky12/castuo-evidence --web
gh pr diff 1 --repo traky12/castuo-evidence
gh pr checks 1 --repo traky12/castuo-evidence
```

Verificar que la PR no contiene secretos ni cambios fuera del workflow, runner, validadores, herramientas, schedule y tests:

```bash
gh api repos/traky12/castuo-evidence/pulls/1/files \
  --paginate \
  --jq '.[].filename'
```

La lista esperada es `.github/workflows/s001a-stress.yml`, `runners/s001a_runner.py`, `scenarios/S-001A/stress-schedule.yml`, `tests/test_evidence_schema.py`, `tools/*` y `validators/*`, junto con la eliminación del archivo con espacio en el nombre.

### 2.3 Aprobar la PR

Sólo después de revisar el diff, los logs y los artefactos:

```bash
gh pr review 1 \
  --repo traky12/castuo-evidence \
  --approve \
  --body "Reviewed: local-only S-001A automation, deterministic stress controls, evidence boundary preserved, promotion remains BLOCKED."
```

Si la política de la cuenta no permite autoaprobación de la propia PR, la aprobación debe hacerla otro revisor autorizado desde la interfaz de GitHub. No usar `--admin` para saltarse la revisión.

### 2.4 Fusionar usando la protección de `master`

```bash
gh pr merge 1 \
  --repo traky12/castuo-evidence \
  --squash \
  --delete-branch
```

Si GitHub exige una estrategia distinta, consultar las opciones permitidas y respetar la política del repositorio:

```bash
gh pr view 1 --repo traky12/castuo-evidence --json mergeStateStatus,reviewDecision,state
```

No ejecutar `git push origin master` ni un `git merge --no-verify` local contra una rama protegida.

### 2.5 Verificar el merge en remoto

```bash
gh pr view 1 --repo traky12/castuo-evidence \
  --json state,mergedAt,mergeCommit,headRefName,baseRefName

gh api repos/traky12/castuo-evidence/contents/.github/workflows/s001a-stress.yml?ref=master \
  --jq '{path,sha,branch:"master"}'

gh api repos/traky12/castuo-evidence/contents/runners/s001a_runner.py?ref=master \
  --jq '{path,sha,branch:"master"}'
```

El campo `state` debe ser `MERGED`, `mergedAt` debe tener valor y los dos archivos deben existir en `master`.

### 2.6 Actualizar el checkout local después del merge

```bash
git fetch origin --prune
git switch master
git reset --hard origin/master
git clean -fd
git log -1 --oneline --decorate
```

El commit remoto de `master` debe contener el cambio de workflow. Conservar el SHA del merge y el run ID como provenance.

## 3. Ejecutar `controlled-stress` manualmente

### 3.1 Antes del merge, sobre la rama de la PR

El workflow existe en la rama de la PR. Se puede lanzar manualmente sobre esa rama para probarlo antes del merge:

```bash
gh workflow run s001a-stress.yml \
  --repo traky12/castuo-evidence \
  --ref ci/s001a-stress-pipeline-2026-08 \
  -f profile=controlled-stress \
  -f iterations=100
```

Localizar la ejecución:

```bash
gh run list \
  --repo traky12/castuo-evidence \
  --workflow s001a-stress.yml \
  --branch ci/s001a-stress-pipeline-2026-08 \
  --limit 5
```

Esperar y observar el run:

```bash
gh run watch <RUN_ID> --repo traky12/castuo-evidence
```

Si termina con error, ver los logs fallidos:

```bash
gh run view <RUN_ID> \
  --repo traky12/castuo-evidence \
  --log-failed
```

Descargar artefactos:

```bash
gh run download <RUN_ID> \
  --repo traky12/castuo-evidence \
  --dir ./artifacts/s001a-<RUN_ID>
```

### 3.2 Después del merge, sobre `master`

```bash
gh workflow run s001a-stress.yml \
  --repo traky12/castuo-evidence \
  --ref master \
  -f profile=controlled-stress \
  -f iterations=100
```

La ejecución debe generar un `s001a-stress-*` y un `s001a-evidence-*`. Validar el resultado descargado:

```bash
find ./artifacts/s001a-<RUN_ID> -type f -maxdepth 5 | sort
jq '.promotion, .claim_boundary, .scope, .assurance' \
  ./artifacts/s001a-<RUN_ID>/**/result.json
jq '.' ./artifacts/s001a-<RUN_ID>/**/gate-result.json
```

El resultado esperado es `promotion: BLOCKED`, `scope: LOCAL`, `oneR: false` y `oneA: false`. Un run verde no es autorización de promoción.

## 4. Configurar y verificar el schedule

El workflow contiene:

```yaml
schedule:
  - cron: '17 2 * * *'
```

Esto significa una ejecución diaria a las **02:17 UTC** sobre la rama por defecto (`master` después del merge). Para verificar que GitHub reconoce el workflow y el schedule:

```bash
gh workflow list --repo traky12/castuo-evidence
gh workflow view s001a-stress.yml --repo traky12/castuo-evidence
```

El schedule sólo se activa una vez que el workflow está en `master`. Después del primer horario programado:

```bash
gh run list \
  --repo traky12/castuo-evidence \
  --workflow s001a-stress.yml \
  --branch master \
  --limit 5
```

Para un schedule más conservador, cambiar la expresión cron en una PR separada; por ejemplo, `17 2 * * 1-5` para días laborables. No modificar el schedule directamente en `master` sin revisión.

## 5. Guion detallado de exposición

### Apertura: estado de la PR

“Comenzamos con el estado real de `castuo-evidence#1`. La PR sigue abierta, apunta a `master`, contiene el commit `e8c4c41` y GitHub la considera `CLEAN`. El workflow ya ha ejecutado correctamente preflight, contratos y negativos, functional smoke y evidence-and-gate. El único job que no corre en una PR es controlled-stress, y eso es intencionado: se reserva para una ejecución manual o nocturna con más duración.”

### Diapositiva 1: propósito

“El objetivo del pipeline no es promover automáticamente CASTÚO. Su objetivo es que cada ejecución deje una evidencia local reproducible, con un scope y un claim boundary explícitos. Por eso la automatización termina en `PROMOTION = BLOCKED` mientras replay externo y revisión humana sigan pendientes.”

### Diapositiva 2: tres ritmos

“Tenemos tres ritmos con responsabilidades distintas. El smoke de PR protege la velocidad del desarrollo. El controlled-stress prueba repetición y tolerancia ante faults. El foreign replay no es un job rutinario de CI: requiere otro entorno y una revisión independiente. Separarlos evita que un test rápido se presente como verificación externa.”

### Diapositiva 3: contrato determinista

“El estrés se ejecuta sobre un fixture congelado, con hash, seed, schedule de fallos y límites de recursos. Esta decisión es importante porque hace que dos ejecuciones comparables tengan el mismo contrato. Una cifra de throughput sin contexto no sería evidencia de resiliencia; las invariantes son el centro del benchmark.”

### Diapositiva 4: jobs gobernados

“Preflight protege el perímetro. Contract-and-negative comprueba schemas, claims y los casos fail-closed. Functional ejecuta el ciclo básico. Controlled-stress somete la operación a fallos repetibles. Evidence-and-gate construye el paquete y verifica que el resultado siga bloqueado. Cada job tiene una función y una evidencia asociada.”

### Diapositiva 5: fallos operacionales

“Los seis fallos representan condiciones que pueden romper continuidad o lineage: red caída, reinicio, duplicados, reorder, desviación temporal y replay de recuperación. El criterio de éxito es conservar decisión, autoridad y evidencia. Si aparece un conflicto no resuelto, el pipeline no lo oculta: lo expone y bloquea el claim.”

### Diapositiva 6: paquete portable

“Los artefactos son result, events, semantic record, manifest, hashes y gate result. El registro semántico es la fuente autoritativa. Los artefactos permiten inspección y replay, pero no constituyen por sí solos una verificación independiente. El envelope debe poder salir del runner sin perder scope, commit, hashes ni límites.”

### Diapositiva 7: mitigación P0

“Los cuatro P0 quedan tratados de forma distinta. El primer riesgo se controla con el claim firewall. El segundo permanece abierto hasta ejercitar vendor exit. El tercero se reduce con el envelope y los hashes, pero exige foreign verifier. El cuarto se contiene con ejecución local-only y negative tests de autoridad. La automatización hace visibles los blockers; no los maquilla.”

### Diapositiva 8: correcciones previas

“Antes de discutir estrés tuvimos que hacer ejecutable la base: corregimos el import faltante del validator, renombramos el test con espacio y añadimos pruebas negativas e invariantes. Esto importa porque un pipeline que no puede descubrir sus tests o validar su JSON no merece ser un gate de evidencia.”

### Diapositiva 9: el verde correcto

“Un resultado verde significa que el código ejecutó la prueba y preservó el estado fail-closed. La lectura correcta es: ejecución local aprobada, evidencia local válida, replay extranjero pendiente, revisión independiente pendiente y promoción bloqueada. Éste es el comportamiento deseado, no una contradicción.”

### Diapositiva 10: siguiente gate

“El siguiente paso operativo es aprobar y fusionar la PR respetando la protección de `master`. Después lanzamos controlled-stress con 100 iteraciones, inspeccionamos los artefactos y verificamos el gate. Finalmente, un tercero debe ejecutar el replay en otro entorno. Sólo entonces se puede evaluar un avance de `1R` para el scope ensayado.”

### Cierre: principio de gobierno

“La conclusión es simple: automatizamos la prueba y la evidencia, no la autoridad ni el claim. La PR #1 hace repetible el primer tramo del camino; no convierte todavía a CASTÚO en un sistema independientemente verificado. El orden correcto es evidence first, fail closed, claim last.”
