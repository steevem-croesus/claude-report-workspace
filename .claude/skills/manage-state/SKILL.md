---
name: manage-state
description: Gère l'état persistant des migrations de rapports via fichiers JSON pour permettre la reprise automatique. Utiliser pour créer, lire et mettre à jour l'état d'une migration en cours (phases, fonctions analysées, paramètres implémentés, blockers).
---

# Skill: Manage State

Gestion de l'état des migrations de rapports via fichiers JSON.

## Objectif

Créer, lire et mettre à jour le fichier d'état JSON pour tracker la progression d'une migration.

## Localisation

**Fichier:** `.work/{slug}/state.json`

Créer répertoire: `mkdir -p .work/{slug}`

## Structure

```json
{
  "reportId": "RPT-17858",
  "reportName": "Gains et Pertes Non Réalisés",
  "reportCode": "GP_NON_REALISE",
  "currentPhase": "analysis",
  "analysis": {
    "status": "in_progress",
    "currentStep": "extraction",
    "completedSteps": [],
    "files": {"extraction": null, "spec": null, "checklist": null},
    "functions": [],
    "summary": {"totalFunctions": 0, "analyzed": 0, "pending": 0, "notFound": 0, "blocked": 0}
  },
  "development": {
    "status": "not_started",
    "currentStep": null,
    "branch": null,
    "completedParameters": [],
    "pendingParameters": [],
    "summary": {"totalParameters": 0, "implemented": 0, "tested": 0, "registered": 0, "pending": 0},
    "build": {"lastStatus": null, "lastRun": null},
    "tests": {"total": 0, "passing": 0, "failing": 0, "coverage": 0},
    "pr": {"created": false, "url": null, "number": null}
  },
  "metadata": {
    "createdAt": "2025-01-18T10:00:00Z",
    "updatedAt": "2025-01-18T10:00:00Z",
    "createdBy": "Claude Code",
    "estimatedTotalHours": 0,
    "actualHours": 0
  },
  "decisions": [],
  "blockers": []
}
```

## Opérations

### 1. Créer nouvel état

**Input:** Report ID, Report Name, Report Code (optionnel)

**Action:**
```bash
mkdir -p .work/{slug}
# Créer fichier JSON avec structure initiale, timestamp actuel pour createdAt/updatedAt
```

**Output:** `.work/{slug}/state.json` créé

### 2. Lire état existant

**Input:** Report ID

**Action:**
```bash
if [ -f ".work/{slug}/state.json" ]; then
  cat .work/{slug}/state.json
fi
```

**Output:** Objet JSON si existe, `null` sinon

### 3. Mettre à jour état

**Input:** Report ID, Section (ex: "analysis.currentStep"), Nouvelle valeur

**Action:**
1. Lire état actuel
2. Modifier section spécifiée
3. Mettre à jour `metadata.updatedAt` (timestamp actuel)
4. Écrire JSON

**Exemple:** Ajouter "extraction" à `analysis.completedSteps`, passer `analysis.currentStep` à "classification"

### 4. Ajouter/Mettre à jour fonction

**Input:** Report ID, Function info: {name, type, widgetType, entryType, status, ...}

**Action - Ajouter:**
```json
// Ajouter à analysis.functions[]
{
  "name": "InitGainLossCost",
  "type": "Specific",
  "widgetType": 3,
  "entryType": "PRE",
  "status": "pending",
  "cppLocation": null,
  "complexity": null,
  "estimatedHours": null,
  "dependencies": []
}
// Mettre à jour analysis.summary
```

**Action - Mettre à jour:**
```json
// Trouver fonction dans analysis.functions[], modifier champs
// Exemple: status "pending" → "analyzed", ajouter cppLocation, complexity
// Recalculer analysis.summary
```

### 5. Ajouter paramètre complété

**Input:** Report ID, Parameter info: {name, file, testsFile, testsStatus, registered}

**Action:**
```json
// Ajouter à development.completedParameters[]
{
  "name": "GetStartYear",
  "file": "Parameters/Date/GetStartYearParameter.cs",
  "testsFile": "Parameters/Date/GetStartYearParameterTests.cs",
  "testsStatus": "passing",
  "registered": true,
  "completedAt": "2025-01-18T14:30:00Z"
}
// Retirer de pendingParameters, mettre à jour summary
```

### 6. Ajouter décision

**Input:** Report ID, Question, Answer, Impact

**Action:**
```json
// Ajouter à decisions[]
{
  "date": "2025-01-18T11:00:00Z",
  "question": "Créer service domaine?",
  "answer": "Non, intégrer directement",
  "impact": "Implémentation plus simple"
}
```

### 7. Gérer blockers

**Ajouter blocker:**
```json
// Ajouter à blockers[]
{
  "date": "2025-01-18T13:00:00Z",
  "function": "CalculateAssetMix",
  "issue": "Fonction C++ non trouvée",
  "status": "open",
  "resolution": null
}
// Mettre à jour analysis.summary.blocked++
```

**Résoudre blocker:**
```json
// Trouver et mettre à jour
{
  "status": "resolved",
  "resolution": "Fonction trouvée dans validation_combo.c",
  "resolvedAt": "2025-01-18T15:00:00Z"
}
// Mettre à jour analysis.summary.blocked--
```

### 8. Changer phase

**Input:** Report ID, Nouvelle phase ("development", "completed")

**Action:**
```json
"currentPhase": "development"
// Si passage à "development":
//   - Vérifier analysis.status == "completed"
//   - Initialiser pendingParameters depuis analysis.functions
//   - Définir development.status = "in_progress"
```

### 9. Mettre à jour métriques tests

**Input:** Report ID, Tests info: {total, passing, failing, coverage}

**Action:**
```json
// Mettre à jour development.tests
{"total": 42, "passing": 42, "failing": 0, "coverage": 85.5}
```

### 10. Créer PR

**Input:** Report ID, PR info: {url, number}

**Action:**
```json
// Mettre à jour development.pr
{
  "created": true,
  "url": "https://github.com/org/repo/pull/123",
  "number": 123,
  "createdAt": "2025-01-18T16:00:00Z"
}
// Si tous Parameters complétés et tests passent: currentPhase = "completed"
```

## Helpers - Calcul Automatique

**Recalculer Summary (Analysis):**
```javascript
summary.totalFunctions = functions.length
summary.analyzed = functions.filter(f => f.status === "analyzed").length
summary.pending = functions.filter(f => f.status === "pending").length
summary.notFound = functions.filter(f => f.status === "not_found").length
summary.blocked = blockers.filter(b => b.status === "open").length
```

**Recalculer Summary (Development):**
```javascript
summary.totalParameters = completedParameters.length + pendingParameters.length
summary.implemented = completedParameters.length
summary.tested = completedParameters.filter(p => p.testsStatus === "passing").length
summary.registered = completedParameters.filter(p => p.registered).length
summary.pending = pendingParameters.length
```

**Timestamp ISO 8601:**
```bash
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

## Validation

Avant écriture:
1. Vérifier JSON valide
2. Vérifier champs obligatoires présents
3. Recalculer summaries pour cohérence

## Utilisation dans Workflows

**Dans `/report-analyst/analyze-report`:**
1. Début: Créer/lire état
2. Après extraction: Mettre à jour files.extraction, completedSteps
3. Après classification: Ajouter toutes fonctions
4. Après localisation: Mettre à jour cppLocation
5. Après analyse: Mettre à jour complexity, dependencies
6. Fin: Marquer analysis.status = "completed"

**Dans `/report-developer/migrate-report`:**
1. Début: Lire état, vérifier analysis.status == "completed"
2. Setup: Créer branche, mettre à jour development.branch
3. Après chaque Parameter: Ajouter à completedParameters
4. Après tests: Mettre à jour tests metrics
5. Après build: Mettre à jour build.lastStatus
6. Fin: Créer PR, marquer completed

**Dans `/migration/status`:**
→ Lire état, afficher currentPhase, progression, summary

**Dans `/migration/checklist`:**
→ Lire état, générer checklist dynamique basée sur completedSteps, functions[]

## Exemples d'Appels

**Créer état:**
```
Skill manage-state: créer état RPT-17858 "Gains et Pertes" GP_NON_REALISE
```

**Lire état:**
```
Skill manage-state: lire état RPT-17858
```

**Marquer étape:**
```
Skill manage-state: mettre à jour RPT-17858
- analysis.completedSteps: ajouter "extraction"
- analysis.currentStep: "classification"
```

**Ajouter fonction:**
```
Skill manage-state: ajouter fonction RPT-17858
- Name: InitGainLossCost
- Type: Specific, WidgetType: 3, EntryType: PRE, Status: pending
```
