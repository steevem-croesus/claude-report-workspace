---
name: extract-parameters
description: Extrait et structure les paramètres de rapport depuis docs/fields.csv. Utiliser quand on analyse un nouveau rapport pour migration C++ vers C# - il suffit de fournir la clé du rapport.
---

# Skill: Extract Parameters

Extraction et structuration des paramètres de rapport pour migration C++ → C#.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Objectif

Créer fichier de travail structuré `.work/{slug}/analysis-extraction.md` à partir de `docs/fields.csv`.

## Processus

### 1. Collecte données

Demander:
- Report ID (ex: `RPT-17858`)
- Clé du rapport dans le CSV (ex: `GP_NON_REALISE`, `ACCUM_INTEREST`, `PERF_ACC_SUMMARY`)
- Nom du rapport (français)

**Source des données:** `docs/fields.csv`

**Colonnes disponibles:**
`report_name`, `PARAM_NAME`, `Default_Function`, `Specific_Function`, `Default_Initial_Value_From_Pref`, `Specific_Initial_Value_From_Pref`, `PARAMETER_IMPL_FILE`, `PARAMETER_ENTRY_TYPE`, `WIDGET_TYPE`

### 1.1 Extraction depuis CSV

```python
import csv

# Lire le CSV et filtrer par report_name
with open('docs/fields.csv', 'r') as f:
    reader = csv.DictReader(f)
    rows = [r for r in reader if r['report_name'] == '{REPORT_KEY}']

print(f"Paramètres trouvés: {len(rows)}")
```

**Si aucun paramètre trouvé:** Vérifier la clé avec:
```python
# Lister les rapports disponibles contenant un mot-clé
keys = set(r['report_name'] for r in csv.DictReader(open('docs/fields.csv')))
matches = [k for k in keys if 'KEYWORD' in k.upper()]
```

### 2. Validation

Vérifier:
- Au moins: `PARAM_NAME`, `PARAMETER_ENTRY_TYPE`, `WIDGET_TYPE`
- Au moins une de: `Default_Function` OU `Specific_Function`
- Au moins une ligne de données

Si colonnes manquantes: demander données ou continuer avec disponibles (documenter limitations).

### 3. Parsing et structuration

**Structure:**
```
List<ParameterInfo>:
  - ParamName, DefaultFunction, SpecificFunction
  - DefaultPref, SpecificPref, ImplFile
  - EntryType: "PRE" | "POST", WidgetType: int
```

**Tri:**
1. `PARAMETER_ENTRY_TYPE` (PRE avant POST)
2. `WIDGET_TYPE` (1→2→3→4→5→7→8→9)
3. Alphabétique `PARAM_NAME`

### 3.1 Interprétation colonnes

| Colonne | Utilisation | Exemple |
|---------|-------------|---------|
| `PARAM_NAME` | Identifier dans Parameters.cs | `PARAM_IndCodeCombo` |
| `Default_Function` | Fonction générique réutilisable | `IndCodeCombo` |
| `Specific_Function` | **PRIORITÉ** sur Default si les deux | `InitGainLossCost` |
| `Default/Specific_Initial_Value_From_Pref` | Dépendance préférence | `PREF_SHOW_CHECK_DIGIT` |
| `PARAMETER_IMPL_FILE` | Organisation code C# | `ComboBoxParametersImplementation.cs` |
| `PARAMETER_ENTRY_TYPE` | Détermine executer (Pre/Post) | `PRE` ou `POST` |
| `WIDGET_TYPE` | Indique fichier C++ source | `1` (Combo), `3` (Check) |

**Règle:** Si `Default_Function` ET `Specific_Function`, toujours **Specific prioritaire**.

**Exemple:**
```csv
PARAM_GainLossCost,DisplayCheckDigit,InitGainLossCost,CheckBoxParametersImplementation.cs,PRE,3
```
→ Fonction: `InitGainLossCost` (specific prioritaire) | C++: `validation_check.c` (Widget 3) | Executer: `PreParamEntry...`

### 3.5 Validation mapping (facultatif mais recommandé)

Pour paramètres critiques (dates, fonctions similaires), vérifier dans code C++ source:

```bash
# Si PARAM_StartDate/EndDate détectés → Chercher les deux fonctions
grep -E "(StartDate|EndDate)" repos/CroesusServer/Src/.../validation_date.c

# Vérifier quelle fonction s'applique à quel paramètre
# Alerter si confusion possible
```

**Ajouter section warnings dans fichier de travail si ambiguïtés détectées.**

### 4. Création fichier de travail

**Créer:** `.work/{slug}/analysis-extraction.md`

```markdown
# Migration: {Nom} ({REPORT-ID})

**Date:** {date} | **Paramètres:** {count} (PRE: {x} | POST: {y})

## Vue d'ensemble

- **Report ID:** {REPORT-ID}
- **Nom:** {nom français}
- **Paramètres PRE:** {count_pre}
- **Paramètres POST:** {count_post}

## Résumé par Widget

| Widget | Description | PRE | POST |
|--------|-------------|-----|------|
| 1 | Combobox | X | X |
| 2 | Radio | X | X |
| 3 | Checkbox | X | X |
| 4 | List | X | X |
| 5 | Date | X | X |
| 7 | String/File | X | X |
| 8 | Hidden | X | X |
| 9 | MultiLangTextBox | X | X |

## Résumé par Implementation File

| File | Count |
|------|-------|
| ComboBoxParametersImplementation.cs | X |
| ... | ... |

## Paramètres PRE

### Widget 1 - Combobox
| PARAM_NAME | Default_Function | Specific_Function | Impl File | Notes |
|------------|------------------|-------------------|-----------|-------|
| ... | ... | ... | ... | ... |

### Widget 2 - Radio
[Même structure pour chaque widget type]

## Paramètres POST

### Widget 8 - Hidden
[Même structure]

## Données Brutes (CSV)

```csv
{CSV complet original}
```

## Prochaines Étapes

- [ ] Classification fonctions (`/classify-functions`)
- [ ] Localisation code C++ pour fonctions spécifiques
- [ ] Analyse dépendances
- [ ] Création spec détaillée
```

### 5. Statistiques et résumé

Générer statistiques et afficher résumé console:

```
Extraction terminée: {REPORT-ID}

Fichier: .work/{slug}/analysis-extraction.md

Stats:
├─ Total: XX (PRE: X | POST: X)
├─ Widgets: Combo: X, Radio: X, Check: X, List: X, Date: X, String: X, Hidden: X, MultiLang: X

Fonctions:
├─ Default seul: XX (XX%)
├─ Specific seul: XX (XX%)
├─ Both (Default+Specific): XX (XX%)
└─ Aucune: XX (XX%) ⚠️ investiguer

Préférences: {count} uniques détectées

Complexité estimée (préliminaire):
├─ Trivial (0-1): ~X params × 20min = Xh
├─ Simple (2): ~X params × 45min = Xh
├─ Moyen (3): ~X params × 90min = Xh
└─ Complexe (4): ~X params × 180min = Xh

Temps estimé: {min}h - {max}h

Prochaines étapes:
1. Skill 'locate-cpp-function' pour fonctions spécifiques
2. Vérifier fonctions Default déjà implémentées
3. Prioriser par complexité (trivial → complexe)
```

### 5.1 Estimation complexité

| Pattern | Complexité | Critère |
|---------|-----------|---------|
| Default seul (commune) | 0-1 | Probablement implémentée/simple |
| Specific sans pref | 1-2 | Logique custom simple |
| Specific + 1 pref | 2 | Condition simple |
| Specific + 2+ prefs | 3 | Logique combinatoire |
| Widget 8 (Hidden) | 2-4 | Calculs internes complexes |

## Cas Particuliers

**CSV avec colonnes supplémentaires** (`LABEL_FR`, `TOOLTIP`, etc.):
→ Inclure dans données brutes, afficher si pertinentes

**Paramètres sans fonctions** (Default ET Specific vides):
→ Marquer "À INVESTIGUER" - possiblement valeur hardcodée ou gestion framework

**Préférences** (`PREF_`):
→ Noter dans colonne "Notes" (ex: "Init from PREF_SHOW_CHECK_DIGIT")

## Validation Finale

- [ ] Fichier `.work/{slug}/analysis-extraction.md` créé
- [ ] Tous paramètres CSV présents
- [ ] Statistiques correctes
- [ ] Tableaux formatés
- [ ] CSV brut inclus

## Widget Types Référence

| Type | Description | C++ File |
|------|-------------|----------|
| 1 | Combobox | validation_combo.c |
| 2 | Radio | validation_radio.c |
| 3 | Checkbox | validation_check.c |
| 4 | List | validation_list.c |
| 5 | Date | validation_date.c |
| 7 | String/File | validation_file.c |
| 8 | Hidden | validation_hided.c |
| 9 | MultiLangTextBox | validation_multilang_textbox.c |

## Références

Prochaine étape: Classification fonctions (Étape 2)
