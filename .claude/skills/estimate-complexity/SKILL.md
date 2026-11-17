---
name: estimate-complexity
description: Évalue la complexité d'une fonction C++ (niveaux 0-4) pour estimer l'effort de migration vers C#. Distingue patterns déclaratifs (Niveau 0, 2min) de patterns impératifs (Niveaux 1-4, 30min-4h). Utiliser après avoir localisé le code C++ pour prédire le temps d'implémentation et identifier les risques.
---

# Skill: Estimate Complexity

Expert en évaluation de complexité de code C++ pour prédire l'effort de migration vers C#.

## Objectif

**RÈGLE CRITIQUE:** Identifier PRIORITAIREMENT si la fonction peut utiliser un pattern déclaratif (Niveau 0) avant d'estimer la complexité d'une implémentation custom (Niveaux 1-4).

Évaluer rapidement la complexité d'une fonction C++ pour:
1. **Détecter patterns déclaratifs** (>90% des cas, 2min)
2. **Estimer temps custom** si nécessaire (>10% des cas, 30min-4h)
3. **Identifier risques** de migration

## Input

- **Code source C++** (complet ou extrait significatif)
- **Nom fonction** (optionnel, contexte)
- **Widget Type** et **Entry Type** (optionnel)

OU référence fonction via skill `locate-cpp-function`

## Les 5 Niveaux de Complexité

### Niveau 0: Patterns Déclaratifs (2 min) ⭐ >90% DES CAS

**⚠️ VÉRIFIER EN PRIORITÉ AVANT de créer classe Parameter custom.**

**Référence:** Voir CLAUDE.md section "Hiérarchie d'Implémentation des Paramètres" et référence `.claude/conventions/reference/generic-functions-reference.md`

**Sous-niveaux déclaratifs:**

**0a. ValidationFunction="" (10s):**
- Fonction géré par `*ParametersImplementation.cs` (HiddenParametersImplementation, CheckBoxParametersImplementation, etc.)
- Ex: CheckTrue, CheckFalse, GetDisplayDate
- Migration: `ValidationFunction = ""`

**0b. InitialValue (2min):**
- `SetValue("constante")` sans conditions
- Ex C++: `pAtt->SetValue("SEC_V_Desc");`
- Migration C#: `InitialValue = "SEC_V_Desc"`

**0c. InitialValueFromPref (2min):**
- Lit `GetConfig()->get("PREF_XXX")` avec mapping simple (YES→1/NO→0)
- Ex C++: `CF_STRING sPref = GetConfig()->get("PREF_STRIP_BOND_GL1"); if (sPref == "YES") ... else ...`
- Migration C#: `InitialValueFromPref = "PREF_STRIP_BOND_GL1"`

**0d. InitialValueDateType (2min):**
- Date système (sys_date_fin) SANS calcul
- Ex C++: `pDate = new DATE_FIN(*sys_date_fin);`
- Migration C#: `InitialValueDateType = "LastProcessedDate"`

**⚠️ Helper Parameters (DÉPRÉCIÉ, 5-10min):**
- Ancienne approche: `implementationsDictionary["Period1"] = () => new StringParameter("3");`
- **NE PLUS UTILISER** - Remplacer par `InitialValue = "3"` (2min au lieu de 5-10min)

**Temps:** 10s-2min | **Risque:** Aucun | **Fichiers:** 1 (Parameters.cs) | **Classe:** ❌ NON

---

### Niveau 1: Transformation Simple Custom (30min-1h)

**⚠️ N'UTILISER QUE si Niveau 0 ne s'applique pas (transformation non-standard, logique minimale).**

**Caractéristiques:**
- Transformation ou calcul simple qui ne rentre pas dans patterns déclaratifs
- UNE dépendance simple (1 pref, 1 param, source type)
- Logique linéaire sans branches complexes

**Exemples C++:**
- Format conversion simple (non disponible en déclaratif)
- Lookup table simple avec 2-3 valeurs
- Calcul arithmétique trivial (date + 1 jour avec conditions spécifiques)

**Migration C#:** Créer petite classe `IValueProvidedParameter` custom

**Temps:** 30min-1h | **Risque:** Faible | **Fichiers:** 3 (Parameter, Executer, Tests) | **Classe:** ✅ OUI

### Niveau 2: Condition Simple (1h)

**⚠️ ATTENTION: Si condition simple sur 1 préférence (YES→1/NO→0), utiliser Niveau 0c (InitialValueFromPref) au lieu de créer classe.**

**Caractéristiques:**
- UN `if/else` avec logique NON-STANDARD (pas juste YES→1/NO→0)
- Condition sur source type (Pad)
- Transformation conditionnelle personnalisée

**Exemples C++:**
```c
// Cas A: Préférence avec logique NON-STANDARD (nécessite classe)
CF_STRING sPref = GetConfig()->get("PREF_CUSTOM_LOGIC");
if (sPref == "SPECIAL_VALUE") pAtt->SetValue("custom"); else pAtt->SetValue("default");

// Cas B: Sur type source (Pad) - nécessite classe
if (pad == REPORT_PORTFOLIO) pGroup->Select(false); else pGroup->Select(true);
```

**Migration C#:** Créer `IValueProvidedParameter` custom avec injection dépendances (`IPreferencesRepository` ou `SourceTypes`)

**Temps:** 1h (tests inclus) | **Risque:** Faible | **Fichiers:** 3 | **Classe:** ✅ OUI

### Niveau 3: Logique Multiple (1-2h)

**Caractéristiques:**
- Plusieurs conditions (`if/else if/else`) OU conditions composées (&&, ||)
- 2-3 préférences/paramètres
- Calculs simples (additions, comparaisons)
- Transformations strings basiques

**Exemple C++:**
```c
sAddTheo = GetConfig()->get("PREF_ADD_THEORETICAL");
sStripBond = GetConfig()->get("PREF_STRIP_BOND_GL1");
int iAddTheo = (sAddTheo == "YES") ? 1 : 0;
int iStripBond = (sStripBond == "YES") ? 1 : 0;
if (iAddTheo == 1 && iStripBond == 0) pAtt->SetValue("1"); else pAtt->SetValue("0");
```

**Migration C#:** Custom Parameter avec injection multiples repositories, tests unitaires exhaustifs (conditions combinées)

**Temps:** 1-2h | **Risque:** Moyen (edge cases) | **Effort:** Medium

### Niveau 4: Logique Complexe (2-4h+)

**Caractéristiques:**
- Boucles (`for`, `while`) sur collections
- Requêtes base de données
- Logique métier complexe (algorithmes, filtres)
- Interactions entre 4+ paramètres/préférences
- Calculs non-triviaux

**Exemple C++:**
```c
for (int i = 0; i < count; i++) {
    CF_INDUSTRY_CODE code = GetIndustryCode(i);
    if (code.IsValid() && code.Level() == targetLevel) {
        combo->AddItem(code.GetCode(), code.GetDescription());
    }
}
```

**Migration C#:** Custom Parameter + Service Domain, plusieurs repositories, tests exhaustifs avec mocks, documentation XML

**Temps:** 2-4h+ | **Risque:** Élevé (logique métier, dépendances) | **Effort:** Large

## Grille de Scoring

**Étape 1: VÉRIFIER PATTERNS DÉCLARATIFS (Niveau 0) EN PRIORITÉ:**

```
1. Fonction dans *ParametersImplementation.cs? → 0a (ValidationFunction="", 10s)
2. SetValue("constante") sans condition? → 0b (InitialValue, 2min)
3. GetConfig("PREF_") + if YES/NO → 1/0? → 0c (InitialValueFromPref, 2min)
4. Date système (sys_date_fin) sans calcul? → 0d (InitialValueDateType, 2min)
```

**Si AUCUN pattern déclaratif → Étape 2: Scoring pour classes custom:**

**Système de points (commencer à 0):**

| Critère | Points |
|---------|--------|
| **Conditions** | |
| 1 `if/else` simple (non-YES/NO) | +2 |
| 2-3 `if/else` | +3 |
| 4+ `if/else` ou `switch` | +4 |
| Conditions composées (&&, \|\|) | +1 |
| **Dépendances** | |
| 1 préférence avec logique non-standard | +2 |
| 2-3 préférences | +3 |
| 4+ préférences | +4 |
| Pad/SourceType | +2 |
| 1-2 paramètres (PARAM_) | +2 |
| 3+ paramètres | +3 |
| **Logique** | |
| Boucle simple (< 10 itérations) | +3 |
| Boucle complexe/imbriquée | +4 |
| Requête BD/Repository | +3 |
| Calculs arithmétiques simples | +1 |
| Algorithme complexe | +4 |
| Manipulation strings (split, regex) | +1 |

**Niveau final (classes custom seulement):**
- **0-2 points** → Niveau 1 (30min-1h)
- **3-4 points** → Niveau 2 (1h)
- **5-7 points** → Niveau 3 (1-2h)
- **≥8 points** → Niveau 4 (2-4h+)

## Tableau Référence Rapide

**Patterns Déclaratifs (>90% des cas, 0 classe):**

| Pattern C++ | Niveau | Temps | Migration C# |
|-------------|--------|-------|--------------|
| Fonction dans *ParametersImplementation.cs | 0a | 10s | `ValidationFunction = ""` |
| `SetValue("constante")` seul | 0b | 2min | `InitialValue = "constante"` |
| `GetConfig("PREF_") + if YES→1/NO→0` | 0c | 2min | `InitialValueFromPref = "PREF_XXX"` |
| `sys_date_fin` sans calcul | 0d | 2min | `InitialValueDateType = "LastProcessedDate"` |

**⚠️ Helper Parameters (DÉPRÉCIÉ - Ne plus utiliser):**

| Pattern C++ (ancien) | Ancien | Nouveau (déclaratif) |
|----------------------|--------|----------------------|
| `SetValue("constante")` | `StringParameter("X")` (5-10min) | `InitialValue = "X"` (2min) |
| `Select(true)` | `TrueParameter()` (5-10min) | `ValidationFunction = ""` (10s) |
| `Select(false)` | `FalseParameter()` (5-10min) | `ValidationFunction = ""` (10s) |

---

**Patterns Custom (>10% des cas, classe requise):**

| Pattern C++ | Niveau | Temps | Migration C# |
|-------------|--------|-------|--------------|
| Transformation simple non-standard | 1 | 30min-1h | Custom Parameter |
| `if (GetPad() == X) SetValue()` | 2 | 1h | Custom Parameter + SourceTypes |
| `if (GetPref() == CUSTOM_VALUE)` | 2 | 1h | Custom Parameter + IPreferencesRepository |
| `if (GetPref1() && GetPref2())` | 3 | 1-2h | Custom Parameter + IPreferencesRepository |
| `for (...) { GetFromDB() }` | 4 | 2-4h | Custom Parameter + Service Domain |
| Calculs + plusieurs params | 4 | 2-4h | Custom Parameter + Service Domain |

## Pièges Courants

**⚠️ Piège 0 (CRITIQUE): Ne pas vérifier patterns déclaratifs AVANT d'estimer**
→ >90% des fonctions utilisent InitialValue/InitialValueFromPref/etc. (2min) au lieu de classes custom (1-4h).
→ **TOUJOURS appliquer arbre de décision Niveau 0 EN PREMIER.**
→ Temps perdu moyen si oublié: 30min-2h par fonction (classe inutile créée).

**Piège 1: Créer classe pour simple préférence YES/NO**
→ `if (GetPref("PREF_XXX") == "YES") SetValue("1")` → Utiliser `InitialValueFromPref` (2min), PAS classe custom (1h).

**Piège 2: Utiliser Helper Parameters (déprécié)**
→ `StringParameter("3")` prend 5-10min. Utiliser `InitialValue = "3"` à la place (2min).

**Piège 3: Surévaluer complexité apparente**
→ Fonction de 100 lignes mais 90 lignes = config UI. Identifier seulement les `SetValue()` - seule logique à migrer.

**Piège 4: Sous-estimer dépendances**
→ Fonction simple mais préférence inexistante en C#. Vérifier existence des préférences AVANT de commencer.

**Piège 5: Ignorer edge cases**
→ Fonction avec `if (value == -1)` non documenté. Lire TOUT le code, pas juste happy path.

## Validation Estimation

Après implémentation, comparer temps réel vs estimé:
- **< 80% estimé:** Surestimation - revoir méthode
- **80-120%:** Estimation correcte
- **> 120%:** Sous-estimation - risques non identifiés

Ajuster estimations futures selon écarts observés.

## Références

**Hiérarchie déclarative (LIRE EN PREMIER):**
- **CLAUDE.md** - Section "Hiérarchie d'Implémentation des Paramètres" (principes + arbre de décision)
- Référence `.claude/conventions/reference/generic-functions-reference.md` - Référence complète des 6 niveaux avec exemples détaillés
- Référence `.claude/conventions/reference/read-cpp-patterns.md` - Guide de lecture rapide du code C++ (scan 10-60s)

**Workflow:**
- Skill `classify-functions` (avant) - Détection patterns déclaratifs
- Skill `locate-cpp-function` (avant) - Localisation code source
- Skill `estimate-complexity` (actuel) - Estimation temps
- Skill `analyze-cpp-function` (après) - Analyse approfondie

**Documentation:**
