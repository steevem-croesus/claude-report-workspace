---
name: read-cpp-patterns
description: Guide de lecture rapide du code C++ legacy sans être expert. Identifie ce qui est important (logique métier) vs ce qu'il faut ignorer (boilerplate, UI). Utiliser pour analyser rapidement le code C++ source.
---

# Skill: Read C++ Patterns

Guide pratique pour lire et comprendre le code C++ legacy **sans être expert en C++**.

## Objectif

Apprendre à lire rapidement le code C++ des rapports pour identifier:
- **IMPORTANT** (logique métier, valeurs retournées)
- **IGNORER** (boilerplate, UI, null checks)
- **Technique de scanning rapide** (10s, 5s, 30-60s)

**Utilisé par:** report-analyst, report-developer

---

## Patterns C++ Courants

### CRITIQUE: Définir/Récupérer Valeur

```c
pAtt->SetValue("1");              // Valeur retournée - IMPORTANT!
pGroup->Select(true/false);       // Checkbox - IMPORTANT!
```

**C#:** `parameter.InitialValue = "1"` ou `"0"`

---

### CRITIQUE: Préférences et Contexte

```c
CF_STRING sPref = GetCresusConfig()->get("PREF_XXX");  // Préférence
eReportPad pad = pReportApi->GetPad();                 // Source type (Client/Account/Portfolio)

if (sPref == "YES") { ... }
if (pad == REPORT_CLIENT) { ... }
```

**C#:**
- Préférence → `_preferencesRepository.GetPreference("PREF_XXX")`
- Source type → `_requestSourceType == SourceTypes.Client`

---

### IMPORTANT: Callbacks et Helpers

```c
// Callbacks - chercher CHAQUE fonction
m_pParam->SetInit(C_VALIDATION_XXX::InitFunction);
m_pParam->SetValue(C_VALIDATION_XXX::SetFunction);

// Helper - lire la fonction appelée
void InitPeriod1(...) {
    InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);  // Chercher InitPeriod
}
```

---

### IGNORER: Boilerplate C++

```c
C_ATTRIBUTE *pAtt = pGroup->GetValue();               // Récupération
if (pAtt == NULL) { return; }                        // Null check
C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_...) in_pGroup;  // Cast
int nValue = 0; bool bFlag = false;                  // Déclarations

// Logique UI - IGNORER COMPLÈTEMENT
SetDlgItemText(hDlg, ...); EnableWindow(...); ShowWindow(...);
SendMessage(...); HWND hDlg;
```

**Action:** Passer directement aux SetValue, GetCresusConfig, GetPad, if métier

---

## Technique de Scanning Rapide

### 1. Scan Visuel (10s)

Chercher visuellement:
- `SetValue` → Valeur retournée
- `GetCresusConfig` → Préférence
- `GetPad` → Source type
- `if` → Logique conditionnelle

### 2. Compter (5s)

- **SetValue:** 1 = simple, 2+ = conditions
- **GetCresusConfig:** 0 = statique, 1 = simple, 2+ = moyen
- **if:** 0-1 = simple, 2+ = moyen

**Exemple:**
```c
void InitSomething(...) {
    CF_STRING sPref1 = GetCresusConfig()->get("PREF_A");  // 1
    CF_STRING sPref2 = GetCresusConfig()->get("PREF_B");  // 2
    if (sPref1 == "YES" && sPref2 == "NO") {             // 1 if
        pAtt->SetValue("1");  // 1
    } else {
        pAtt->SetValue("0");  // 2
    }
}
```

**Comptage:** 2 prefs + 1 if + 2 SetValue → **Niveau 2-3**

### 3. Lire Logique (30-60s)

1. **Identifier flux:**
   - Début fonction → Déclarations (ignorer)
   - Milieu → Préférences/Paramètres/Source (lire)
   - Conditions if/else (lire)
   - SetValue (noter valeurs)

2. **Noter seulement:**
   - Noms PREF_XXX
   - Comparaisons (== "YES", != "NO")
   - Valeurs SetValue ("0", "1", "2024")

3. **Ignorer complètement:**
   - Tout code UI (hDlg, SetDlgItemText, EnableWindow)
   - Casts ((C_WINDOW_PARAM_GROUP_CHECK *))
   - Null checks basiques (if (pAtt == NULL))

---

## Exemples Annotés

### Exemple 1: Fonction Triviale (10s)

```c
void C_VALIDATION_CHECK::InitSinceInceptionCheck(C_WINDOW_PARAM_GROUP *in_pGroup) {
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;  // ← IGNORER
    C_ATTRIBUTE *pAtt = pGroup->GetValue();  // ← IGNORER
    if (pAtt == NULL) { return; }            // ← IGNORER

    pGroup->Select(true);  // ← LIRE: Checkbox cochée = "1"
}
```

**Scan 10s:** 1 Select(true) → Niveau 1 → Helper Parameter

---

### Exemple 2: Condition Simple (20s)

```c
void C_VALIDATION_CHECK::InitDefaultIndex(C_WINDOW_PARAM_GROUP *in_pGroup) {
    // 10 lignes boilerplate - IGNORER
    const C_REPORT_API *pReportApi = pGroup->GetReportApi();  // ← LIRE

    if (pReportApi != NULL && pReportApi->GetPad() == REPORT_PORTEF) {  // ← LIRE: Source type
        pGroup->Select(false); pGroup->Enable(false);  // UI - IGNORER sauf valeur
        pAtt->SetValue("0");  // ← NOTER: Portfolio → "0"
    } else {
        pAtt->SetValue("1");  // ← NOTER: Autres → "1"
    }
}
```

**Scan 20s:** GetPad → 1 if → 2 SetValue → Niveau 2 → Custom Parameter avec SourceTypes

---

### Exemple 3: Préférences Multiples (40s)

```c
void InitComplexCheck(...) {
    // Boilerplate - IGNORER
    CF_STRING sAddTheo = GetCresusConfig()->get("PREF_ADD_THEORETICAL_VALUE");  // ← NOTER: PREF_ADD_THEORETICAL_VALUE
    CF_STRING sStripBond = GetCresusConfig()->get("PREF_STRIP_BOND_GL1");       // ← NOTER: PREF_STRIP_BOND_GL1

    int iAddTheo = (sAddTheo == "YES") ? 1 : 0;          // ← LIRE: Conversion YES → 1
    int iStripBond = (sStripBond == "YES") ? 1 : 0;       // ← LIRE: Conversion YES → 1

    if (iAddTheo == 1 && iStripBond == 0) {              // ← LIRE: Condition composée
        pAtt->SetValue("1");  // ← NOTER: Cas A → "1"
    } else {
        pAtt->SetValue("0");  // ← NOTER: Cas B → "0"
    }
}
```

**Scan 40s:** 2 prefs + 1 if composé → Niveau 3 → Custom Parameter avec IPreferencesRepository

**Notes migration:**
- Dépendances: IPreferencesRepository
- Logique: (PREF_ADD == YES && PREF_STRIP == NO) → "1", sinon "0"
- Tests: 4 cas (YES/YES, YES/NO, NO/YES, NO/NO)

---

## Checklist Analyse Rapide

1. **Ouvrir fichier C++**
2. **Scan 10s:** Chercher SetValue/Select → Compter
3. **Scan 5s:** Compter GetCresusConfig, GetPad, if
4. **Estimer:** Niveaux 0-4 basé sur comptage
5. **Si complexe (3-4):** Lire logique 30-60s
6. **Noter:** PREF_XXX, valeurs, conditions
7. **Ignorer:** Tout le reste

---

## Patterns de Simplification

### Pattern 1: Helper Appelé

```c
void InitPeriod1(...) {
    InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);  // Helper avec "3"
}
```

**Action:** Chercher `InitPeriod` → Si juste SetValue → Simplifier à StringParameter("3")

### Pattern 2: Callbacks Multiples

```c
m_pParam->SetInit(C_VALIDATION_COMBO::InitAssetMix);
m_pParam->SetValue(C_VALIDATION_COMBO::SetAssetMix);
```

**Action:** Localiser CHAQUE callback, lire logique, combiner dans C#

### Pattern 3: Switch/Case

```c
switch (pad) {
    case REPORT_CLIENT: pAtt->SetValue("1"); break;
    case REPORT_ACCOUNT: pAtt->SetValue("2"); break;
    default: pAtt->SetValue("0");
}
```

**Action:** Noter mapping direct (Client=1, Account=2, Défaut=0)

---

## Anti-Patterns à Reconnaître

**❌ Piège 1: Complexité Apparente**
```c
// 100 lignes de code...
// 90 lignes = UI (IGNORER)
// 10 lignes = logique métier (LIRE)
pAtt->SetValue("1");  // Seule ligne importante!
```

**❌ Piège 2: Fonctions Alias**
```c
void InitFunc1(...) { InitHelper(...); }
void InitFunc2(...) { InitHelper(...); }  // Identique!
```

**Action:** Créer UNE classe, DEUX enregistrements

**❌ Piège 3: Conditions Redondantes**
```c
if (sPref == "YES") {
    // 20 lignes UI - IGNORER
    pAtt->SetValue("1");
} else {
    // 15 lignes UI - IGNORER
    pAtt->SetValue("0");
}
```

**Action:** Simplifier à `pref == "YES" ? "1" : "0"`

---

## Références

**Skills:** `estimate-complexity` (utilise ces patterns), `analyze-cpp-function` (analyse approfondie), `migration-examples` (exemples concrets)

**Fichiers C++:** `repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_*.c`
