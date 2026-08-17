---
name: list-report-parameters
description: Liste tous les paramètres d'un rapport depuis fields.csv avec leurs fonctions (Default/Specific) et type d'entrée (PRE/POST). Utiliser au début d'une migration pour avoir une vue d'ensemble des paramètres à traiter.
allowed-tools: Read, Grep, Bash
---

# Skill: List Report Parameters

Liste tous les paramètres d'un rapport à partir du fichier `docs/fields.csv`.

---

## Input

L'utilisateur fournit:
- **Nom interne du rapport**: Ex: `FOREIGN_PROPERTY`, `ASSETS_UNDER_MGT`

Si non fourni, demander à l'utilisateur.

---

## Exécution

### 1. Extraire les paramètres du CSV

Chercher dans `docs/fields.csv` toutes les lignes où la colonne `report_name` (colonne 1) correspond au nom interne fourni.

```bash
grep "^NOM_INTERNE," docs/fields.csv
```

### 2. Parser les colonnes

Pour chaque ligne trouvée, extraire:

| Colonne CSV | Position | Description |
|-------------|----------|-------------|
| `PARAM_NAME` | 2 | Nom du paramètre |
| `Default_Function` | 3 | Fonction par défaut (générique) |
| `Specific_Function` | 4 | Fonction spécifique au rapport |
| `PARAMETER_IMPL_FILE` | 7 | Fichier d'implémentation (ex: HiddenParametersImplementation.cs) |
| `PARAMETER_ENTRY_TYPE` | 8 | PRE ou POST |

### 3. Afficher la liste

Présenter les résultats sous forme de tableau:

```
| # | PARAM_NAME | Default_Function | Specific_Function | Impl_File | Entry |
|---|------------|------------------|-------------------|-----------|-------|
| 1 | PARAM_Xxx  | CheckTrue        |                   | HiddenParametersImplementation.cs | POST  |
| 2 | PARAM_Yyy  |                  | CustomFunction    | ComboBoxParametersImplementation.cs | PRE   |
```

### 4. Si aucun paramètre trouvé

Afficher:
```
Aucun paramètre trouvé pour le rapport "NOM_INTERNE" dans docs/fields.csv.
Vérifier que le nom interne est correct (colonne report_name du CSV).
```

### 5. Résumé

Après le tableau, afficher un résumé:
- Nombre total de paramètres
- Nombre PRE / POST
- Nombre avec Specific_Function (ceux qui pourraient nécessiter une analyse C++)
- Nombre sans Specific_Function (probablement déclaratifs)
