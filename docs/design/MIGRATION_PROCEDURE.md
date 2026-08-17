# Procédure de Migration des Rapports C++ → C#

Ce document détaille la méthodologie complète pour migrer un rapport du legacy C++ (CroesusServer) vers le nouveau système C# (ReportManagerApi).

**Basé sur l'analyse de:** PR #5972 - Rapport "Gains et Pertes Non Réalisés" (GP_NON_REALISE)

---

## Table des Matières

1. [Vue d'ensemble du processus](#vue-densemble-du-processus)
2. [Étape 1: Extraction des paramètres](#étape-1-extraction-des-paramètres)
3. [Étape 2: Classification des fonctions](#étape-2-classification-des-fonctions)
4. [Étape 3: Localisation du code C++](#étape-3-localisation-du-code-c)
5. [Étape 4: Implémentation C#](#étape-4-implémentation-c)
6. [Étape 5: Enregistrement](#étape-5-enregistrement)
7. [Étape 6: Tests](#étape-6-tests)
8. [Patterns et transformations](#patterns-et-transformations)
9. [Checklist finale](#checklist-finale)

---

## Vue d'ensemble du processus

### Flux de migration

```
SQL Query → Extraction CSV → Classification → Recherche C++ → Implémentation C# → Tests
```

### Fichiers clés impliqués

1. **Source (Lecture seule):**
   - `repos/CroesusServer/Src/**/*.cpp, *.h` - Code C++ original

2. **Destination (Migration):**
   - `repos/ReportFoundations/ReportImplementations/.../Reports/.../Parameters.cs` - Définition des paramètres du rapport
   - `ReportManagerAPI.Infrastructure/.../ValueProviderFunctions/Parameters/` - Implémentations des fonctions
   - `ReportManagerAPI.Infrastructure/.../Pre|PostParamEntryValueProviderFunctionsExecuter.cs` - Enregistrement
   - `repos/ReportFoundations/ReportImplementations/.../SpecificTypes/*ParametersImplementation.cs` - Implémentations génériques

3. **Tests:**
   - `ReportManagerAPI.Infrastructure.SmallTests/.../Parameters/` - Tests unitaires

---

## Étape 1: Extraction des paramètres

### 1.1 Exécuter la requête SQL

La requête SQL pour un rapport retourne les colonnes suivantes:

| Colonne | Description |
|---------|-------------|
| `PARAM_NAME` | Nom du paramètre (ex: `PARAM_IndCodeCombo`) |
| `Default_Function` | Fonction générique (souvent déjà implémentée) |
| `Specific_Function` | Fonction spécifique au rapport (à migrer) |
| `Default_Initial_Value_From_Pref` | Préférence pour valeur par défaut |
| `Specific_Initial_Value_From_Pref` | Préférence spécifique |
| `PARAMETER_IMPL_FILE` | Fichier C# de destination |
| `PARAMETER_ENTRY_TYPE` | `PRE` ou `POST` |
| `WIDGET_TYPE` | Type de widget UI |

### 1.2 Créer un fichier de travail

Créer `docs/MIGRATION-{REPORT-ID}.md` avec le CSV complet pour référence.

**Exemple pour RPT-17858 (GP_NON_REALISE):**

```csv
PARAM_NAME,Default_Function,Specific_Function,PARAMETER_IMPL_FILE,PARAMETER_ENTRY_TYPE
PARAM_IndCodeCombo,IndCodeCombo,,ComboBoxParametersImplementation.cs,PRE
PARAM_Pagination,PaginationVisible,PaginationVisible,ComboBoxParametersImplementation.cs,PRE
PARAM_AssetMixRepartitionID,AssetMixRepartitionCombo,,ComboBoxParametersImplementation.cs,PRE
PARAM_AvgCostCalculMethod,CostCalculation,,RadioParametersImplementation.cs,PRE
PARAM_GainLossCostDisplayed,,InitGainLossCostDisplayed,CheckBoxParametersImplementation.cs,PRE
...
```

---

## Étape 2: Classification des fonctions

### 2.1 Identifier le type de fonction

Pour chaque paramètre, déterminer:

**A. Fonction générique (Default_Function)**
- Souvent déjà implémentée dans `PARAMETER_IMPL_FILE`
- Réutilisable entre plusieurs rapports
- Exemples: `CheckFalse`, `CheckTrue`, `GetFirmCurrency`, `AsOfDate`

**B. Fonction spécifique (Specific_Function)**
- Logique unique au rapport
- **DOIT être migrée du C++**
- Exemples: `InitGainLossCostDisplayed`, `AssetMixRadioButton`, `EvalSimpleEntryPoint`

**C. Fonction basée sur préférence**
- Utilise `Default_Initial_Value_From_Pref` ou `Specific_Initial_Value_From_Pref`
- Pattern: `GetBoolFromPref(PREF_XXX)`
- Souvent déjà implémenté via framework

### 2.2 Prioriser par statut

**Statut 1: Déjà implémenté ✅**
- Vérifier existence dans `Pre|PostParamEntryValueProviderFunctionsExecuter.cs`
- Pas de `UnimplementedParameter()`
- Aucune action requise

**Statut 2: Marqué TODO ⚠️**
- Existe comme `UnimplementedParameter() // TODO`
- **Priorité haute** - blocage pour le rapport
- Nécessite migration C++ → C#

**Statut 3: Inexistant 🔴**
- Pas d'entrée dans l'executer
- **Priorité critique** - doit être créé
- Recherche C++ + implémentation complète

### 2.3 Règle de priorité Default vs Specific

Lorsqu'un paramètre a BOTH `Default_Function` ET `Specific_Function`:

**Règle générale:** **Specific_Function a TOUJOURS priorité**

**Exemple:**
```csv
PARAM_DoGraphAssetMix,CheckFalse,PerfDoGraphAssetMix
```
→ Utiliser `PerfDoGraphAssetMix` (Specific), ignorer `CheckFalse` (Default)

**Cas particuliers - Conflits apparents:**

Si Default et Specific ont des valeurs contradictoires (ex: CheckTrue vs CheckFalse):
1. **Vérifier le code C** pour comprendre la logique conditionnelle
2. Possibilité: Default pour certains pads, Specific pour d'autres contextes
3. **Toujours privilégier Specific** sauf indication contraire dans le code C
4. Documenter l'anomalie dans les commentaires du code C#

**Exemples détectés dans PERF_ACC_SUMM:**
- `PARAM_NonZeroTotalsOnly`: Default=CheckTrue, Specific=CheckFalse → Utiliser CheckFalse
- `PARAM_KeepInvalidPeriods`: Default=CheckFalse, Specific=CheckTrue → Utiliser CheckTrue

**Fonctions alias (même implémentation):**

Certains paramètres ont Default ≠ Specific mais avec la même logique:
```csv
PARAM_PerformanceIndexes,IndexListWhithIndexPerso,IndexListWhithIndexPersoSymb
```

Dans ce cas:
1. Vérifier si les deux fonctions ont EXACTEMENT la même implémentation en C
2. Si oui, créer UNE SEULE implémentation C# et la réutiliser
3. Les deux noms pointeront vers la même classe Parameter dans l'executer

---

## Étape 3: Localisation du code C++

### 3.1 Structure des fichiers de validation

**⚠️ IMPORTANT:** Chercher dans les fichiers `.c` et `.h` UNIQUEMENT (PAS les `.cpp`)

**Localisation EXACTE:**
```
repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/
├── validation_check.c/.h              ← Checkbox parameters (PRE, WIDGET_TYPE=3)
├── validation_combo.c/.h              ← Combobox parameters (PRE, WIDGET_TYPE=1)
├── validation_radio.c/.h              ← Radio button parameters (PRE, WIDGET_TYPE=2)
├── validation_date.c/.h               ← Date parameters (PRE, WIDGET_TYPE=5)
├── validation_hided.c/.h              ← Hidden parameters (POST, WIDGET_TYPE=8)
├── validation_list.c/.h               ← List parameters (PRE, WIDGET_TYPE=4)
├── validation_file.c/.h               ← String/File parameters (PRE, WIDGET_TYPE=7)
├── validation_multilang_textbox.c/.h  ← Multi-language textbox (PRE, WIDGET_TYPE=9)
└── ctr_param.c/.h                     ← Controller orchestration
```

**Mapping SQL → Fichier C:**

| SQL: WIDGET_TYPE | SQL: ENTRY_TYPE | Fichier C source |
|------------------|-----------------|------------------|
| 1 (Combobox) | PRE | `validation_combo.c` |
| 2 (Radio) | PRE | `validation_radio.c` |
| 3 (Checkbox) | PRE | `validation_check.c` |
| 4 (List) | PRE | `validation_list.c` |
| 5 (Date) | PRE | `validation_date.c` |
| 7 (String) | PRE | `validation_file.c` |
| 8 (Hidden) | POST | `validation_hided.c` |
| 9 (MultiLangTextBox) | PRE | `validation_multilang_textbox.c` |

**Note:** Il n'y a pas de WIDGET_TYPE=6 dans l'enum (probablement réservé ou supprimé).

### 3.2 Stratégie de recherche

**Étape 1: Identifier le bon fichier**

Depuis le SQL, regarder `WIDGET_TYPE` et `PARAMETER_ENTRY_TYPE`:

```bash
cd repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/

# Liste des fichiers disponibles
ls -la validation_*.c
```

**Étape 2: Chercher la fonction**

```bash
# Pour Default_Function ou Specific_Function du SQL
grep -n "FunctionName" validation_[type].c | head -10

# Exemples concrets:
grep -n "InitDisplayCheckDigit" validation_check.c
grep -n "InitGainLossCostDisplayed" validation_check.c
grep -n "AssetMixRadioButton" validation_radio.c
grep -n "GetFirmCurrency" validation_hided.c
```

**Étape 3: Lire l'implémentation**

```bash
# Méthode 1: grep -A (After context)
grep -A 50 "void.*InitDisplayCheckDigit" validation_check.c

# Méthode 2: sed avec numéro de ligne
# (utiliser le numéro de ligne trouvé à l'étape 2)
sed -n '1234,1300p' validation_check.c

# Méthode 3: Ouvrir dans éditeur
vim +/InitDisplayCheckDigit validation_check.c
```

**Étape 4: Stratégie pour noms de fonctions non standard**

Si `grep -n "FunctionName" validation_*.c` ne retourne **aucun résultat**:

**Plan B - Recherche par fragments:**

Décomposer le nom en fragments significatifs et chercher chaque partie:

```bash
# Exemple: PerfAccSummGetSubReportField
# → Décomposer en: "AccSumm" + "SubReportField"

grep -n "AccSumm" validation_hided.c
grep -n "SubReportField" validation_hided.c
grep -n "GetSubReport" validation_hided.c
```

**Plan C - Recherche par nom de paramètre:**

Chercher le nom du paramètre SQL (`PARAM_XXX`) dans le code C:

```bash
# Exemple: pour PARAM_RPTSubId
grep -n "PARAM_RPTSubId" validation_hided.c
grep -rn "RPTSubId" Src/ReportApi/
```

**Plan D - Recherche contextuelle par pattern:**

Chercher des fonctions similaires pour déduire le naming pattern:

```bash
# Pour des fonctions Perf*:
grep -n "^void.*Perf" validation_hided.c | head -20

# Pour des fonctions *DataEntryPoint:
grep -n "DataEntryPoint" validation_hided.c

# Pour des fonctions Set*:
grep -n "^void.*Set.*RptView" validation_hided.c
```

**Plan E - Examiner le rapport spécifique:**

Parfois les fonctions sont définies dans des fichiers propres au rapport:

```bash
# Chercher dans toute la hiérarchie ReportApi
cd repos/CroesusServer/Src/ReportApi
grep -rn "PerfAccSummGetSubReportField" .
```

**Dernier recours - Analyser les fonctions similaires:**

Si vraiment introuvable, examiner les implémentations C# existantes pour des fonctions similaires et déduire la logique attendue à partir du nom et du contexte du rapport.

### 3.3 Types de fonctions trouvées

**Pattern A: Fonction Init simple (PRE)**

```c
void C_VALIDATION_CHECK::InitDisplayCheckDigit(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    // Implémentation directe
    bool bDisplayCheckDigit = HasPrefCheckDigit();
    pGroup->SetHideWidgetFlag(!bDisplayCheckDigit);
    pAtt->SetValue("0");
}
```

**Migration:** Créer IValueProvidedParameter avec logique équivalente.

**Pattern B: Fonction callback handler (Radio/Combo)**

```c
else if (in_sFunction == "AssetMixRadioButton")
{
    m_pParam->SetInit(InitAssetMixWrapper);
    m_pParam->SetValue(C_VALIDATION_RADIO::SetAssetMix);
    m_pParam->SetGetValue(C_VALIDATION_RADIO::GetAssetMix);
    m_pParam->SetGetDisplayValue(C_VALIDATION_RADIO::GetDisplayAssetMix);
}
```

**Migration:** Chercher CHAQUE callback (`InitAssetMixWrapper`, `SetAssetMix`, etc.) et migrer la logique combinée.

**Pattern C: Fonction POST simple (Hidden)**

```c
void C_VALIDATION_HIDED::GetPad (C_WINDOW_PARAM_GROUP *in_pGroup)
{
    pAtt->SetValue(CF_STRING(pReportApi->GetPad()));
}
```

**Migration:** Souvent déjà générique dans HiddenParametersImplementation.cs

### 3.4 Identifier les dépendances

Lors de l'analyse du code C, noter:

| Pattern C | Signifie | Repository C# requis |
|-----------|----------|---------------------|
| `GetCresusConfig()->get("PREF_XXX")` | Accès préférence | `IPreferencesRepository` |
| `HasPrefCheckDigit()`, `HasPref*()` | Vérification préférence | `IPreferencesRepository` |
| `GetParam("PARAM_XXX")` | Accès paramètre rapport | `IReportCommandAndQueryContextRepository` |
| `pReportApi->GetPad()` | Type de source (pad) | `SourceTypes` (injection constructor) |
| `DATE_FIN`, date operations | Gestion dates | `IParameterDateValueService`, `IDateTimeService` |
| Database queries, SQL | Accès BD | Repository spécifique |
| Repartition logic | Répartitions | `IRepartitionRepository` |
| Industry codes | Codes industrie | `IIndustryCodeRepository` |
| Indexes | Indices | `IIndexesRepository` |
| Transactions | Transactions | `ITransactionsRepository` |

**Exemples réels:**

```c
// Préférence simple
CF_STRING sPref = GetCresusConfig()->get("PREF_DISPLAY_CHECK_DIGIT");
// → _preferencesRepository.GetPreference("PREF_DISPLAY_CHECK_DIGIT")

// Source type
eReportPad pad = pReportApi->GetPad();
if (pad == REPORT_CLIENT) { ... }
// → if (_requestSourceType == SourceTypes.Client) { ... }

// Comparaison YES/NO
if (sPref.CompareCaseInsensitive("YES") == 0) { ... }
// → if (pref?.Value?.ToUpper() == "YES") { ... }
```

### 3.5 Documenter la logique

Pour chaque fonction C, créer une note dans le fichier de migration:

```markdown
### FunctionName

**Fichier C:** `Src/ReportApi/ReportCtr/ReportCtrParam/validation_check.c:ligne 1234`

**Logique:**
1. Récupère préférence PREF_ADD_THEORETICAL_VALUE
2. Récupère préférence PREF_STRIP_BOND_GL1
3. Si THEORETICAL=YES ET STRIP=NO → retourne "1"
4. Sinon → retourne "0"

**Dépendances:**
- IPreferencesRepository (2 préférences)

**Transformation C#:**
- Utiliser GetPreference(string) du framework
- Retourner string "1" ou "0"
```

### 3.6 Fonctions Génériques du Framework

**⚠️ IMPORTANT:** Certaines fonctions simples sont gérées directement par le framework C# et **n'apparaissent PAS** dans les executers.

#### Fonctions POST (Hidden) - HiddenParametersImplementation.cs

Ces fonctions sont définies dans:
```
repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/HiddenParametersImplementation.cs
```

**Liste des fonctions génériques courantes:**

| Fonction | Retour | Usage |
|----------|--------|-------|
| `CheckTrue` | "1" | Valeur cachée à true |
| `CheckFalse` | "0" | Valeur cachée à false |
| `PureValueZero` | "0" | Valeur hardcodée 0 |
| `PureValueMinusOne` | "-1" | Valeur hardcodée -1 |
| `GetBoolFromPref(PREF_XXX)` | "1"/"0" | Selon préférence YES/NO |

**Implémentation dans Parameters.cs:**

Pour ces fonctions, utiliser `ValidationFunction` + `InitialValue` hardcodé:

```csharp
// Exemple: PARAM_KeepInvalidPeriods avec CheckTrue
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_KeepInvalidPeriods))
{
    WindowOrder = 1,
    Position = 1,
    PositionH = 1,
    ValidationFunction = "CheckTrue",  // ← Fonction générique
    InitialValue = "1"                 // ← Valeur correspondante
});

// Exemple: PARAM_CompareReparNo avec CheckFalse
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_CompareReparNo))
{
    WindowOrder = 1,
    Position = 1,
    PositionH = 1,
    ValidationFunction = "CheckFalse",
    InitialValue = "0"
});
```

**Action requise:** **AUCUNE** - pas besoin de créer ValueProviderParameter pour ces fonctions!

#### Fonctions PRE (Checkbox) - CheckBoxParametersImplementation.cs

**Localisation:**
```
repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/CheckBoxParametersImplementation.cs
```

**Fonctions génériques:**
- `InitCheckTrue` / `CheckTrue` → Coche par défaut
- `InitCheckFalse` / `CheckFalse` → Décoche par défaut

#### Comment identifier une fonction générique?

**Signes qu'une fonction est générique:**

1. ✅ Nom très simple: `CheckTrue`, `CheckFalse`, `GetFirmCurrency`
2. ✅ Utilisée dans PLUSIEURS rapports différents
3. ✅ Logique triviale (retourne juste "0", "1", ou une préférence simple)
4. ✅ Déjà définie dans `HiddenParametersImplementation.cs` ou `CheckBoxParametersImplementation.cs`

**Workflow de vérification:**

```bash
# 1. Chercher dans HiddenParametersImplementation.cs
cd ../monolith/CFF/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes
grep -n "CheckTrue" HiddenParametersImplementation.cs

# 2. Si trouvé → Fonction générique, pas de migration requise
# 3. Si non trouvé → Fonction spécifique, suivre la procédure normale
```

**Exemples concrets:**

| PARAM_NAME | Default_Function | Action requise |
|------------|------------------|----------------|
| PARAM_CheckForClosedAccount | CheckTrue | ❌ Aucune - générique |
| PARAM_CompareReparNo | CheckFalse | ❌ Aucune - générique |
| PARAM_FirmCurrency | GetFirmCurrency | ⚠️ Vérifier si déjà dans executer |
| PARAM_DisplayDate | GetDisplayDate | ✅ Migration requise - fonction complexe |

### 3.7 Déterminer la Complexité Réelle d'une Fonction

**⚠️ IMPORTANT:** Beaucoup de fonctions marquées `UnimplementedParameter()` sont en fait **triviales**!

Ne pas confondre "non implémenté" avec "complexe". Une fonction peut être marquée TODO simplement parce que personne ne l'a encore migrée, pas parce qu'elle est difficile.

#### Checklist Rapide (30 secondes)

**Lire les 10 premières lignes du code C. Cocher ce qui s'applique:**

```
□ La fonction fait juste pAtt->SetValue("valeur_fixe")
□ La fonction appelle une autre fonction Init simple
□ La fonction ne contient que des if/else simples
□ La fonction accède à 1 seule préférence
□ La fonction utilise GetPad() pour 1 seule condition
□ La fonction n'a PAS de boucles (for, while)
□ La fonction n'a PAS de requêtes SQL/BD
□ La fonction n'a PAS de calculs mathématiques complexes
□ La fonction fait < 30 lignes
```

**Résultat:**
- ✅ **7-9 cochés:** Fonction TRIVIALE (< 30min)
- ⚠️ **4-6 cochés:** Fonction SIMPLE (30min - 1h)
- ⚠️ **2-3 cochés:** Fonction MOYENNE (1-2h)
- 🔴 **0-1 coché:** Fonction COMPLEXE (2-4h)

#### Les 5 Niveaux de Complexité

**Niveau 0: Valeur Hardcodée Pure** ⭐ (5-10 minutes)

**Code C typique:**
```c
void C_VALIDATION_HIDED::PerfAccSummGetSubReportField(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_ATTRIBUTE *pAtt = pGroup->GetValue();
    if (pAtt != NULL)
    {
        pAtt->SetValue("PAC_Name,PER_V_Inflow,PEI_V_Symbol,...");
    }
}
```

**Migration:** InitialValue directement dans Parameters.cs ou StringParameter

**Signes distinctifs:**
- Une seule ligne `pAtt->SetValue("...")`
- Aucune logique, aucune condition
- Valeur entre guillemets

---

**Niveau 1: Appel de Fonction Simple** ⭐ (10-30 minutes)

**Code C typique:**
```c
void C_VALIDATION_CHECK::InitSinceInceptionCheck(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;
    C_ATTRIBUTE *pAtt = pGroup->GetValue();

    pGroup->Select(true);  // C'est tout!
}
```

**Migration:** TrueParameter, FalseParameter, ou StringParameter

**Signes distinctifs:**
- Appelle une fonction simple: `Select(true)`, `SetValue("0")`
- Pas de logique conditionnelle
- Fonction wrapper autour d'une valeur statique

---

**Niveau 2: Condition Simple (1 préférence ou 1 pad)** ⭐⭐ (30min - 1h)

**Code C typique:**
```c
void C_VALIDATION_CHECK::InitDefaultIndexCheckTrue(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    const C_REPORT_API *pReportApi = pGroup->GetReportApi();

    if (pReportApi != NULL && pReportApi->GetPad() == REPORT_PORTEF)
    {
        pAtt->SetValue("0");
    }
    else
    {
        pAtt->SetValue("1");
    }
}
```

**Migration:** IValueProvidedParameter avec 1 dépendance (IPreferencesRepository OU SourceTypes)

**Signes distinctifs:**
- Un seul `if/else`
- Condition sur GetPad() OU une préférence
- Deux valeurs possibles

---

**Niveau 3: Conditions Multiples ou Préférences Multiples** ⭐⭐ (1-2h)

**Code C typique:**
```c
void C_VALIDATION_CHECK::InitGainLossCostDisplayed(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    CF_STRING sAddTheoreticalValue = GetCresusConfig()->get("PREF_ADD_THEORETICAL_VALUE");
    CF_STRING sStripBondGl1 = GetCresusConfig()->get("PREF_STRIP_BOND_GL1");

    int iAddTheo = (sAddTheoreticalValue == "YES") ? 1 : 0;
    int iStripBond = (sStripBondGl1 == "YES") ? 1 : 0;

    if (iAddTheo == 1 && iStripBond == 0)
    {
        pAtt->SetValue("1");
    }
    else
    {
        // ... autre logique
    }
}
```

**Migration:** IValueProvidedParameter avec plusieurs dépendances

**Signes distinctifs:**
- Plusieurs GetCresusConfig()->get()
- Logique conditionnelle avec AND/OR
- Comparaisons multiples

---

**Niveau 4: Logique Complexe (Boucles, Calculs, BD)** ⭐⭐⭐ (2-4h+)

**Code C typique:**
```c
void C_VALIDATION_COMBO::InitPeriod(...)
{
    // 50+ lignes
    for (int i = 0; i < count; i++)
    {
        // Boucle sur des données
    }

    // Calculs de dates
    CF_DATE dateMax = CalculateSomething();

    // Appels multiples
    SetWidgetPeriod(pGroup);
    SetRangeForCalendar(dateMin, dateMax);

    // Logique métier complexe
    if (condition1 && condition2)
    {
        // ...
    }
}
```

**Migration:** IValueProvidedParameter avec services multiples + possiblement nouveau service Domain

**Signes distinctifs:**
- Boucles (for, while)
- Calculs mathématiques ou de dates
- Appels à plusieurs helpers
- > 30 lignes de code
- Requêtes BD

#### Decision Tree Visuel

```
Code C++ trouvé
    ↓
Contient pAtt->SetValue("valeur_fixe") UNIQUEMENT ?
    ✅ Oui → NIVEAU 0 (5min) → InitialValue direct
    ❌ Non ↓

Contient pGroup->Select(true/false) UNIQUEMENT ?
    ✅ Oui → NIVEAU 1 (10min) → TrueParameter/FalseParameter
    ❌ Non ↓

Contient UN SEUL if avec GetPad() OU une préférence ?
    ✅ Oui → NIVEAU 2 (30min-1h) → IValueProvidedParameter simple
    ❌ Non ↓

Contient plusieurs préférences OU conditions multiples ?
    ✅ Oui → NIVEAU 3 (1-2h) → IValueProvidedParameter moyen
    ❌ Non ↓

Contient boucles, calculs, ou > 30 lignes ?
    ✅ Oui → NIVEAU 4 (2-4h+) → IValueProvidedParameter complexe + service
```

#### Exemples de "Fausses Complexités"

**Cas réels du rapport PERF_ACC_SUMM:**

| Fonction | Perception | Réalité | Code C |
|----------|------------|---------|--------|
| Period1-5 | ⚠️ UnimplementedParameter → "complexe" | ⭐ Niveau 0 | `pAtt->SetValue("3")` |
| SinceInception | ⚠️ UnimplementedParameter → "complexe" | ⭐ Niveau 1 | `pGroup->Select(true)` |
| PerfAccSummGetSubReportField | 🔴 Nom bizarre → "complexe" | ⭐ Niveau 0 | `pAtt->SetValue("PAC_Name,...")` |
| InitDefaultIndex | ⚠️ UnimplementedParameter | ⭐⭐ Niveau 2 | Un seul if sur GetPad() |

**Leçon:** Ne pas juger la complexité par le status UnimplementedParameter ou le nom de la fonction!

#### Workflow Recommandé

```
1. Voir fonction dans SQL
2. Chercher dans executers C#
   → Existe ET implémenté ? FIN ✅
   → UnimplementedParameter() ? Continuer ↓
3. Chercher code C avec grep
4. Lire 10 premières lignes
5. Appliquer checklist 30 secondes
6. Déterminer niveau 0-4
7. Choisir approche de migration appropriée
```

**Temps gagné:** Identifier rapidement les niveaux 0-1 évite de perdre des heures à analyser du code trivial!

### 3.8 Guide de Lecture du Code C++

**Objectif:** Comprendre rapidement le code C++ **sans être expert en C++**

#### Patterns C++ Courants et Leur Signification

**Pattern 1: Récupération d'attribut**
```c
C_ATTRIBUTE *pAtt = pGroup->GetValue();
if (pAtt == NULL)
{
    return;
}
```
**Signification:** Boilerplate standard - toujours présent, peut être ignoré.
**En C#:** Aucun équivalent - on travaille directement avec `parameter.InitialValue`

---

**Pattern 2: Définir une valeur**
```c
pAtt->SetValue("1");
// OU
pAtt->SetValue(CF_STRING(value));
```
**Signification:** **C'EST LA VALEUR RETOURNÉE PAR LA FONCTION!**
**En C#:** `parameter.InitialValue = "1";`

---

**Pattern 3: Cocher/décocher une checkbox**
```c
pGroup->Select(true);   // Cocher
pGroup->Select(false);  // Décocher
```
**Signification:** Valeur booléenne
**En C#:**
```csharp
parameter.InitialValue = "1";  // true
parameter.InitialValue = "0";  // false
```

---

**Pattern 4: Accès préférence**
```c
CF_STRING sPref = GetCresusConfig()->get("PREF_XXX");
// OU
CF_STRING sPref = GetPreference("PREF_XXX");
```
**Signification:** Lire une préférence de configuration
**En C#:** `_preferencesRepository.GetPreference("PREF_XXX")`

---

**Pattern 5: Comparaison YES/NO**
```c
if (sPref.CompareCaseInsensitive("YES") == 0)
if (sPref == "YES")
```
**Signification:** Tester si préférence = "YES"
**En C#:** `pref?.Value?.ToUpper() == "YES"`

---

**Pattern 6: Source type (Pad)**
```c
eReportPad pad = pReportApi->GetPad();
if (pad == REPORT_CLIENT)
if (pad == REPORT_ACCOUNT)
if (pad == REPORT_PORTEF)   // Portfolio
```
**Signification:** Contexte d'exécution du rapport
**En C#:**
```csharp
if (_requestSourceType == SourceTypes.Client)
if (_requestSourceType == SourceTypes.Account)
if (_requestSourceType == SourceTypes.Portfolio)
```

---

**Pattern 7: Callback handler**
```c
else if (in_sFunction == "FunctionName")
{
    m_pParam->SetInit(C_VALIDATION_XXX::InitFunction);
    m_pParam->SetValue(C_VALIDATION_XXX::SetFunction);
    m_pParam->SetGetValue(C_VALIDATION_XXX::GetFunction);
}
```
**Signification:** La fonction configure des callbacks - il faut chercher CHAQUE callback
**En C#:** Migrer la logique combinée de tous les callbacks

---

**Pattern 8: Helper function**
```c
void InitPeriod1(...)
{
    InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);
}
```
**Signification:** La vraie logique est dans la helper function - il faut la lire aussi
**En C#:** Chercher la helper function plus bas dans le fichier

#### Ce Qu'on Peut Ignorer

**❌ Ces éléments peuvent être sautés lors de la lecture:**

1. **Type casts:**
   ```c
   C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;
   ```
   → Ignore - juste du casting de types

2. **Null checks sur pGroup:**
   ```c
   if (pGroup != NULL)
   {
       // ...
   }
   ```
   → Framework C++ - pas nécessaire en C#

3. **Déclarations de variables simples:**
   ```c
   int nValue = 0;
   bool bFlag = false;
   ```
   → Juste des initialisations

4. **Commentaires en français:**
   ```c
   // Cette méthode permet de...
   ```
   → Lire si besoin de contexte métier

#### Ce Qui Est IMPORTANT

**✅ Ces éléments sont CRITIQUES:**

1. **Tous les appels à SetValue():**
   ```c
   pAtt->SetValue("1");  // ← IMPORTANT!
   ```

2. **Tous les GetCresusConfig()->get():**
   ```c
   GetCresusConfig()->get("PREF_XXX");  // ← IMPORTANT!
   ```

3. **Tous les GetPad():**
   ```c
   pReportApi->GetPad()  // ← IMPORTANT!
   ```

4. **Tous les if/else avec logique métier:**
   ```c
   if (condition_métier)  // ← IMPORTANT!
   {
       pAtt->SetValue("1");
   }
   ```

5. **Appels à d'autres fonctions:**
   ```c
   InitPeriod(pGroup, value, index);  // ← IMPORTANT - chercher cette fonction!
   ```

#### Technique de "Scanning" Rapide

**Étape 1: Scan visuel (10 secondes)**

Regarder le code en diagonale et chercher visuellement:
- Mot-clé `SetValue`
- Mot-clé `GetCresusConfig`
- Mot-clé `GetPad`
- Mot-clé `if`

**Étape 2: Compter (5 secondes)**

Compter mentalement:
- Combien de SetValue? (1 = simple, 2+ = conditions)
- Combien de GetCresusConfig? (0 = statique, 1 = simple, 2+ = moyen)
- Combien de if? (0-1 = simple, 2+ = moyen)

**Étape 3: Lire sélectivement (30-60 secondes)**

Lire UNIQUEMENT:
- Les lignes avec SetValue
- Les conditions des if
- Les valeurs entre guillemets

**Exemple pratique:**

```c
void C_VALIDATION_CHECK::InitSomething(C_WINDOW_PARAM_GROUP *in_pGroup)  // ← Ignorer
{
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;  // ← Ignorer

    C_ATTRIBUTE *pAtt = pGroup->GetValue();  // ← Ignorer
    if ( pAtt == NULL )  // ← Ignorer
    {
        return;
    }

    CF_STRING sPref = GetCresusConfig()->get("PREF_DISPLAY_CHECK_DIGIT");  // ← LIRE!

    if (sPref == "YES")  // ← LIRE!
    {
        pAtt->SetValue("1");  // ← LIRE!
    }
    else
    {
        pAtt->SetValue("0");  // ← LIRE!
    }
}
```

**Résultat du scan:**
- 1 GetCresusConfig → Préférence simple
- 2 SetValue dans if/else → Condition simple
- **Niveau 2: 30min-1h**

#### Commandes Bash Utiles pour Analyser

**Trouver toutes les fonctions d'un fichier:**
```bash
grep -n "^void C_VALIDATION" validation_check.c
```

**Compter les SetValue dans une fonction:**
```bash
sed -n '789,850p' validation_check.c | grep -c "SetValue"
```

**Extraire juste les valeurs SetValue:**
```bash
sed -n '789,850p' validation_check.c | grep "SetValue" | sed 's/.*SetValue(\(.*\)).*/\1/'
```

**Trouver toutes les préférences utilisées:**
```bash
grep -o 'PREF_[A-Z_]*' validation_check.c | sort -u
```

---

## Étape 4: Implémentation C#

### 4.1 Choix du type d'implémentation

**Option A: ValueProviderParameter (Recommandé)**

Pour fonctions spécifiques ou complexes.

**Localisation:**
```
ReportManagerAPI.Infrastructure/
└── Repositories/
    └── ValueProviderFunctions/
        └── Parameters/
            ├── [FunctionName]Parameter.cs
            ├── Hidden/                 # Paramètres cachés (POST)
            └── Date/                   # Paramètres de date
```

**Template (utiliser snippet `ivalueProvidedParameter`):**

```csharp
using ReportManagerAPI.Domain.Repositories;
using ReportManagerAPI.Domain.Models;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters
{
    public class FunctionNameParameter : IValueProvidedParameter
    {
        private readonly IPreferencesRepository _preferencesRepository;
        // Autres dépendances...

        public FunctionNameParameter(IPreferencesRepository preferencesRepository)
        {
            _preferencesRepository = preferencesRepository;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            // Implémentation de la logique C++

            parameter.InitialValue = "valeur";
            parameter.VisibleOnUi = true; // si applicable

            return parameter;
        }
    }
}
```

**Option B: Modification dans SpecificTypes/*ParametersImplementation.cs**

Pour fonctions génériques simples réutilisables.

**Localisation:**
```
repos/ReportFoundations/ReportImplementations/
└── Implementations/
    └── Parameters/
        └── SpecificTypes/
            ├── CheckBoxParametersImplementation.cs
            ├── ComboBoxParametersImplementation.cs
            ├── RadioParametersImplementation.cs
            ├── DateParametersImplementation.cs
            └── HiddenParametersImplementation.cs
```

### 4.1.1 Helper Parameters Réutilisables

**⚠️ IMPORTANT:** Pour les cas simples, utilisez ces classes préfabriquées au lieu de créer de nouveaux Parameters!

**Localisation:** `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/String/`

| Classe | Usage | Code | Cas d'usage |
|--------|-------|------|-------------|
| `StringParameter` | Valeur hardcodée | `new StringParameter("3")` | Valeur statique quelconque |
| `TrueParameter` | Valeur "1" (true) | `new TrueParameter()` | Checkbox cochée, boolean true |
| `FalseParameter` | Valeur "0" (false) | `new FalseParameter()` | Checkbox décochée, boolean false |
| `EmptyParameter` | Valeur "" (vide) | `new EmptyParameter()` | Champ vide |
| `VoidParameter` | Ne fait rien | `new VoidParameter()` | Placeholder, no-op |

**Enregistrement:**
```csharp
implementationsDictionary["Period1"] = () => new StringParameter("3");
implementationsDictionary["PerfCurrencyRadio"] = () => new TrueParameter();
implementationsDictionary["DisplayAscCode"] = () => new FalseParameter();
implementationsDictionary["GraphNegativePieWarningRemoval"] = () => new VoidParameter();
```

**Quand les utiliser:**
- ✅ Fonction C++ retourne valeur hardcodée: `pAtt->SetValue("3")` → `StringParameter("3")`
- ✅ Checkbox toujours cochée: `pGroup->Select(true)` → `TrueParameter()`
- ✅ Pas de logique conditionnelle

**Ne PAS créer** de nouvelle classe Parameter pour ces cas triviaux!

**Exemples réels dans les executers:**
- PreParamEntry lignes 49, 66, 88, 92: `StringParameter` pour valeurs hardcodées
- PreParamEntry ligne 60: `FalseParameter` pour GraphicIncluded
- PreParamEntry ligne 67: `VoidParameter` pour GraphNegativePieWarningRemoval

---

### 4.2 Patterns d'implémentation courants

#### Pattern 1: Préférence simple

**C++:**
```cpp
if (GetPreference("PREF_ENABLE_CLIENT_GROUPING") == "YES")
    return "Y";
return "N";
```

**C#:**
```csharp
var preference = _preferencesRepository.GetPreference("PREF_ENABLE_CLIENT_GROUPING");

if (preference == null)
    throw new Exception($"Preference PREF_ENABLE_CLIENT_GROUPING not found");

parameter.InitialValue = preference.Value == "YES" ? "Y" : "N";
return parameter;
```

#### Pattern 2: Préférences multiples

**C++:**
```cpp
int addTheo = GetPreference("PREF_ADD_THEORETICAL_VALUE") == "YES" ? 1 : 0;
int stripBond = GetPreference("PREF_STRIP_BOND_GL1") == "YES" ? 1 : 0;

if (addTheo == 1 && stripBond == 0)
    return "1";
return "0";
```

**C#:**
```csharp
var preferences = _preferencesRepository.GetPreferencesValue(new List<string>
{
    "PREF_ADD_THEORETICAL_VALUE",
    "PREF_STRIP_BOND_GL1"
}).Result;

var addTheoPref = preferences.FirstOrDefault(x => x.Name == "PREF_ADD_THEORETICAL_VALUE");
var stripBondPref = preferences.FirstOrDefault(x => x.Name == "PREF_STRIP_BOND_GL1");

int addTheo = addTheoPref?.Value?.ToUpper() == "YES" ? 1 : 0;
int stripBond = stripBondPref?.Value?.ToUpper() == "YES" ? 1 : 0;

parameter.InitialValue = (addTheo == 1 && stripBond == 0) ? "1" : "0";
return parameter;
```

**⚠️ IMPORTANT - Choix de la méthode:**

**Règle:**
- ✅ **1 préférence** → `GetPreference(string)` (recommandé depuis PR #5972)
- ✅ **2+ préférences** → `GetPreferencesValue(List<string>)`

**Ancien code (à NE PAS copier):**
```csharp
// FirmCurrencyParameter.cs:27 - OBSOLÈTE pour UNE préférence
var listPref = new List<string>() { "DEVISE.DEVISE_SYS" };
var returnedPreference = preferencesRepository.GetPreferencesValue(listPref).Result.FirstOrDefault();
```

**Nouveau code (recommandé):**
```csharp
// InitDisplayCheckDigitParameter.cs:28 - CORRECT pour UNE préférence
var preference = _preferencesRepository.GetPreference(PreferenceKey);
```

**Note:** Certains parameters migrés utilisent encore l'ancien pattern. Lors de la migration, utilisez TOUJOURS le pattern recommandé même si le code existant fait autrement.

#### Pattern 3: Accès paramètre du rapport

**C++:**
```cpp
string paramValue = GetParam("PARAM_GainLossCostDisplayed");
```

**C#:**
```csharp
var paramValue = reportMetaDataFromRtm.Parameters
    .FirstOrDefault(p => p.Name == "PARAM_GainLossCostDisplayed")?.InitialValue;
```

#### Pattern 4: Source type (Pad)

**C++:**
```cpp
eReportPad pad = GetPad();
if (pad == REPORT_CLIENT)
    return "Y";
```

**C#:**
```csharp
private readonly SourceTypes _requestSourceType;

// Dans le constructeur
public FunctionNameParameter(SourceTypes requestSourceType)
{
    _requestSourceType = requestSourceType;
}

// Dans ProvideValue
if (_requestSourceType == SourceTypes.Client)
{
    parameter.InitialValue = "Y";
}
```

**Helper:** Utiliser `PadValueExtractor.GetPadStringValueFromSourceType(_requestSourceType)`

#### Pattern 5: Valeur conditionnelle avec visibilité

**C++:**
```cpp
if (HasPreference("PREF_DISPLAY_CHECK_DIGIT") &&
    (pad == ACCOUNT || pad == CLIENT))
{
    SetVisible(true);
    return "1";
}
```

**C#:**
```csharp
var preference = _preferencesRepository.GetPreference("PREF_DISPLAY_CHECK_DIGIT");

parameter.InitialValue = "0";
parameter.VisibleOnUi = false;

if (preference?.Value == "YES" &&
    (_requestSourceType == SourceTypes.Account ||
     _requestSourceType == SourceTypes.Client))
{
    parameter.VisibleOnUi = true;
    parameter.InitialValue = "1";
}

return parameter;
```

#### Pattern 6: GetBoolFromPref dans le SQL

**⚠️ NOUVEAU PATTERN:** Certaines fonctions dans le SQL contiennent directement la préférence en paramètre.

**SQL:**
```csv
Default_Function: GetBoolFromPref(PREF_DISPLAY_ASC_CODE)
Default_Function: GetBoolFromPrefUserAccess(PREF_DISPLAY_ASC_CODE)
```

**Extraction:**
- Nom de la fonction: `GetBoolFromPref` ou `GetBoolFromPrefUserAccess`
- Nom de la préférence: **Entre parenthèses** (ex: `PREF_DISPLAY_ASC_CODE`)
- Pattern regex: `GetBoolFromPref(?:UserAccess)?\((PREF_[A-Z_]+)\)`

**Étapes de migration:**

1. **Extraire le nom de la préférence du SQL:**
   ```csv
   GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
   → Préférence: PREF_REPORT_HIDE_CURRENCY
   ```

2. **Rechercher dans le code C:**
   ```bash
   cd repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam
   grep -n "PREF_REPORT_HIDE_CURRENCY" validation_hided.c
   ```

3. **Code C typique:**
   ```c
   void C_VALIDATION_HIDED::SomeFunctionName(C_WINDOW_PARAM_GROUP *in_pGroup)
   {
       C_ATTRIBUTE *pAtt = in_pGroup->GetValue();
       if (pAtt != NULL)
       {
           CF_STRING sPref = GetCresusConfig()->get("PREF_REPORT_HIDE_CURRENCY");
           bool bValue = (sPref.CompareCaseInsensitive("YES") == 0);
           pAtt->SetValue(bValue ? "1" : "0");
       }
   }
   ```

4. **Migration C#:**

**Option A: ValueProviderParameter (si logique complexe)**

```csharp
using ReportManagerAPI.Domain.Repositories;
using ReportManagerAPI.Domain.Models;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters.Hidden
{
    public class GetBoolFromPrefReportHideCurrencyParameter : IValueProvidedParameter
    {
        private readonly IPreferencesRepository _preferencesRepository;

        public GetBoolFromPrefReportHideCurrencyParameter(IPreferencesRepository preferencesRepository)
        {
            _preferencesRepository = preferencesRepository;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            var preference = _preferencesRepository.GetPreference("PREF_REPORT_HIDE_CURRENCY");
            parameter.InitialValue = preference?.Value?.ToUpper() == "YES" ? "1" : "0";
            return parameter;
        }
    }
}
```

**Option B: Fonction générique dans HiddenParametersImplementation.cs (si simple)**

Si la logique est identique pour toutes les préférences, ajouter dans `HiddenParametersImplementation.cs`:

```csharp
this.AddData(new ParameterEntity(
    Params.PARAM_HideTitleCurrency,
    "",
    "",
    "GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)",
    WidgetTypes.Hidden,
    "",
    initialValueFromPref: "PREF_REPORT_HIDE_CURRENCY"));
```

**Enregistrement dans l'executer:**

```csharp
implementationsDictionary["GetBoolFromPrefReportHideCurrency"] =
    () => new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
```

**Nom de la classe Parameter:**
- Format: `GetBoolFromPref{PreferenceName}Parameter`
- Exemple: `PREF_REPORT_HIDE_CURRENCY` → `GetBoolFromPrefReportHideCurrencyParameter`
- Conversion: Enlever `PREF_`, convertir en PascalCase

**Tests unitaires:**

```csharp
[Theory]
[InlineData("YES", "1")]
[InlineData("NO", "0")]
[InlineData(null, "0")]
public void GivenPreferenceValue_WhenProvideValueCalled_ThenReturnsExpectedValue(
    string prefValue, string expectedResult)
{
    // Arrange
    var preferencesRepositoryMock = Mock.Get(preferencesRepository);
    preferencesRepositoryMock
        .Setup(x => x.GetPreference("PREF_REPORT_HIDE_CURRENCY"))
        .Returns(prefValue == null ? null : new Preference
        {
            Name = "PREF_REPORT_HIDE_CURRENCY",
            Value = prefValue
        });

    var parameter = new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
    var reportParameterMetaData = new ReportParameterMetaData();
    var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

    // Act
    var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

    // Assert
    result.InitialValue.Should().Be(expectedResult);
}
```

### 4.3 Mise à jour de Parameters.cs

**Localisation:** `repos/ReportFoundations/ReportImplementations/Implementations/Reports/[Category]/[ReportName]/Parameters.cs`

**Pour chaque paramètre migré:**

```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_GainLossCostDisplayed))
{
    WindowOrder = 3,
    Position = 2,
    PositionH = 1,
    ValidationFunction = "",
    ValueProviderFunction = "InitGainLossCostDisplayed"  // ← AJOUTER CETTE LIGNE
});
```

**Notes importantes:**
- `ValueProviderFunction` = nom de la fonction (pas le nom de la classe Parameter)
- Pour fonctions génériques déjà dans Implementation files, peut être omis (commentaire explicatif recommandé)
- Pour TODOs, ajouter commentaire: `// ValueProviderFunction (FunctionName) set in HiddenParametersImplementation`

### 4.4 ValidationFunction vs ValueProviderFunction

**⚠️ IMPORTANT:** Il existe DEUX façons de définir la logique d'un paramètre dans Parameters.cs.

#### Approche 1: ValidationFunction + InitialValue hardcodé

**Quand l'utiliser:**
- Fonctions **génériques simples** (CheckTrue, CheckFalse, etc.)
- Valeur **statique** connue à l'avance
- Fonction déjà définie dans `HiddenParametersImplementation.cs` ou `CheckBoxParametersImplementation.cs`

**Exemple:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_KeepInvalidPeriods))
{
    WindowOrder = 1,
    Position = 1,
    PositionH = 1,
    ValidationFunction = "CheckTrue",  // ← Nom de la fonction générique
    InitialValue = "1"                 // ← Valeur hardcodée
});
```

**Caractéristiques:**
- ✅ Pas besoin de créer ValueProviderParameter
- ✅ Pas besoin d'enregistrement dans executer
- ✅ Valeur définie directement dans Parameters.cs
- ⚠️ Valeur STATIQUE - ne change pas selon le contexte

#### Approche 2: ValueProviderFunction (dynamique)

**Quand l'utiliser:**
- Fonctions **spécifiques** au rapport
- Logique **complexe** avec dépendances (repositories, services)
- Valeur **dynamique** qui dépend du contexte (préférences, pad, paramètres, etc.)
- Fonction enregistrée dans `Pre|PostParamEntryValueProviderFunctionsExecuter.cs`

**Exemple:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_DisplayPerfStartDate))
{
    WindowOrder = 1,
    Position = 1,
    PositionH = 1,
    ValidationFunction = "GetDateOneYearBefPerfEndDate",     // ← Optionnel
    ValueProviderFunction = "GetDateOneYearBefPerfEndDate"  // ← Fonction dynamique
});
```

**Caractéristiques:**
- ✅ Valeur calculée à l'exécution
- ✅ Accès aux repositories et services
- ✅ Logique complexe et conditionnelle
- ⚠️ Requiert implémentation IValueProvidedParameter
- ⚠️ Requiert enregistrement dans executer

#### Approche 3: Mixte (ValidationFunction + ValueProviderFunction)

**Quand l'utiliser:**
- Fonction avec logique complexe qui a **aussi** une valeur initiale hardcodée
- La ValidationFunction définit une valeur par défaut
- La ValueProviderFunction peut la modifier dynamiquement

**Exemple:**
```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_DataEntryPoint))
{
    WindowOrder = 1,
    Position = 1,
    PositionH = 1,
    ValidationFunction = "PerfAccSummDataEntryPoint",
    InitialValue = "PAC_Name|PEI_V_Symbol|...",  // ← Valeur par défaut
    // Mais peut être modifiée par logique runtime si ValueProviderFunction existait
});
```

#### Tableau de décision

| Critère | ValidationFunction | ValueProviderFunction |
|---------|-------------------|---------------------|
| Valeur statique ("0", "1", "-1") | ✅ Oui | ❌ Non |
| Fonction générique (CheckTrue, CheckFalse) | ✅ Oui | ❌ Non |
| Dépend de préférence simple | ✅ Possible | ✅ Recommandé |
| Dépend de préférences multiples | ❌ Non | ✅ Oui |
| Dépend du pad/source type | ❌ Non | ✅ Oui |
| Dépend d'autres paramètres | ❌ Non | ✅ Oui |
| Logique conditionnelle complexe | ❌ Non | ✅ Oui |
| Accès BD / repository | ❌ Non | ✅ Oui |
| Calculs de dates | ❌ Non | ✅ Oui |

#### Exemples concrets

**Cas 1: Simple static value**
```csharp
// SQL: Default_Function = CheckTrue
// Solution: ValidationFunction SEULEMENT
ValidationFunction = "CheckTrue",
InitialValue = "1"
// Pas de ValueProviderFunction
```

**Cas 2: Simple preference**
```csharp
// SQL: Default_Function = GetBoolFromPref(PREF_XXX)
// Solution: SOIT ValidationFunction (si générique dans HiddenParametersImplementation.cs)
ValidationFunction = "GetBoolFromPref(PREF_XXX)",
// OU ValueProviderFunction (si logique spécifique)
ValueProviderFunction = "GetBoolFromPrefXXX"
```

**Cas 3: Complex logic**
```csharp
// SQL: Specific_Function = PerfAccSummDataEntryPoint
// Solution: ValueProviderFunction OBLIGATOIRE
ValidationFunction = "PerfAccSummDataEntryPoint",  // Optionnel
ValueProviderFunction = "PerfAccSummDataEntryPoint",  // Obligatoire - enregistré dans executer
InitialValue = "default_value"  // Optionnel - valeur par défaut
```

**Cas 4: Date calculation**
```csharp
// SQL: Specific_Function = GetDateOneYearBefPerfEndDate
// Solution: ValueProviderFunction car calcul dynamique
ValueProviderFunction = "GetDateOneYearBefPerfEndDate"
// Valeur calculée par le parameter, pas de InitialValue hardcodé
```

#### Workflow de décision

```
Fonction du SQL
    ↓
Est-ce CheckTrue/CheckFalse/PureValueZero ?
    ✅ Oui → ValidationFunction + InitialValue
    ❌ Non ↓

Est-ce dans HiddenParametersImplementation.cs ?
    ✅ Oui → ValidationFunction (vérifier si InitialValue requis)
    ❌ Non ↓

Dépend de contexte runtime (pref, pad, params) ?
    ✅ Oui → ValueProviderFunction (créer Parameter)
    ❌ Non ↓

Valeur statique simple ?
    ✅ Oui → InitialValue hardcodé sans function
    ❌ Non → ValueProviderFunction (logique custom)
```

---

## Étape 5: Enregistrement

### 5.1 Enregistrer dans l'executer

**Fichier:**
- PRE: `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs`
- POST: `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PostParamEntryValueProviderFunctionsExecuter.cs`

**Méthode:** `InitializeValueProviderFunctionImplementations`

**Ordre alphabétique strict:**

```csharp
protected override void InitializeValueProviderFunctionImplementations(
    Dictionary<string, Func<IValueProvidedParameter>> implementationsDictionary)
{
    // ... existing entries ...

    implementationsDictionary["FunctionName"] =
        () => new FunctionNameParameter(preferencesRepository, requestSourceType);

    // ... more entries (alphabetical) ...
}
```

**Important:**
- Respecter l'ordre alphabétique strict
- Passer toutes les dépendances requises (disponibles via DI dans la classe)
- Si temporairement non implémenté: `() => new UnimplementedParameter() // TODO`

### 5.2 Injection de dépendances

Si un nouveau repository est requis, l'ajouter au constructeur:

```csharp
public PostParamEntryValueProviderFunctionsExecuter(
    IPreferencesRepository preferencesRepository,
    IReportCommandAndQueryContextRepository reportCommandAndQueryContextRepository,
    IIndustryCodeRepository industryCodeRepository, // ← Nouveau
    // ... autres dépendances
) : base()
{
    // Assignments...
}
```

---

## Étape 6: Tests

### 6.1 Structure des tests

**Localisation:**
```
ReportManagerAPI.Infrastructure.SmallTests/
└── Repositories/
    └── ValueProviderFunctions/
        └── Parameters/
            ├── [FunctionName]ParameterTests.cs
            ├── Hidden/
            └── Date/
```

### 6.2 Template de test

```csharp
using FluentAssertions;
using Moq;
using ReportManagerAPI.Domain.Repositories;
using ReportManagerAPI.Domain.Models;
using Xunit;

namespace ReportManagerAPI.Infrastructure.SmallTests.Repositories.ValueProviderFunctions.Parameters
{
    public class FunctionNameParameterTests
    {
        private readonly IPreferencesRepository preferencesRepository;

        public FunctionNameParameterTests()
        {
            preferencesRepository = Mock.Of<IPreferencesRepository>();
        }

        [Fact]
        public void GivenCondition_WhenProvideValueCalled_ThenExpectedResult()
        {
            // Arrange
            var preferencesRepositoryMock = Mock.Get(preferencesRepository);
            preferencesRepositoryMock
                .Setup(x => x.GetPreference("PREF_XXX"))
                .Returns(new Preference { Name = "PREF_XXX", Value = "YES" });

            var parameter = new FunctionNameParameter(preferencesRepository);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act
            var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

            // Assert
            result.Should().NotBeNull();
            result.InitialValue.Should().Be("Y");
            preferencesRepositoryMock.Verify(
                x => x.GetPreference("PREF_XXX"),
                Times.Once);
        }

        [Fact]
        public void GivenPreferenceNotFound_WhenProvideValueCalled_ThenThrowsException()
        {
            // Arrange
            var preferencesRepositoryMock = Mock.Get(preferencesRepository);
            preferencesRepositoryMock
                .Setup(x => x.GetPreference(It.IsAny<string>()))
                .Returns(null as Preference);

            var parameter = new FunctionNameParameter(preferencesRepository);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act & Assert
            Assert.Throws<Exception>(() =>
                parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm));
        }
    }
}
```

### 6.3 Scénarios de tests minimaux

Pour chaque ValueProviderParameter, tester:

1. **Cas nominal** - Valeurs correctes retournées
2. **Préférence/paramètre non trouvé** - Exception levée
3. **Valeurs limites** - YES/NO, 0/1, null, etc.
4. **Dépendances multiples** - Combinaisons de préférences
5. **Visibilité UI** - Si `VisibleOnUi` est modifié

### 6.4 Exécution des tests

```bash
cd ../monolith/CFF/Products/ReportManagerApi

# Run all tests
dotnet test

# Run specific test class
dotnet test --filter "FullyQualifiedName~FunctionNameParameterTests"

# Run with coverage
./show-code-coverage.cmd
```

---

## Patterns et transformations

### Tableau de correspondance C++ → C#

| C++ | C# | Notes |
|-----|-----|-------|
| `GetPreference("PREF_XXX")` | `_preferencesRepository.GetPreference("PREF_XXX")` | Framework simplifié |
| `GetParam("PARAM_XXX")` | `reportMetaDataFromRtm.Parameters.FirstOrDefault(p => p.Name == "PARAM_XXX")` | |
| `GetPad()` | `_requestSourceType` (injection) | Enum `SourceTypes` |
| `"YES"` / `"NO"` | Dépend du contexte | Parfois → `"Y"/"N"`, parfois → `"1"/"0"` |
| `TRUE` / `FALSE` | `"Y"` / `"N"` ou `"1"` / `"0"` | Cohérence avec legacy |
| `SetVisible(true)` | `parameter.VisibleOnUi = true` | |
| `SetInitialValue(val)` | `parameter.InitialValue = val` | |
| Classes C++ customs | Services C# dans Domain | Ex: DateTimeService |

### Anti-patterns à éviter

❌ **NE PAS:**
- Utiliser `GetPreferencesValue(List<string>)` pour une seule préférence
- Oublier la validation null sur les préférences
- Hardcoder des valeurs magiques sans constantes
- Copier-coller sans comprendre la logique
- Mélanger logique métier et accès données dans Parameter
- Oublier les tests

✅ **FAIRE:**
- Utiliser `GetPreference(string)` pour préférence unique
- Lever exception explicite si préférence manquante
- Définir constantes: `private const string PreferenceKey = "PREF_XXX"`
- Documenter la logique C++ source en commentaire
- Séparer dans services Domain si logique complexe
- Écrire tests avant implémentation (TDD)

---

## Exemples Complets de Migration

Cette section présente **4 migrations complètes** du début à la fin, couvrant tous les niveaux de complexité.

### Exemple 1: Cas Trivial - SinceInception (⭐ Niveau 1 - 10 minutes)

#### 1.1 Données du SQL

```csv
PARAM_NAME: PARAM_PerfSinceInception
Default_Function: SinceInception
Specific_Function: (vide)
PARAMETER_IMPL_FILE: CheckBoxParametersImplementation.cs
PARAMETER_ENTRY_TYPE: PRE
WIDGET_TYPE: 3 (Checkbox)
```

#### 1.2 Vérification dans les Executers C#

```bash
cd ../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure
grep -n "SinceInception" Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs
```

**Résultat:**
```csharp
implementationsDictionary["SinceInception"] = () => new UnimplementedParameter();
```

**Status:** ⚠️ UnimplementedParameter → Migration requise

#### 1.3 Localisation du Code C++

```bash
cd ../monolith/PM/Products/CroesusServer
grep -n "SinceInception" Src/ReportApi/ReportCtr/ReportCtrParam/validation_check.c
```

**Résultat:** Ligne 154 et ligne 644

```bash
sed -n '644,660p' Src/ReportApi/ReportCtr/ReportCtrParam/validation_check.c
```

#### 1.4 Code C++ Source

```c
//------------------------------------------------------------------------
// C_VALIDATION_CHECK::InitSinceInceptionCheck
//------------------------------------------------------------------------
// Description:
//		Cette fonction permet d'initialiser le parametre PARAM_PerfSinceInception.
//------------------------------------------------------------------------
void C_VALIDATION_CHECK::InitSinceInceptionCheck(C_WINDOW_PARAM_GROUP *in_pGroup)
{
	C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;

	C_ATTRIBUTE *pAtt = pGroup->GetValue();
	if ( pAtt == NULL )
	{
		return;
	}

	pGroup->Select(true);  // ← SEULE LIGNE IMPORTANTE!
}
```

#### 1.5 Analyse de Complexité

**Checklist 30 secondes:**
- ✅ Fonction < 30 lignes
- ✅ Aucune boucle
- ✅ Aucune requête BD
- ✅ Aucun calcul
- ✅ Une seule action: `Select(true)`
- ✅ Aucune préférence
- ✅ Aucun GetPad()

**Résultat:** ✅ **Niveau 1 - Trivial** (10 minutes)

**Code significatif:**
```c
pGroup->Select(true);  // Coche la checkbox
```

**Équivalent C#:**
```csharp
parameter.InitialValue = "1";  // true → "1"
```

#### 1.6 Implémentation C#

**Option choisie:** TrueParameter (déjà existant dans le framework)

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs:
implementationsDictionary["SinceInception"] = () => new TrueParameter();
```

**Alternative:**
```csharp
implementationsDictionary["SinceInception"] = () => new StringParameter("1");
```

#### 1.7 Tests

```csharp
// Test déjà existant pour TrueParameter - aucun test additionnel requis
// OU si StringParameter:
[Fact]
public void SinceInception_WhenCalled_ReturnsOne()
{
    var parameter = new StringParameter("1");
    var metadata = new ReportParameterMetaData();
    var reportMetadata = new ReportMetaDataFromRtm();

    var result = parameter.ProvideValue(metadata, reportMetadata);

    result.InitialValue.Should().Be("1");
}
```

#### 1.8 Temps Réel

- Localisation code C++: 2 minutes
- Analyse: 1 minute
- Implémentation: 2 minutes
- **Total: 5 minutes** ✅

---

### Exemple 2: Cas Simple - InitDefaultIndex (⭐⭐ Niveau 2 - 1 heure)

#### 2.1 Données du SQL

```csv
PARAM_NAME: PARAM_DefaultIndices
Default_Function: InitDefaultIndex
Specific_Function: (vide)
PARAMETER_IMPL_FILE: CheckBoxParametersImplementation.cs
PARAMETER_ENTRY_TYPE: PRE
WIDGET_TYPE: 3 (Checkbox)
```

#### 2.2 Vérification dans les Executers

```bash
grep -n "InitDefaultIndex" PreParamEntryValueProviderFunctionsExecuter.cs
```

**Résultat:**
```csharp
implementationsDictionary["InitDefaultIndex"] = () => new UnimplementedParameter();
```

**Status:** ⚠️ Migration requise

#### 2.3 Code C++ Source (validation_check.c:789)

```c
void C_VALIDATION_CHECK::InitDefaultIndexCheckTrue(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *)in_pGroup;

    if (pGroup != NULL)
    {
        C_ATTRIBUTE *pAtt = pGroup->GetValue();
        const C_REPORT_API *pReportApi = pGroup->GetReportApi();

        if (pReportApi != NULL && pReportApi->GetPad() == REPORT_PORTEF)
        {
            // Si contexte Portfolio: décocher et désactiver
            pGroup->Select(false);
            pGroup->Enable(false);
            pAtt->SetValue("0");
        }
        else
        {
            // Sinon: cocher par défaut
            pGroup->Select(true);
            pAtt->SetValue("1");
        }
    }
}
```

#### 2.4 Analyse

**Checklist:**
- ✅ < 30 lignes
- ✅ Un seul if/else
- ✅ GetPad() présent
- ✅ Deux SetValue (condition binaire)
- ✅ Aucune boucle, aucun calcul

**Résultat:** ⭐⭐ **Niveau 2 - Simple** (30min-1h)

**Logique:**
```
SI source_type == Portfolio
  ALORS valeur = "0" ET désactivé
  SINON valeur = "1"
```

**Dépendances identifiées:**
- `GetPad()` → `SourceTypes` (injection constructor)

#### 2.5 Implémentation C#

**Fichier:** `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/InitDefaultIndexParameter.cs`

```csharp
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Models.ReportGeneration.IncomingGenerationRequest;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters
{
    /// <summary>
    /// Initialise PARAM_DefaultIndices selon le source type.
    /// Si Portfolio: décoche et désactive, sinon: coche.
    ///
    /// Migré depuis: validation_check.c:789 - InitDefaultIndexCheckTrue
    /// </summary>
    public class InitDefaultIndexParameter : IValueProvidedParameter
    {
        private readonly SourceTypes _requestSourceType;

        public InitDefaultIndexParameter(SourceTypes requestSourceType)
        {
            _requestSourceType = requestSourceType;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            if (_requestSourceType == SourceTypes.Portfolio)
            {
                parameter.InitialValue = "0";
                parameter.EnabledOnUi = false;  // Désactivé dans l'UI
            }
            else
            {
                parameter.InitialValue = "1";
                parameter.EnabledOnUi = true;
            }

            return parameter;
        }
    }
}
```

#### 2.6 Enregistrement

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs:
implementationsDictionary["InitDefaultIndex"] =
    () => new InitDefaultIndexParameter(reportCommandAndQueryContextRepository.RequestSourceType);
```

#### 2.7 Tests

**Fichier:** `ReportManagerAPI.Infrastructure.SmallTests/.../Parameters/InitDefaultIndexParameterTests.cs`

```csharp
using FluentAssertions;
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Models.ReportGeneration.IncomingGenerationRequest;
using ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters;
using Xunit;

namespace ReportManagerAPI.Infrastructure.SmallTests.Repositories.ValueProviderFunctions.Parameters
{
    public class InitDefaultIndexParameterTests
    {
        [Theory]
        [InlineData(SourceTypes.Portfolio, "0", false)]
        [InlineData(SourceTypes.Account, "1", true)]
        [InlineData(SourceTypes.Client, "1", true)]
        [InlineData(SourceTypes.Relationship, "1", true)]
        public void GivenSourceType_WhenProvideValue_ThenReturnsExpectedValue(
            SourceTypes sourceType,
            string expectedValue,
            bool expectedEnabled)
        {
            // Arrange
            var parameter = new InitDefaultIndexParameter(sourceType);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act
            var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

            // Assert
            result.InitialValue.Should().Be(expectedValue);
            result.EnabledOnUi.Should().Be(expectedEnabled);
        }
    }
}
```

#### 2.8 Validation

```bash
cd ../monolith/CFF/Products/ReportManagerApi
dotnet test --filter "FullyQualifiedName~InitDefaultIndexParameterTests"
```

**Résultat attendu:** ✅ 4 tests passed

#### 2.9 Temps Réel

- Localisation code C++: 5 minutes
- Analyse: 5 minutes
- Création fichier Parameter: 15 minutes
- Enregistrement: 2 minutes
- Tests unitaires: 20 minutes
- Validation: 5 minutes
- **Total: 52 minutes** ✅

---

### Exemple 3: Cas Moyen - Period1 (⭐⭐ Niveau 2-3 - 30 minutes)

#### 3.1 Données du SQL

```csv
PARAM_NAME: PARAM_PerformanceGroup1
Default_Function: Period1
Specific_Function: (vide)
PARAMETER_IMPL_FILE: ComboBoxParametersImplementation.cs
PARAMETER_ENTRY_TYPE: PRE
WIDGET_TYPE: 1 (Combobox)
```

#### 3.2 Code C++ Source (validation_combo.c:1020)

```c
void C_VALIDATION_COMBO::InitPeriod1(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_WINDOW_PARAM_GROUP_COMBO *pGroup = (C_WINDOW_PARAM_GROUP_COMBO *)in_pGroup;

    InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);
}
```

**⚠️ Attention:** La fonction appelle une helper function `InitPeriod`.

#### 3.3 Lecture de la Helper Function (ligne 1543)

```c
void C_VALIDATION_COMBO::InitPeriod(
    C_WINDOW_PARAM_GROUP_COMBO *in_pGroup,
    int in_nCumulPeriodDefault,
    int in_nFixedPeriodDefault)
{
    if (in_pGroup != NULL)
    {
        if (!in_pGroup->IsInit())
        {
            SetWidgetPeriod(in_pGroup);  // Configure les choix du combobox
        }

        CF_DATE dateMaxDate = *sys_date_fin;
        CF_DATE dateMinDate = GetFirmStartDate();

        in_pGroup->SetRangeForCalendarScreen(dateMinDate, dateMaxDate);

        // ... 30 lignes de configuration UI ...

        if (in_pGroup->GetActiveList() == PERIOD_TYPE_CUMULATIVE_LIST)
        {
            in_pGroup->Select(in_nCumulPeriodDefault);  // ← Sélectionne l'index
        }
        else
        {
            in_pGroup->Select(in_nFixedPeriodDefault);
        }
    }
}
```

#### 3.4 Analyse Approfondie

**Question:** Quelle est la vraie valeur retournée?

**Observation:**
- `GetPeriodNotFixed("3")` retourne un **index** dans une liste
- `InitPeriod1` appelle `InitPeriod(pGroup, GetPeriodNotFixed("3"), 0)`
- Le "3" est l'argument, pas nécessairement la valeur finale

**Investigation supplémentaire:**

```bash
grep -n "GetPeriodNotFixed" validation_combo.c
```

Après analyse, `GetPeriodNotFixed("3")` retourne un index pour une période de **3 mois**.

**Conclusion:** Dans le contexte web/API, toute cette logique UI est **simplifiée**. La valeur "3" représente directement **3 mois**.

#### 3.5 Décision de Migration

**Option A: Valeur statique simple** (Recommandé pour démarrage)

La logique UI complexe n'est pas nécessaire dans le nouveau système. On retourne directement la période en mois.

```csharp
implementationsDictionary["Period1"] = () => new StringParameter("3");
```

**Option B: Parameter avec métadonnées** (Si UI web a besoin des choix)

```csharp
public class PeriodParameter : IValueProvidedParameter
{
    private readonly string _defaultPeriodValue;

    public PeriodParameter(string defaultPeriodValue)
    {
        _defaultPeriodValue = defaultPeriodValue;
    }

    public ReportParameterMetaData ProvideValue(...)
    {
        parameter.InitialValue = _defaultPeriodValue;
        // Optionnel: ajouter les choix disponibles
        parameter.AvailableChoices = new List<string> { "3", "6", "12", "36", "-1" };
        return parameter;
    }
}
```

#### 3.6 Implémentation Choisie

**Option A - Simple et rapide:**

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs:
implementationsDictionary["Period1"] = () => new StringParameter("3");
implementationsDictionary["Period2"] = () => new StringParameter("6");
implementationsDictionary["Period3"] = () => new StringParameter("12");
implementationsDictionary["Period4"] = () => new StringParameter("36");
implementationsDictionary["Period5"] = () => new StringParameter("-1");  // Since Inception
```

#### 3.7 Leçon Apprise

**⚠️ Piège courant:** Une fonction C++ qui semble complexe (appelle helpers, 50+ lignes) peut en fait être **simplifiée** dans le nouveau système.

**Workflow:**
1. Lire le code C++ complexe
2. **Identifier ce qui est logique UI vs logique métier**
3. Garder seulement la logique métier (la valeur)
4. Simplifier dans le C#

**Temps gagné:** Au lieu de passer 2-3h à migrer toute la logique UI, on fait une implémentation simple en 15 minutes!

#### 3.8 Temps Réel

- Localisation + lecture code C++: 10 minutes
- Analyse de la helper function: 10 minutes
- Décision de simplification: 5 minutes
- Implémentation: 5 minutes
- **Total: 30 minutes** ✅

---

### Exemple 4: Cas avec Piège - GetBoolFromPref (⭐⭐ Niveau 2 - 45 minutes)

#### 4.1 Données du SQL

```csv
PARAM_NAME: PARAM_HideTitleCurrency
Default_Function: GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
Specific_Function: (vide)
PARAMETER_IMPL_FILE: HiddenParametersImplementation.cs
PARAMETER_ENTRY_TYPE: POST
WIDGET_TYPE: 8 (Hidden)
```

#### 4.2 Observation du Pattern SQL

**⚠️ Pattern spécial:** La fonction contient **directement la préférence en paramètre**:
```
GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

Ce n'est **PAS** un nom de fonction C standard!

#### 4.3 Extraction de l'Information

**Nom de la fonction:** `GetBoolFromPref` (générique)
**Préférence:** `PREF_REPORT_HIDE_CURRENCY` (entre parenthèses)

#### 4.4 Recherche dans le Code C

```bash
cd ../monolith/PM/Products/CroesusServer
grep -n "PREF_REPORT_HIDE_CURRENCY" Src/ReportApi/ReportCtr/ReportCtrParam/validation_hided.c
```

**Résultat:** Possiblement aucune fonction explicite! C'est une **fonction générique** qui lit n'importe quelle préférence.

#### 4.5 Code C Générique (hypothétique)

```c
// Pattern typique pour GetBoolFromPref:
CF_STRING sPref = GetCresusConfig()->get("PREF_REPORT_HIDE_CURRENCY");
bool bValue = (sPref.CompareCaseInsensitive("YES") == 0);
pAtt->SetValue(bValue ? "1" : "0");
```

#### 4.6 Implémentation C#

**Fichier:** `ReportManagerAPI.Infrastructure/.../Parameters/Hidden/GetBoolFromPrefReportHideCurrencyParameter.cs`

```csharp
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Repositories;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters.Hidden
{
    /// <summary>
    /// Retourne "1" si PREF_REPORT_HIDE_CURRENCY = "YES", sinon "0".
    ///
    /// Pattern SQL: GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
    /// </summary>
    public class GetBoolFromPrefReportHideCurrencyParameter : IValueProvidedParameter
    {
        private const string PreferenceKey = "PREF_REPORT_HIDE_CURRENCY";
        private readonly IPreferencesRepository _preferencesRepository;

        public GetBoolFromPrefReportHideCurrencyParameter(IPreferencesRepository preferencesRepository)
        {
            _preferencesRepository = preferencesRepository;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            var preference = _preferencesRepository.GetPreference(PreferenceKey);
            parameter.InitialValue = preference?.Value?.ToUpper() == "YES" ? "1" : "0";

            return parameter;
        }
    }
}
```

#### 4.7 Convention de Nommage

**Pattern:**
```
GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                PREF_ + ReportHideCurrency
```

**Nom de la classe:**
```
GetBoolFromPref + ReportHideCurrency + Parameter
```

**Résultat:** `GetBoolFromPrefReportHideCurrencyParameter`

---

### 4.2.1 Propriétés Disponibles sur ReportParameterMetaData

**⚠️ RÉFÉRENCE COMPLÈTE:** Toutes les propriétés modifiables dans `ProvideValue()`.

| Propriété | Type | Description | Exemple | Mapping C++ |
|-----------|------|-------------|---------|-------------|
| `InitialValue` | string | Valeur par défaut du paramètre | "1", "2024-01-01", "USD" | `pAtt->SetValue("1")` |
| `VisibleOnUi` | bool | Afficher/cacher dans l'UI | `true` (affiché), `false` (caché) | `pGroup->SetHideWidgetFlag(!visible)` |
| `EnabledOnUi` | bool | Activer/désactiver le widget | `true` (éditable), `false` (grisé) | `pGroup->Enable(false)` |
| `IsReadOnly` | bool | Lecture seule (visible mais non modifiable) | `true` (lecture seule) | Pas d'équivalent direct |
| `PossibleDisplayValues` | IEnumerable&lt;PossibleDisplayValue&gt; | Choix disponibles (Combobox/Radio) | Liste des options | Callbacks `SetInit`, `SetValue` |
| **Retour `null`** | ReportParameterMetaData? | **Supprime le paramètre complètement** | `return null;` | N/A - nouveau pattern C# |

**Notes importantes:**

**1. VisibleOnUi vs return null**
- `VisibleOnUi = false`: Paramètre existe mais caché, peut être montré plus tard
- `return null`: Paramètre **supprimé du modèle**, n'existe plus

**2. EnabledOnUi vs IsReadOnly**
- `EnabledOnUi = false`: Widget **grisé** (visuellement inactif, pas cliquable)
- `IsReadOnly = true`: Widget **actif** (normal) mais valeur **non modifiable**

**3. PossibleDisplayValues**
- Utilisé pour Combobox (WIDGET_TYPE=1) et Radio (WIDGET_TYPE=2)
- Peut être filtré dynamiquement selon le contexte
- Voir Pattern 7 ci-dessous pour exemples détaillés

**Exemples concrets:**

```csharp
// Cacher un paramètre
parameter.VisibleOnUi = false;
parameter.InitialValue = "0";
return parameter;

// Désactiver un paramètre (grisé)
parameter.EnabledOnUi = false;
parameter.InitialValue = "0";
return parameter;

// Lecture seule
parameter.IsReadOnly = true;
parameter.InitialValue = "USD";
return parameter;

// Supprimer complètement
if (noDataAvailable)
{
    return null;  // Le paramètre n'apparaîtra pas dans l'UI
}
```

---

#### Pattern 7: Manipulation des Choix Disponibles (Combobox/Radio)

**⚠️ PATTERN CRITIQUE:** Pour les paramètres Combobox (WIDGET_TYPE=1) ou Radio (WIDGET_TYPE=2), vous devrez souvent manipuler les choix disponibles via `PossibleDisplayValues`.

**A. Filtrage Dynamique**

**Code C++ typique (validation_radio.c):**
```c
m_pParam->SetInit(InitAssetMixWrapper);
m_pParam->SetValue(C_VALIDATION_RADIO::SetAssetMix);
m_pParam->SetGetValue(C_VALIDATION_RADIO::GetAssetMix);
// Ces callbacks ajoutent/enlèvent des items du combobox
```

**Migration C#:**
```csharp
public ReportParameterMetaData ProvideValue(...)
{
    // Filtrer les choix selon les conditions
    if (!repartitionRepository.FirmRepartitionExist())
    {
        parameter.PossibleDisplayValues =
            parameter.PossibleDisplayValues.Where(x => !x.Value.Contains("MultiLevelFirmAssetMix"));
    }

    // IMPORTANT: Ajuster InitialValue si choix supprimé!
    if (choixSupprimés && parameter.InitialValue == "MultiLevelFirmAssetMix")
    {
        parameter.InitialValue = "MultiLevelBasicAssetMix";  // Valeur alternative
    }

    return parameter;
}
```

**Exemple réel:** `AssetMixSleevesRadioButtonParameter.cs:29-57`

**B. Construction Complète avec Traductions**

Pour construire les choix depuis une BD ou repository:

```csharp
// Exemple: IndCodeComboParameter.cs:44-65
parameter.PossibleDisplayValues = industryCodes.Select(x =>
    new PossibleDisplayValue
    {
        Value = x.IndustryCodeSetId.ToString(),  // Valeur technique
        DisplayValue = new TranslatedDescription
        {
            Key = x.DescriptionEn,
            Values = new List<LocalizedDescription>
            {
                new LocalizedDescription
                {
                    Culture = CultureValue.EnCa,
                    Description = x.DescriptionEn
                },
                new LocalizedDescription
                {
                    Culture = CultureValue.FrCa,
                    Description = x.DescriptionFr
                }
            }
        }
    });
```

**C. Quand Chercher ce Pattern?**

Si dans le code C++ vous voyez:
- ✅ `SetInit()` + `SetValue()` + `SetGetValue()` → Manipulation de choix
- ✅ `pCombo->AddItem()` / `RemoveItem()` → Construction dynamique
- ✅ Boucles sur des données → Probablement pour remplir une liste
- ✅ WIDGET_TYPE = 1 (Combobox) ou 2 (Radio) dans le SQL

**Exemples réels:**
- `AssetMixSleevesRadioButtonParameter.cs` - Filtrage selon préférences et pad
- `IndCodeComboParameter.cs` - Construction complète depuis repository
- `AssetMixRepartitionIDParameter.cs` - Construction de choix custom
- `PreviousCurrentYearParameter.cs` - Construction d'années disponibles

**Mapping C++ → C#:**

| Code C++ | Équivalent C# | Usage |
|----------|---------------|-------|
| `m_pParam->SetInit(InitFunction)` | Initialise `PossibleDisplayValues` | Setup initial |
| `m_pParam->SetValue(SetFunction)` | Modifie `PossibleDisplayValues` | Filtrage dynamique |
| `pCombo->AddItem("value", "display")` | Ajout à `PossibleDisplayValues` | Construction liste |
| `pCombo->RemoveItem(index)` | `Where(x => !x.Value.Contains(...))` | Filtrage |
| `pCombo->Select(index)` | `parameter.InitialValue = "value"` | Sélection par défaut |

---

#### Pattern 8: Supprimer un Paramètre Conditionnellement

**Cas d'usage:** Le paramètre ne doit **PAS apparaître** dans l'UI selon certaines conditions.

**Syntaxe:** `return null;`

**Exemple:**
```csharp
public ReportParameterMetaData ProvideValue(
    ReportParameterMetaData parameter,
    ReportMetaDataFromRtm reportMetaDataFromRtm)
{
    var industryCodes = industryCodeRepository.GetIndustryCodes();

    // Si aucune donnée disponible, supprimer le paramètre
    if (industryCodes.Count == 0)
    {
        Logger.Debug("Removing parameter {ParameterName} - no industry codes available",
            parameter.Name);
        return null;  // ← Le paramètre sera complètement supprimé
    }

    // Sinon, traitement normal
    parameter.InitialValue = industryCodes.First().Id.ToString();
    parameter.PossibleDisplayValues = industryCodes.Select(/* ... */);
    return parameter;
}
```

**Exemple réel:** `IndCodeComboParameter.cs:28-34`

**Différence avec VisibleOnUi = false:**

| Approche | Effet | Quand utiliser |
|----------|-------|----------------|
| `return null` | Paramètre **SUPPRIMÉ**, n'existe plus dans le modèle | Paramètre conditionnel qui ne s'applique jamais dans ce contexte |
| `VisibleOnUi = false` | Paramètre existe mais **caché**, peut être montré plus tard | Paramètre caché par défaut mais peut être révélé dynamiquement |

**Cas d'usage typiques pour `return null`:**
- ✅ Aucune donnée disponible pour remplir un combobox (ex: aucun industry code)
- ✅ Feature désactivée globalement dans les préférences
- ✅ Contexte incompatible (ex: paramètre Account-only sur un rapport Client)

---

#### Pattern 9: Composition avec MultipleValueProvidedParameters

**Cas d'usage:** Appliquer **PLUSIEURS transformations** sur un même paramètre.

**Syntaxe:**
```csharp
implementationsDictionary["FunctionName"] =
    () => new MultipleValueProvidedParameters(
        new FirstParameter(...),   // S'exécute en premier
        new SecondParameter(...)   // Modifie le résultat
    );
```

**Exemple:**
```csharp
// PreParamEntryValueProviderFunctionsExecuter.cs:132-133
implementationsDictionary["SimpleAssetMixRadioButton_RemovedForSleeveContext"] =
    () => new MultipleValueProvidedParameters(
        new SimpleAssetMixRadioButtonParameter(repartitionsRepository),
        new RemovedForSleeveContext(reportCommandAndQueryContextRepository.RequestSourceType)
    );
```

**Comportement:**
1. ✅ Le premier parameter s'exécute (`SimpleAssetMixRadioButtonParameter`)
   - Définit `InitialValue`, `PossibleDisplayValues`, etc.
2. ✅ Le deuxième parameter modifie le résultat (`RemovedForSleeveContext`)
   - Peut changer `VisibleOnUi`, `EnabledOnUi`, ou même retourner `null`
3. ✅ Pattern COMPOSITE - enchaînement de transformations

**Quand l'utiliser:**
- ✅ Logique réutilisable (ex: "Supprimer pour Sleeve") s'applique à PLUSIEURS paramètres
- ✅ Éviter duplication de code
- ✅ Composition de comportements (ex: valeur par défaut + modification contextuelle)

**Exemples réels dans PreParamEntry:**
- `GetIsGraphicIncludedForPerfReport_RemovedForSleeveContext` (lignes 62-63)
- `SimpleAssetMixRadioButton_RemovedForSleeveContext` (lignes 132-133)
- `HideIfNotSingleAccount_RemovedForSleeveContext` (lignes 134-135)

**Pattern typique:**
```csharp
// 1. Créer le parameter de base
public class MyBaseParameter : IValueProvidedParameter { /* ... */ }

// 2. Créer le modificateur réutilisable
public class RemovedForSleeveContext : IValueProvidedParameter
{
    public ReportParameterMetaData ProvideValue(...)
    {
        if (_requestSourceType == SourceTypes.Sleeve)
            return null;  // Supprime le paramètre pour Sleeves
        return parameter;  // Sinon, pas de modification
    }
}

// 3. Composer dans l'executer
implementationsDictionary["MyFunction"] = () => new MultipleValueProvidedParameters(
    new MyBaseParameter(...),
    new RemovedForSleeveContext(...)
);
```

---

#### 4.8 Enregistrement

```csharp
// Dans PostParamEntryValueProviderFunctionsExecuter.cs:
implementationsDictionary["GetBoolFromPrefReportHideCurrency"] =
    () => new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
```

#### 4.9 Tests

```csharp
public class GetBoolFromPrefReportHideCurrencyParameterTests
{
    private readonly IPreferencesRepository preferencesRepository;

    public GetBoolFromPrefReportHideCurrencyParameterTests()
    {
        preferencesRepository = Mock.Of<IPreferencesRepository>();
    }

    [Theory]
    [InlineData("YES", "1")]
    [InlineData("NO", "0")]
    [InlineData("yes", "1")]  // Case insensitive
    [InlineData(null, "0")]
    public void GivenPreferenceValue_WhenProvideValue_ThenReturnsExpectedValue(
        string prefValue, string expectedResult)
    {
        // Arrange
        var preferencesRepositoryMock = Mock.Get(preferencesRepository);
        preferencesRepositoryMock
            .Setup(x => x.GetPreference("PREF_REPORT_HIDE_CURRENCY"))
            .Returns(prefValue == null ? null : new Preference
            {
                Name = "PREF_REPORT_HIDE_CURRENCY",
                Value = prefValue
            });

        var parameter = new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
        var reportParameterMetaData = new ReportParameterMetaData();
        var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

        // Act
        var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

        // Assert
        result.InitialValue.Should().Be(expectedResult);
    }
}
```

#### 4.10 Temps Réel

- Identification du pattern SQL: 5 minutes
- Extraction préférence: 2 minutes
- Recherche code C (optionnel): 5 minutes
- Implémentation: 15 minutes
- Enregistrement: 2 minutes
- Tests: 15 minutes
- **Total: 44 minutes** ✅

#### 4.11 Template Réutilisable

**Pour les 6 autres GetBoolFromPref du rapport:**

1. Copier le fichier et renommer
2. Changer la constante `PreferenceKey`
3. Changer le nom de la classe
4. Copier les tests et adapter

**Temps par fonction additionnelle:** 15 minutes

**Total pour 7 fonctions:** 44min + (6 × 15min) = **2h 14min**

---

## Récapitulatif des 4 Exemples

| Exemple | Niveau | Temps Estimé | Temps Réel | Leçon Clé |
|---------|--------|--------------|------------|-----------|
| SinceInception | ⭐ Niveau 1 | 10min | 5min | UnimplementedParameter ≠ Complexe |
| InitDefaultIndex | ⭐⭐ Niveau 2 | 1h | 52min | Condition simple = IValueProvidedParameter |
| Period1-5 | ⭐⭐ Niveau 2-3 | 2-3h | 30min | Simplifier logique UI complexe |
| GetBoolFromPref | ⭐⭐ Niveau 2 | 45min/fonction | 44min | Pattern SQL spécial + template réutilisable |

**Conclusion:** Avec la bonne approche, la migration est **beaucoup plus rapide** que prévu!

---

## Checklist finale

### Pour chaque paramètre migré:

- [ ] Fonction C++ localisée et documentée
- [ ] Dépendances identifiées (Repositories requis)
- [ ] ValueProviderParameter créé (si applicable)
- [ ] Logique C++ → C# transformée correctement
- [ ] Enregistré dans Pre/PostParamEntryValueProviderFunctionsExecuter
- [ ] `ValueProviderFunction` ajouté dans Parameters.cs
- [ ] Tests unitaires écrits et passent
- [ ] Code review interne effectué
- [ ] TODO comments supprimés

### Pour le rapport complet:

- [ ] Tous les paramètres du CSV traités
- [ ] Aucun `UnimplementedParameter()` sans TODO
- [ ] Build réussit: `dotnet build`
- [ ] Tests réussissent: `dotnet test`
- [ ] Code coverage acceptable
- [ ] Documentation de migration mise à jour
- [ ] PR créée avec description détaillée
- [ ] Template de rapport testé en local

---

## Exemples de PR de référence

### RPT-17858 - Gains et Pertes Non Réalisés

**PR principale:** #5972 (merged 2025-05-21)
**PR fix:** #6155 (merged 2025-06-06)

**Paramètres migrés:**
- ✅ `InitDisplayCheckDigit` - Préférence + SourceType
- ✅ `IsCliRootManagement` - Préférence + SourceType
- ✅ `InitGainLossCostDisplayed` - Préférences multiples
- ✅ `GetAccTypeForAccExpandedSrc` - Préférence CASH_ACCOUNTS
- ⚠️ TODOs marqués pour implémentation future:
  - `AssetMixRadioButton`
  - `AssetMixRepartitionCombo`
  - `EvalDontUseViewParam`
  - `EvalSimpleEntryPoint`
  - Etc.

**Fichiers modifiés:** 18 fichiers
**Lignes changées:** ~1884 lignes

**Temps estimé:** 2-3 jours pour rapport de complexité moyenne

---

## Conseils et astuces

### Guidelines de Logging

**Pattern recommandé:**
```csharp
using Serilog;

public class YourParameterClassName : IValueProvidedParameter
{
    private static ILogger Logger => Log.Logger.ForContext<YourParameterClassName>();

    public ReportParameterMetaData ProvideValue(
        ReportParameterMetaData parameter,
        ReportMetaDataFromRtm reportMetaDataFromRtm)
    {
        // Log au début pour debugging (optionnel)
        Logger.ForContext(parameter, reportMetaDataFromRtm)
            .Debug("Processing parameter {ParameterName}", parameter.Name);

        // Log les erreurs critiques
        if (preference == null)
        {
            Logger.Error(
                "Croesus Services api was not able to resolve preference {PreferenceName}",
                PreferenceKey);
            throw new Exception($"Preference {PreferenceKey} not found");
        }

        // Log les décisions importantes (optionnel)
        if (industryCodes.Count == 0)
        {
            Logger.Debug("Removing parameter {ParameterName} - no industry codes available",
                parameter.Name);
            return null;
        }

        // Log le résultat (optionnel - seulement pour debugging)
        Logger.Debug("Returning InitialValue: {InitialValue}", parameter.InitialValue);
        return parameter;
    }
}
```

**Quand logger:**
- ✅ **Erreurs critiques** (préférence/donnée manquante) → `Logger.Error()`
- ✅ **Décisions importantes** (paramètre supprimé, choix modifiés) → `Logger.Debug()`
- ✅ **Debugging complexe** (logique conditionnelle multiple) → `Logger.Debug()`
- ❌ **PAS** pour chaque ligne de code
- ❌ **PAS** pour paramètres triviaux (StringParameter, TrueParameter)

**Exemples réels:**
- `InitDisplayCheckDigitParameter.cs:18, 32-34` - Logging d'erreur pour préférence manquante
- `IndCodeComboParameter.cs:30-32` - Logging de décision (suppression paramètre)

---

### Incohérences dans le Code Legacy

**⚠️ ATTENTION:** Certains parameters migrés utilisent des patterns **OBSOLÈTES** ou **INCORRECTS**.

**Ne pas copier ces patterns:**

#### 1. GetPreferencesValue pour une seule préférence

**Incorrect (code legacy existant):**
```csharp
// FirmCurrencyParameter.cs:24-27 - NE PAS COPIER
var listPref = new List<string>() { preference };
var returnedPreference = preferencesRepository.GetPreferencesValue(listPref).Result.FirstOrDefault();
```

**Correct (nouveau code):**
```csharp
var preference = _preferencesRepository.GetPreference("PREF_NAME");
```

#### 2. Absence de logging pour erreurs critiques

Certains anciens parameters ne loggent pas les erreurs, rendant le debugging difficile.

**Toujours logger les erreurs:**
```csharp
if (preference == null)
{
    Logger.Error("Preference {PreferenceName} not found", PreferenceKey);
    throw new Exception($"Preference {PreferenceKey} not found");
}
```

#### 3. Constantes hardcodées vs définies

**À améliorer:**
```csharp
var pref = _preferencesRepository.GetPreference("PREF_DISPLAY_CHECK_DIGIT");
```

**Recommandé:**
```csharp
private const string PreferenceKey = "PREF_DISPLAY_CHECK_DIGIT";
var pref = _preferencesRepository.GetPreference(PreferenceKey);
```

**Règle générale:**
> **Lors de la migration, utilisez TOUJOURS les patterns recommandés de ce document, même si le code existant fait autrement.**

---

### Débogage

**Si un paramètre ne fonctionne pas:**
1. Vérifier enregistrement dans executer (typo dans le nom?)
2. Vérifier `ValueProviderFunction` dans Parameters.cs
3. Vérifier injection dépendances (null?)
4. Ajouter logging avec Serilog
5. Vérifier valeurs retournées (format correct?)

**Logging utile:**

```csharp
private static ILogger Logger => Log.Logger.ForContext<FunctionNameParameter>();

public ReportParameterMetaData ProvideValue(...)
{
    var logger = Logger.ForContext("ParameterName", parameter.Name);
    logger.Debug("Starting ProvideValue for {ParameterName}", parameter.Name);

    // ... logique ...

    logger.Debug("Returning InitialValue: {InitialValue}", parameter.InitialValue);
    return parameter;
}
```

### Optimisation

- Grouper récupérations de préférences multiples (`GetPreferencesValue`)
- Mettre en cache valeurs calculées lourdes
- Éviter appels répétitifs au FrameworkServer

### Ressources

**Code snippets:**
- `MyCustomSnippets.code-snippets` → `ivalueProvidedParameter`

**Documentation Croesus:**
- [BusinessBrowserWebApi](../monolith/README.BusinessBrowserWebApi.md)
- [Contributing](../monolith/CONTRIBUTING.md)

**Références externes:**
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [FluentValidation](https://docs.fluentvalidation.net/)
- [Mapster](https://github.com/MapsterMapper/Mapster)

---

**Dernière mise à jour:** 2025-11-17
**Analysé par:** Claude Code (AI)
**Basé sur:** PR #5972 - RPT-17858, Validation RPT-17862 - PERF_ACC_SUMM

**Améliorations 2025-11-17 (Version 1):**
- ✅ Ajout WIDGET_TYPE 4 (List), 7 (String), 9 (MultiLangTextBox) dans tableau de mapping
- ✅ Nouvelle section 2.3: Règle de priorité Default vs Specific
- ✅ Nouvelle section 3.6: Fonctions Génériques du Framework (CheckTrue, CheckFalse, etc.)
- ✅ Stratégie de recherche pour noms de fonctions non standard (section 3.2)
- ✅ Pattern 6: GetBoolFromPref(PREF_XXX) avec exemples complets
- ✅ Section 4.4: ValidationFunction vs ValueProviderFunction avec tableau de décision

**Améliorations 2025-11-17 (Version 2 - Analyse code migré):**
- ✅ Section 4.1.1: Helper Parameters Réutilisables (StringParameter, TrueParameter, etc.)
- ✅ Section 4.2.1: Propriétés Disponibles sur ReportParameterMetaData (tableau complet)
- ✅ **Pattern 7: Manipulation des Choix Disponibles (PossibleDisplayValues)** - CRITIQUE
- ✅ **Pattern 8: Supprimer un Paramètre Conditionnellement (return null)** - NOUVEAU
- ✅ **Pattern 9: Composition avec MultipleValueProvidedParameters** - AVANCÉ
- ✅ Amélioration Pattern 2: GetPreference vs GetPreferencesValue avec règles claires
- ✅ Guidelines de Logging dans Conseils et astuces
- ✅ Section Incohérences dans le Code Legacy (patterns obsolètes à éviter)
- ✅ Exemples réels de code migré avec références de lignes précises

**Patterns découverts par analyse du code:**
- 23 usages de `PossibleDisplayValues` dans les parameters migrés
- Pattern `return null` utilisé dans IndCodeComboParameter pour supprimer paramètres
- Pattern `MultipleValueProvidedParameters` utilisé 4 fois dans PreParamEntry
- Incohérence: FirmCurrencyParameter utilise ancien pattern GetPreferencesValue pour 1 seule préférence
