# Guide de Migration des Rapports C++ vers C#

## 📖 À propos de ce guide

Ce document est votre compagnon pour migrer des rapports du système legacy C++ (CroesusServer) vers la nouvelle architecture C# (ReportManagerApi). Contrairement au document technique MIGRATION_PROCEDURE.md qui sert de référence pour l'automatisation, ce guide est conçu pour vous accompagner pas à pas avec des explications détaillées.

**Basé sur l'analyse de :** PR #5972 - Rapport "Gains et Pertes Non Réalisés" (GP_NON_REALISE)

---

## 🎯 Vue d'ensemble : Comprendre la migration

### Qu'est-ce qu'on migre exactement ?

Lorsqu'un rapport est exécuté, il utilise des **paramètres** (dates, options, filtres, etc.). Dans le système C++, ces paramètres sont gérés par des fonctions C++ dispersées dans CroesusServer. Notre objectif est de **recréer cette logique en C#** dans le nouveau système ReportManagerApi.

### Le flux de migration en un coup d'œil

```
1. Extraire la liste     2. Trouver le code     3. Comprendre la      4. Recréer en C#
   des paramètres           C++ correspondant      logique métier         et tester
   du rapport

   ↓ SQL Query             ↓ grep, recherche      ↓ Analyse            ↓ IValueProvidedParameter
```

### Où se trouve le code ?

**Avant (C++ - Lecture seule) :**
```
repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/
├── validation_check.c     # Checkboxes (paramètres cochables)
├── validation_combo.c     # Comboboxes (listes déroulantes)
├── validation_radio.c     # Boutons radio
├── validation_date.c      # Dates
├── validation_hided.c     # Paramètres cachés (calculs internes)
└── ...
```

**Après (C# - Destination) :**
```
ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/
├── [NomFonction]Parameter.cs     # Vos nouvelles implémentations
├── Hidden/                        # Paramètres cachés
├── Date/                          # Paramètres de date
└── ...
```

---

## 📋 Table des matières détaillée

1. [Étape 1 : Extraction des paramètres du rapport](#étape-1--extraction-des-paramètres-du-rapport)
2. [Étape 2 : Classification et priorisation](#étape-2--classification-et-priorisation)
3. [Étape 3 : Localisation du code C++](#étape-3--localisation-du-code-c)
4. [Étape 4 : Analyse et compréhension](#étape-4--analyse-et-compréhension)
5. [Étape 5 : Implémentation C#](#étape-5--implémentation-c)
6. [Étape 6 : Enregistrement et configuration](#étape-6--enregistrement-et-configuration)
7. [Étape 7 : Tests](#étape-7--tests)
8. [Exemples complets de A à Z](#exemples-complets-de-a-à-z)
9. [Patterns de transformation courants](#patterns-de-transformation-courants)
10. [Troubleshooting et FAQ](#troubleshooting-et-faq)

---

## Étape 1 : Extraction des paramètres du rapport

### 🎯 Objectif
Obtenir la liste complète des paramètres du rapport et comprendre leur structure.

### Comment faire

1. **Exécuter la requête SQL du rapport** (fournie par l'équipe)
2. **Exporter les résultats en CSV** pour référence
3. **Créer un fichier de travail** : `docs/MIGRATION-{REPORT-ID}.md`

### Comprendre les colonnes du CSV

Voici les informations clés que vous obtiendrez :

| Colonne | Ce que ça signifie | Exemple |
|---------|-------------------|---------|
| `PARAM_NAME` | Nom technique du paramètre | `PARAM_IndCodeCombo` |
| `Default_Function` | Fonction générique réutilisable | `IndCodeCombo` |
| `Specific_Function` | Fonction spécifique au rapport | `InitGainLossCostDisplayed` |
| `PARAMETER_IMPL_FILE` | Où ira le code C# | `ComboBoxParametersImplementation.cs` |
| `PARAMETER_ENTRY_TYPE` | Quand s'exécute la fonction | `PRE` (avant) ou `POST` (après) |
| `WIDGET_TYPE` | Type de contrôle UI | `1` (Combobox), `3` (Checkbox), etc. |

### 💡 Point clé

Si un paramètre a **à la fois** `Default_Function` ET `Specific_Function`, c'est **toujours** la `Specific_Function` qui a la priorité. La `Default_Function` est juste une suggestion de fallback.

### Exemple concret

```csv
PARAM_NAME,Default_Function,Specific_Function,PARAMETER_IMPL_FILE,PARAMETER_ENTRY_TYPE,WIDGET_TYPE
PARAM_IndCodeCombo,IndCodeCombo,,ComboBoxParametersImplementation.cs,PRE,1
PARAM_GainLossCostDisplayed,,InitGainLossCostDisplayed,CheckBoxParametersImplementation.cs,PRE,3
PARAM_AsOfDate,AsOfDate,,DateParametersImplementation.cs,PRE,5
```

**Interprétation :**
- `PARAM_IndCodeCombo` : Utilise la fonction générique `IndCodeCombo` (probablement déjà implémentée)
- `PARAM_GainLossCostDisplayed` : Nécessite une migration de `InitGainLossCostDisplayed` (fonction spécifique)
- `PARAM_AsOfDate` : Fonction générique de date

---

## Étape 2 : Classification et priorisation

### 🎯 Objectif
Identifier quelles fonctions nécessitent réellement du travail et dans quel ordre les traiter.

### Les 3 statuts possibles

#### ✅ Statut 1 : Déjà implémenté
**Comment vérifier :**
```bash
cd ../monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure
grep -n "NomDeLaFonction" Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs
```

**Si vous voyez :**
```csharp
implementationsDictionary["AsOfDate"] = () => new AsOfDateParameter(dateTimeService);
```
✅ **Aucune action requise** - la fonction est déjà migrée !

#### ⚠️ Statut 2 : Marqué TODO
**Si vous voyez :**
```csharp
implementationsDictionary["InitGainLossCost"] = () => new UnimplementedParameter(); // TODO
```
⚠️ **Priorité haute** - c'est bloquant pour le rapport, mais au moins c'est identifié.

#### 🔴 Statut 3 : Inexistant
**Si grep ne retourne rien** :
🔴 **Priorité critique** - la fonction n'existe même pas encore, il faut tout créer.

### 💡 Conseil pratique

Ne vous fiez PAS au statut pour juger la complexité ! Une fonction `UnimplementedParameter()` peut être triviale (5 minutes) alors qu'une fonction déjà partiellement implémentée peut nécessiter des ajustements complexes.

### Les 5 niveaux de complexité réelle

Voici comment évaluer rapidement la difficulté d'une migration :

| Niveau | Temps | Signes distinctifs | Exemple |
|--------|-------|-------------------|---------|
| ⭐ Niveau 0 | 5-10 min | Valeur hardcodée pure : `pAtt->SetValue("3")` | `Period1` → `"3"` |
| ⭐ Niveau 1 | 10-30 min | Une seule action simple : `pGroup->Select(true)` | `SinceInception` → checkbox cochée |
| ⭐⭐ Niveau 2 | 30min-1h | Un seul `if/else` sur préférence OU pad | `InitDefaultIndex` - selon Portfolio ou non |
| ⭐⭐⭐ Niveau 3 | 1-2h | Plusieurs préférences OU conditions multiples | `InitGainLossCost` - 2 préférences combinées |
| ⭐⭐⭐⭐ Niveau 4 | 2-4h+ | Boucles, calculs, BD, > 30 lignes | Fonctions complexes avec logique métier |

### Checklist rapide de complexité (30 secondes)

Lisez les 10 premières lignes du code C++ et cochez :
- [ ] La fonction fait juste `pAtt->SetValue("valeur_fixe")`
- [ ] La fonction ne contient que des if/else simples
- [ ] La fonction accède à 1 seule préférence
- [ ] La fonction n'a PAS de boucles (for, while)
- [ ] La fonction n'a PAS de requêtes SQL/BD
- [ ] La fonction n'a PAS de calculs mathématiques complexes
- [ ] La fonction fait < 30 lignes

**Si 7+ cases cochées** : Niveau 0-1 (< 30min)
**Si 4-6 cases cochées** : Niveau 2-3 (30min-2h)
**Si 0-3 cases cochées** : Niveau 4 (2-4h+)

---

## Étape 3 : Localisation du code C++

### 🎯 Objectif
Trouver le fichier C++ exact qui contient la logique de la fonction à migrer.

### Mapping WIDGET_TYPE → Fichier C++

C'est simple : le `WIDGET_TYPE` du SQL vous indique directement où chercher !

| WIDGET_TYPE | Nom | Fichier C++ | Exemple de paramètre |
|-------------|-----|-------------|---------------------|
| 1 | Combobox | `validation_combo.c` | Liste déroulante de devises |
| 2 | Radio button | `validation_radio.c` | Choix entre méthodes de calcul |
| 3 | Checkbox | `validation_check.c` | "Afficher les détails" |
| 4 | List | `validation_list.c` | Sélection multiple |
| 5 | Date | `validation_date.c` | Date de début/fin |
| 7 | String/File | `validation_file.c` | Champ texte |
| 8 | Hidden | `validation_hided.c` | Paramètres internes/calculés |
| 9 | Multi-lang textbox | `validation_multilang_textbox.c` | Texte multilingue |

### Stratégie de recherche par étapes

#### Étape 1 : Aller au bon endroit
```bash
cd ../monolith/PM/Products/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/
```

#### Étape 2 : Chercher la fonction par nom
```bash
# Remplacez "InitGainLossCost" par le nom de votre fonction
grep -n "InitGainLossCost" validation_check.c | head -10
```

#### Étape 3 : Lire l'implémentation
Si `grep` trouve la ligne 1234 :
```bash
# Méthode A : Afficher 50 lignes après la ligne trouvée
grep -A 50 "InitGainLossCost" validation_check.c

# Méthode B : Afficher les lignes 1234 à 1300
sed -n '1234,1300p' validation_check.c
```

### 🚨 Que faire si grep ne trouve rien ?

**Plan B - Recherche par fragments :**

Décomposez le nom en parties et cherchez séparément :

```bash
# Exemple : PerfAccSummGetSubReportField
# → Cherchez "AccSumm" puis "SubReportField"

grep -n "AccSumm" validation_hided.c
grep -n "SubReportField" validation_hided.c
```

**Plan C - Recherche par nom de paramètre :**

```bash
# Si la fonction s'appelle InitGainLossCost,
# le paramètre pourrait être PARAM_GainLossCost
grep -n "PARAM_GainLossCost" validation_check.c
```

**Plan D - Recherche large dans tout ReportApi :**

```bash
cd ../../../..  # Revenir à Src/ReportApi
grep -rn "InitGainLossCost" .
```

### 💡 Astuce pour les noms tronqués

Certains noms de fonctions dans le SQL sont raccourcis. Exemples courants :
- `Init*` peut être `Initialize*` en C++
- `Get*` peut être `Retrieve*` en C++
- Cherchez aussi sans le préfixe `Init`

---

## Étape 4 : Analyse et compréhension

### 🎯 Objectif
Comprendre ce que fait réellement le code C++ **sans être expert en C++**.

### Guide de lecture rapide du code C++

#### Ce qu'on peut IGNORER (boilerplate) ✋

Ces éléments sont du code technique C++ qui n'a pas d'équivalent en C# :

```c
// ❌ IGNOREZ TOUT CELA :
C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;
C_ATTRIBUTE *pAtt = pGroup->GetValue();
if (pAtt == NULL)
{
    return;
}
if (pGroup != NULL)
{
    // ...
}
```

**Pourquoi ?** C'est de la gestion de pointeurs C++, pas de la logique métier.

#### Ce qui est IMPORTANT ⭐

**1. Tous les `SetValue` - C'EST LA VALEUR RETOURNÉE !**
```c
pAtt->SetValue("1");     // ← IMPORTANT! Retourne "1"
pAtt->SetValue("USD");   // ← IMPORTANT! Retourne "USD"
```

**2. Tous les accès aux préférences**
```c
GetCresusConfig()->get("PREF_DISPLAY_CHECK_DIGIT");  // ← IMPORTANT! Lit une config
GetPreference("PREF_XXX");                           // ← IMPORTANT! Même chose
```

**3. Tous les `GetPad()` - Type de source du rapport**
```c
if (pReportApi->GetPad() == REPORT_CLIENT)   // ← IMPORTANT! Condition métier
if (pad == REPORT_ACCOUNT)                   // ← IMPORTANT!
```

**4. Les conditions métier (if/else avec logique)**
```c
if (preference == "YES" && pad == REPORT_CLIENT)  // ← IMPORTANT! Logique métier
{
    pAtt->SetValue("1");
}
```

**5. Les appels à d'autres fonctions**
```c
InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);  // ← IMPORTANT! Suivre cette fonction
```

### Patterns C++ courants et leur signification

#### Pattern 1 : Valeur statique simple
```c
pAtt->SetValue("3");
```
**Signification :** Retourne toujours "3"
**Migration C# :** `parameter.InitialValue = "3";`
**Complexité :** ⭐ Niveau 0 (5 minutes)

#### Pattern 2 : Cocher/décocher une checkbox
```c
pGroup->Select(true);   // Cocher
pGroup->Select(false);  // Décocher
```
**Signification :** Valeur booléenne
**Migration C# :** `parameter.InitialValue = "1";` ou `"0"`
**Complexité :** ⭐ Niveau 1 (10 minutes)

#### Pattern 3 : Condition sur préférence
```c
CF_STRING sPref = GetCresusConfig()->get("PREF_DISPLAY_CHECK_DIGIT");
if (sPref == "YES")
{
    pAtt->SetValue("1");
}
else
{
    pAtt->SetValue("0");
}
```
**Signification :** La valeur dépend d'une configuration système
**Migration C# :** Injecter `IPreferencesRepository`
**Complexité :** ⭐⭐ Niveau 2 (30min-1h)

#### Pattern 4 : Condition sur le type de source (Pad)
```c
eReportPad pad = pReportApi->GetPad();
if (pad == REPORT_CLIENT)
{
    pAtt->SetValue("1");
}
else if (pad == REPORT_ACCOUNT)
{
    pAtt->SetValue("0");
}
```
**Signification :** La valeur dépend du contexte d'exécution (Client vs Compte vs Portfolio)
**Migration C# :** Injecter `SourceTypes requestSourceType`
**Complexité :** ⭐⭐ Niveau 2 (30min-1h)

#### Pattern 5 : Préférences multiples
```c
CF_STRING sAddTheo = GetCresusConfig()->get("PREF_ADD_THEORETICAL_VALUE");
CF_STRING sStripBond = GetCresusConfig()->get("PREF_STRIP_BOND_GL1");

int addTheo = (sAddTheo == "YES") ? 1 : 0;
int stripBond = (sStripBond == "YES") ? 1 : 0;

if (addTheo == 1 && stripBond == 0)
{
    pAtt->SetValue("1");
}
```
**Signification :** Logique conditionnelle sur plusieurs configurations
**Migration C# :** `GetPreferencesValue(List<string>)` pour récupérer plusieurs préférences en un appel
**Complexité :** ⭐⭐⭐ Niveau 3 (1-2h)

### Identifier les dépendances C#

Pendant votre lecture, notez quels repositories/services vous aurez besoin :

| Ce que vous voyez en C++ | Repository/Service C# requis |
|--------------------------|------------------------------|
| `GetCresusConfig()->get("PREF_XXX")` | `IPreferencesRepository` |
| `GetPreference("PREF_XXX")` | `IPreferencesRepository` |
| `GetParam("PARAM_XXX")` | `IReportCommandAndQueryContextRepository` |
| `GetPad()` | `SourceTypes` (injection constructor) |
| Opérations de dates | `IParameterDateValueService` |
| Requêtes BD sur repartitions | `IRepartitionRepository` |
| Requêtes BD sur codes industrie | `IIndustryCodeRepository` |
| Requêtes BD sur indices | `IIndexesRepository` |

### 💡 Technique de lecture rapide (scan visuel)

1. **Ouvrez le fichier C++**
2. **Faites défiler rapidement** en cherchant visuellement :
   - Le mot `SetValue` (compte combien de fois)
   - Le mot `GetCresusConfig` ou `GetPreference` (compte combien)
   - Le mot `GetPad` (oui/non)
   - Le mot `if` (compte combien)
   - Le mot `for` ou `while` (oui/non = complexe)
3. **Lisez SEULEMENT les lignes avec ces mots-clés**
4. **Notez les dépendances** dans votre fichier de migration

**Temps : 30-60 secondes par fonction !**

---

## Étape 5 : Implémentation C#

### 🎯 Objectif
Recréer la logique C++ en C# moderne et testable.

### Choix de l'approche : Simple ou Custom ?

#### Option A : Utiliser les classes helper (RECOMMANDÉ pour les cas simples)

Pour les **fonctions triviales** (niveaux 0-1), utilisez ces classes préfabriquées :

| Classe | Quand l'utiliser | Code |
|--------|------------------|------|
| `StringParameter` | Valeur fixe quelconque | `new StringParameter("3")` |
| `TrueParameter` | Toujours "1" (true) | `new TrueParameter()` |
| `FalseParameter` | Toujours "0" (false) | `new FalseParameter()` |
| `EmptyParameter` | Chaîne vide "" | `new EmptyParameter()` |
| `VoidParameter` | Ne fait rien (placeholder) | `new VoidParameter()` |

**Exemple d'utilisation :**
```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs
implementationsDictionary["Period1"] = () => new StringParameter("3");
implementationsDictionary["SinceInception"] = () => new TrueParameter();
implementationsDictionary["DisplayAscCode"] = () => new FalseParameter();
```

**⚠️ Important :** N'inventez PAS une nouvelle classe Parameter si une de ces classes fait déjà le travail !

#### Option B : Créer un IValueProvidedParameter custom

Pour les **fonctions avec logique** (niveaux 2+), créez une classe dédiée :

**Localisation :**
```
ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/
├── [NomFonction]Parameter.cs
├── Hidden/
└── Date/
```

**Template de base :**
```csharp
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Repositories;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters
{
    /// <summary>
    /// [Description de ce que fait le paramètre]
    ///
    /// Migré depuis: validation_check.c:[numéro de ligne]
    /// </summary>
    public class [NomFonction]Parameter : IValueProvidedParameter
    {
        // Constantes pour les clés de préférences
        private const string PreferenceKey = "PREF_XXX";

        // Dépendances injectées
        private readonly IPreferencesRepository _preferencesRepository;

        public [NomFonction]Parameter(IPreferencesRepository preferencesRepository)
        {
            _preferencesRepository = preferencesRepository;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            // 1. Récupérer les données nécessaires
            var preference = _preferencesRepository.GetPreference(PreferenceKey);

            // 2. Valider
            if (preference == null)
            {
                Logger.Error("Preference {PreferenceName} not found", PreferenceKey);
                throw new Exception($"Preference {PreferenceKey} not found");
            }

            // 3. Appliquer la logique métier
            if (preference.Value?.ToUpper() == "YES")
            {
                parameter.InitialValue = "1";
            }
            else
            {
                parameter.InitialValue = "0";
            }

            // 4. Retourner le paramètre modifié
            return parameter;
        }
    }
}
```

### Patterns de transformation C++ → C#

#### Pattern 1 : Préférence simple (1 seule)

**C++ :**
```c
CF_STRING sPref = GetCresusConfig()->get("PREF_DISPLAY_CHECK_DIGIT");
if (sPref == "YES")
    return "1";
return "0";
```

**C# :**
```csharp
var preference = _preferencesRepository.GetPreference("PREF_DISPLAY_CHECK_DIGIT");

if (preference == null)
    throw new Exception("Preference PREF_DISPLAY_CHECK_DIGIT not found");

parameter.InitialValue = preference.Value?.ToUpper() == "YES" ? "1" : "0";
return parameter;
```

**⚠️ Bonne pratique :** Utilisez `GetPreference(string)` pour UNE seule préférence.

#### Pattern 2 : Préférences multiples (2+)

**C++ :**
```c
CF_STRING sAddTheo = GetPreference("PREF_ADD_THEORETICAL_VALUE");
CF_STRING sStripBond = GetPreference("PREF_STRIP_BOND_GL1");

if (sAddTheo == "YES" && sStripBond == "NO")
    return "1";
return "0";
```

**C# :**
```csharp
// Récupérer les 2 préférences en un seul appel (optimisation)
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

**⚠️ Bonne pratique :** Utilisez `GetPreferencesValue(List<string>)` pour PLUSIEURS préférences (évite les appels multiples).

#### Pattern 3 : Type de source (Pad)

**C++ :**
```c
eReportPad pad = pReportApi->GetPad();
if (pad == REPORT_PORTFOLIO)
{
    return "0";
}
return "1";
```

**C# :**
```csharp
// Injecté dans le constructeur
private readonly SourceTypes _requestSourceType;

public MonParameter(SourceTypes requestSourceType)
{
    _requestSourceType = requestSourceType;
}

public ReportParameterMetaData ProvideValue(...)
{
    if (_requestSourceType == SourceTypes.Portfolio)
    {
        parameter.InitialValue = "0";
        parameter.EnabledOnUi = false;  // Souvent désactivé aussi
    }
    else
    {
        parameter.InitialValue = "1";
    }

    return parameter;
}
```

#### Pattern 4 : Visibilité et activation

**C++ :**
```c
pGroup->SetHideWidgetFlag(!bVisible);  // Cacher/montrer
pGroup->Enable(false);                  // Désactiver
```

**C# :**
```csharp
parameter.VisibleOnUi = false;   // Cacher le paramètre
parameter.EnabledOnUi = false;   // Désactiver (grisé)
parameter.IsReadOnly = true;     // Lecture seule
```

### Propriétés disponibles sur ReportParameterMetaData

Voici tout ce que vous pouvez modifier :

| Propriété | Type | Usage | Exemple |
|-----------|------|-------|---------|
| `InitialValue` | string | Valeur par défaut | `"1"`, `"2024-01-01"`, `"USD"` |
| `VisibleOnUi` | bool | Afficher/cacher | `false` = caché |
| `EnabledOnUi` | bool | Activer/désactiver | `false` = grisé (non cliquable) |
| `IsReadOnly` | bool | Lecture seule | `true` = visible mais non modifiable |
| `PossibleDisplayValues` | IEnumerable&lt;PossibleDisplayValue&gt; | Choix disponibles (Combo/Radio) | Liste d'options |

**⚠️ Cas spécial - Supprimer un paramètre :**
```csharp
if (aucuneDonnéeDisponible)
{
    return null;  // Le paramètre n'apparaîtra PAS dans l'UI
}
```

### 💡 Conseils de logging

Ajoutez des logs pour faciliter le debugging :

```csharp
using Serilog;

public class MonParameter : IValueProvidedParameter
{
    private static ILogger Logger => Log.Logger.ForContext<MonParameter>();

    public ReportParameterMetaData ProvideValue(...)
    {
        // Log les erreurs critiques
        if (preference == null)
        {
            Logger.Error("Preference {PreferenceName} not found", PreferenceKey);
            throw new Exception($"Preference {PreferenceKey} not found");
        }

        // Log les décisions importantes
        if (industryCodes.Count == 0)
        {
            Logger.Debug("Removing parameter {ParameterName} - no data", parameter.Name);
            return null;
        }

        return parameter;
    }
}
```

---

## Étape 6 : Enregistrement et configuration

### 🎯 Objectif
Rendre votre nouveau parameter accessible au système.

### Étape 6.1 : Enregistrer dans l'executer

**Fichier à modifier :**
- Si `PARAMETER_ENTRY_TYPE = PRE` : `PreParamEntryValueProviderFunctionsExecuter.cs`
- Si `PARAMETER_ENTRY_TYPE = POST` : `PostParamEntryValueProviderFunctionsExecuter.cs`

**Chemin :**
```
ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/
```

**Méthode à modifier :** `InitializeValueProviderFunctionImplementations`

**Code à ajouter (ordre alphabétique STRICT) :**

```csharp
protected override void InitializeValueProviderFunctionImplementations(
    Dictionary<string, Func<IValueProvidedParameter>> implementationsDictionary)
{
    // ... autres entrées existantes (ordre alphabétique) ...

    // VOTRE NOUVELLE ENTRÉE (insérer au bon endroit alphabétique)
    implementationsDictionary["NomDeLaFonction"] =
        () => new NomDeLaFonctionParameter(preferencesRepository, requestSourceType);

    // ... suite des entrées ...
}
```

**💡 Astuce pour l'ordre alphabétique :**
```csharp
// A
implementationsDictionary["AsOfDate"] = ...
implementationsDictionary["AssetMixCombo"] = ...

// B
implementationsDictionary["BenchmarkCombo"] = ...

// I
implementationsDictionary["InitDefaultIndex"] = ...    // ← Votre fonction ici
implementationsDictionary["InitDisplayCheck"] = ...

// P
implementationsDictionary["Period1"] = ...
```

### Étape 6.2 : Injection de dépendances

Les repositories/services sont déjà disponibles dans le constructeur de l'executer :

**Disponibles par défaut :**
- `preferencesRepository` : `IPreferencesRepository`
- `reportCommandAndQueryContextRepository` : `IReportCommandAndQueryContextRepository`
- `requestSourceType` : `SourceTypes`
- `dateTimeService` : `IDateTimeService`
- `repartitionsRepository` : `IRepartitionRepository`

**Si vous avez besoin d'un nouveau repository :**

1. L'ajouter au constructeur :
```csharp
public PostParamEntryValueProviderFunctionsExecuter(
    IPreferencesRepository preferencesRepository,
    IReportCommandAndQueryContextRepository reportCommandAndQueryContextRepository,
    IMyNewRepository myNewRepository,  // ← NOUVEAU
    // ... autres dépendances
) : base()
{
    this.myNewRepository = myNewRepository;
    // ... autres assignments
}
```

2. L'utiliser dans l'enregistrement :
```csharp
implementationsDictionary["MaFonction"] =
    () => new MaFonctionParameter(myNewRepository);
```

### Étape 6.3 : Mise à jour de Parameters.cs

**Localisation :**
```
repos/ReportFoundations/ReportImplementations/Implementations/Reports/
[Catégorie]/[NomDuRapport]/Parameters.cs
```

**Trouver le paramètre existant :**
```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_GainLossCostDisplayed))
{
    WindowOrder = 3,
    Position = 2,
    PositionH = 1,
    ValidationFunction = "",  // ← Peut être vide ou contenir un nom
});
```

**Ajouter la propriété `ValueProviderFunction` :**
```csharp
this.AddParameter(new ParameterJoinEntity(
    this.GlobalProviders.Parameters.GetEntity(Params.PARAM_GainLossCostDisplayed))
{
    WindowOrder = 3,
    Position = 2,
    PositionH = 1,
    ValidationFunction = "",
    ValueProviderFunction = "InitGainLossCostDisplayed"  // ← AJOUTER ICI
});
```

**⚠️ Important :** Le nom dans `ValueProviderFunction` doit correspondre EXACTEMENT à la clé dans `implementationsDictionary`.

### ValidationFunction vs ValueProviderFunction

Il existe 2 façons de définir la logique d'un paramètre :

| Approche | Quand l'utiliser | Exemple |
|----------|------------------|---------|
| `ValidationFunction` + `InitialValue` | Valeur statique simple | `ValidationFunction = "CheckTrue", InitialValue = "1"` |
| `ValueProviderFunction` | Logique dynamique (dépend de contexte) | `ValueProviderFunction = "InitGainLossCost"` |
| Les deux | Valeur par défaut + logique custom | `ValidationFunction = "X", ValueProviderFunction = "Y"` |

**Arbre de décision :**

```
Votre fonction retourne-t-elle TOUJOURS la même valeur ?
  ↓ OUI
  → ValidationFunction + InitialValue hardcodé
  → Pas besoin de créer un Parameter !

  ↓ NON - La valeur dépend de :
    • Préférences
    • Type de source (Pad)
    • Autres paramètres
    • Base de données
  → ValueProviderFunction
  → Créer un IValueProvidedParameter
```

---

## Étape 7 : Tests

### 🎯 Objectif
Garantir que votre implémentation fonctionne correctement et couvre tous les cas.

### Structure des tests

**Localisation :**
```
ReportManagerAPI.Infrastructure.SmallTests/Repositories/ValueProviderFunctions/Parameters/
├── [NomFonction]ParameterTests.cs
├── Hidden/
└── Date/
```

### Template de test complet

```csharp
using FluentAssertions;
using Moq;
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Repositories;
using ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters;
using Xunit;

namespace ReportManagerAPI.Infrastructure.SmallTests.Repositories.ValueProviderFunctions.Parameters
{
    public class MonFonctionParameterTests
    {
        // Mocks des dépendances
        private readonly IPreferencesRepository preferencesRepository;

        public MonFonctionParameterTests()
        {
            // Initialiser les mocks
            preferencesRepository = Mock.Of<IPreferencesRepository>();
        }

        [Fact]
        public void GivenPreferenceIsYes_WhenProvideValueCalled_ThenReturnsOne()
        {
            // Arrange
            var preferencesRepositoryMock = Mock.Get(preferencesRepository);
            preferencesRepositoryMock
                .Setup(x => x.GetPreference("PREF_DISPLAY_CHECK_DIGIT"))
                .Returns(new Preference
                {
                    Name = "PREF_DISPLAY_CHECK_DIGIT",
                    Value = "YES"
                });

            var parameter = new MonFonctionParameter(preferencesRepository);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act
            var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

            // Assert
            result.Should().NotBeNull();
            result.InitialValue.Should().Be("1");

            // Vérifier que la préférence a bien été appelée
            preferencesRepositoryMock.Verify(
                x => x.GetPreference("PREF_DISPLAY_CHECK_DIGIT"),
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

            var parameter = new MonFonctionParameter(preferencesRepository);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act & Assert
            Assert.Throws<Exception>(() =>
                parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm));
        }

        [Theory]
        [InlineData("YES", "1")]
        [InlineData("NO", "0")]
        [InlineData("yes", "1")]  // Case insensitive
        [InlineData(null, "0")]
        public void GivenVariousPreferenceValues_WhenProvideValue_ThenReturnsExpectedValue(
            string prefValue,
            string expectedResult)
        {
            // Arrange
            var preferencesRepositoryMock = Mock.Get(preferencesRepository);
            preferencesRepositoryMock
                .Setup(x => x.GetPreference("PREF_DISPLAY_CHECK_DIGIT"))
                .Returns(prefValue == null ? null : new Preference
                {
                    Name = "PREF_DISPLAY_CHECK_DIGIT",
                    Value = prefValue
                });

            var parameter = new MonFonctionParameter(preferencesRepository);
            var reportParameterMetaData = new ReportParameterMetaData();
            var reportMetaDataFromRtm = new ReportMetaDataFromRtm();

            // Act
            var result = parameter.ProvideValue(reportParameterMetaData, reportMetaDataFromRtm);

            // Assert
            result.InitialValue.Should().Be(expectedResult);
        }
    }
}
```

### Scénarios de tests minimaux

Pour chaque parameter, testez au minimum :

1. ✅ **Cas nominal** - Valeurs correctes retournées
2. ✅ **Cas d'erreur** - Préférence/donnée manquante → Exception
3. ✅ **Valeurs limites** - YES/NO, 0/1, null, chaînes vides
4. ✅ **Combinaisons** - Si plusieurs préférences, tester les combinaisons
5. ✅ **Effets de bord** - Si `VisibleOnUi`, `EnabledOnUi`, ou `return null` sont utilisés

### Exécution des tests

```bash
cd ../monolith/CFF/Products/ReportManagerApi

# Tous les tests
dotnet test

# Tests d'une classe spécifique
dotnet test --filter "FullyQualifiedName~MonFonctionParameterTests"

# Avec couverture de code
./show-code-coverage.cmd
```

**✅ Critère de succès :** Tous les tests passent en vert !

---

## Exemples complets de A à Z

Cette section présente 4 migrations complètes, du niveau débutant au niveau avancé.

### 🌟 Exemple 1 : Cas ultra-simple (5 minutes)

**Fonction :** `SinceInception`

#### Ce qu'on migre

Un paramètre checkbox qui est toujours coché par défaut.

#### Code C++ (validation_check.c:644)

```c
void C_VALIDATION_CHECK::InitSinceInceptionCheck(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_WINDOW_PARAM_GROUP_CHECK *pGroup = (C_WINDOW_PARAM_GROUP_CHECK *) in_pGroup;
    C_ATTRIBUTE *pAtt = pGroup->GetValue();
    if (pAtt == NULL)
    {
        return;
    }

    pGroup->Select(true);  // ← LA SEULE LIGNE IMPORTANTE !
}
```

#### Analyse rapide

- ✅ Fonction < 15 lignes
- ✅ Une seule action : `Select(true)`
- ✅ Aucune préférence, aucun GetPad()
- ✅ **Niveau 1 - Trivial**

#### Implémentation C#

**Option choisie :** Utiliser `TrueParameter` (déjà existant)

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs
implementationsDictionary["SinceInception"] = () => new TrueParameter();
```

**C'est tout !** Pas besoin de créer une nouvelle classe.

#### Tests

Les tests de `TrueParameter` existent déjà. Aucun test additionnel requis.

#### Temps réel : 5 minutes ✅

---

### 🌟🌟 Exemple 2 : Cas simple avec condition (1 heure)

**Fonction :** `InitDefaultIndex`

#### Ce qu'on migre

Un paramètre checkbox qui se comporte différemment selon le type de source :
- Si **Portfolio** : décoche et désactive
- Sinon : coche

#### Code C++ (validation_check.c:789)

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
            // Portfolio : décocher et désactiver
            pGroup->Select(false);
            pGroup->Enable(false);
            pAtt->SetValue("0");
        }
        else
        {
            // Autres : cocher
            pGroup->Select(true);
            pAtt->SetValue("1");
        }
    }
}
```

#### Analyse

- ✅ Un seul `if/else`
- ✅ Condition sur `GetPad()`
- ✅ Deux `SetValue` possibles
- ✅ **Niveau 2 - Simple**
- **Dépendances :** `SourceTypes` (type de source)

#### Implémentation C#

**Fichier :** `ReportManagerAPI.Infrastructure/.../Parameters/InitDefaultIndexParameter.cs`

```csharp
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Models.ReportGeneration.IncomingGenerationRequest;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters
{
    /// <summary>
    /// Initialise PARAM_DefaultIndices selon le type de source.
    /// Si Portfolio : décoche et désactive, sinon : coche.
    ///
    /// Migré depuis : validation_check.c:789 - InitDefaultIndexCheckTrue
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
                parameter.EnabledOnUi = false;  // Désactivé (grisé)
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

#### Enregistrement

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs
implementationsDictionary["InitDefaultIndex"] =
    () => new InitDefaultIndexParameter(
        reportCommandAndQueryContextRepository.RequestSourceType);
```

#### Tests

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

#### Temps réel : 52 minutes ✅

- Localisation code C++ : 5 min
- Analyse : 5 min
- Création fichier Parameter : 15 min
- Enregistrement : 2 min
- Tests unitaires : 20 min
- Validation : 5 min

---

### 🌟🌟🌟 Exemple 3 : Piège de complexité apparente (30 minutes)

**Fonction :** `Period1`

#### Ce qu'on migre

Un paramètre pour sélectionner une période de performance (3 mois, 6 mois, etc.).

#### Code C++ (validation_combo.c:1020)

```c
void C_VALIDATION_COMBO::InitPeriod1(C_WINDOW_PARAM_GROUP *in_pGroup)
{
    C_WINDOW_PARAM_GROUP_COMBO *pGroup = (C_WINDOW_PARAM_GROUP_COMBO *)in_pGroup;

    InitPeriod(pGroup, GetPeriodNotFixed("3"), 0);
}
```

**🤔 Réflexe initial :** "Il faut migrer `InitPeriod` et `GetPeriodNotFixed` aussi !"

#### Investigation de la helper function

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

**💡 Observation :** Toute cette logique est de la **configuration d'interface** (C++ desktop), pas de la logique métier !

#### Analyse

Dans le nouveau système web :
- L'UI est gérée par le frontend React/Angular
- Les choix disponibles sont déjà définis ailleurs
- On a juste besoin de la **valeur par défaut**

**Simplification :** `InitPeriod1` retourne simplement "3" (3 mois)

#### Implémentation C#

```csharp
// Dans PreParamEntryValueProviderFunctionsExecuter.cs
implementationsDictionary["Period1"] = () => new StringParameter("3");
implementationsDictionary["Period2"] = () => new StringParameter("6");
implementationsDictionary["Period3"] = () => new StringParameter("12");
implementationsDictionary["Period4"] = () => new StringParameter("36");
implementationsDictionary["Period5"] = () => new StringParameter("-1");  // Since Inception
```

#### Leçon apprise

🎓 **Ne migrez pas aveuglément toute la logique C++ !**
Une fonction C++ de 50 lignes peut se réduire à une valeur statique en C#.

**Différenciez :**
- **Logique UI** (configuration de widgets) → Ignorer
- **Logique métier** (la valeur elle-même) → Migrer

#### Temps réel : 30 minutes ✅

- Lecture code C++ complexe : 10 min
- Analyse de la helper function : 10 min
- Décision de simplification : 5 min
- Implémentation : 5 min

**Temps économisé :** 2-3h en évitant de tout migrer !

---

### 🌟🌟🌟 Exemple 4 : Pattern spécial GetBoolFromPref (45 minutes)

**Fonction :** `GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)`

#### Ce qu'on migre

Un paramètre caché qui lit une préférence pour déterminer si on doit masquer la devise dans le rapport.

#### Particularité du pattern SQL

**Dans le CSV :**
```csv
Default_Function: GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
```

**⚠️ Attention :** Le nom de la préférence est **dans la fonction** elle-même !

**Décomposition :**
- **Fonction :** `GetBoolFromPref` (générique)
- **Préférence :** `PREF_REPORT_HIDE_CURRENCY` (entre parenthèses)

#### Code C++ (générique - validation_hided.c)

```c
void C_VALIDATION_HIDED::GetBoolFromPrefFunction(C_WINDOW_PARAM_GROUP *in_pGroup)
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

**Logique :** Si préférence = "YES" → retourne "1", sinon "0"

#### Implémentation C#

**Fichier :** `ReportManagerAPI.Infrastructure/.../Parameters/Hidden/GetBoolFromPrefReportHideCurrencyParameter.cs`

```csharp
using ReportManagerAPI.Domain.Models;
using ReportManagerAPI.Domain.Repositories;
using Serilog;

namespace ReportManagerAPI.Infrastructure.Repositories.ValueProviderFunctions.Parameters.Hidden
{
    /// <summary>
    /// Retourne "1" si PREF_REPORT_HIDE_CURRENCY = "YES", sinon "0".
    ///
    /// Pattern SQL : GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
    /// </summary>
    public class GetBoolFromPrefReportHideCurrencyParameter : IValueProvidedParameter
    {
        private const string PreferenceKey = "PREF_REPORT_HIDE_CURRENCY";
        private readonly IPreferencesRepository _preferencesRepository;
        private static ILogger Logger => Log.Logger.ForContext<GetBoolFromPrefReportHideCurrencyParameter>();

        public GetBoolFromPrefReportHideCurrencyParameter(IPreferencesRepository preferencesRepository)
        {
            _preferencesRepository = preferencesRepository;
        }

        public ReportParameterMetaData ProvideValue(
            ReportParameterMetaData parameter,
            ReportMetaDataFromRtm reportMetaDataFromRtm)
        {
            var preference = _preferencesRepository.GetPreference(PreferenceKey);

            if (preference == null)
            {
                Logger.Error("Preference {PreferenceName} not found", PreferenceKey);
                throw new Exception($"Preference {PreferenceKey} not found");
            }

            parameter.InitialValue = preference.Value?.ToUpper() == "YES" ? "1" : "0";

            return parameter;
        }
    }
}
```

#### Convention de nommage

**Pattern :**
```
GetBoolFromPref(PREF_REPORT_HIDE_CURRENCY)
                     ^^^^^^^^^^^^^^^^^^^
                     ReportHideCurrency
```

**Nom de la classe :**
```
GetBoolFromPref + ReportHideCurrency + Parameter
= GetBoolFromPrefReportHideCurrencyParameter
```

**Règle :** Enlever `PREF_`, convertir en PascalCase, préfixer `GetBoolFromPref`, suffixer `Parameter`

#### Enregistrement

```csharp
// Dans PostParamEntryValueProviderFunctionsExecuter.cs
implementationsDictionary["GetBoolFromPrefReportHideCurrency"] =
    () => new GetBoolFromPrefReportHideCurrencyParameter(preferencesRepository);
```

#### Tests

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
        string prefValue,
        string expectedResult)
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

#### Template réutilisable

**Bonne nouvelle :** Si vous avez 10 fonctions `GetBoolFromPref(PREF_XXX)`, vous pouvez :
1. Copier ce fichier
2. Renommer la classe
3. Changer `PreferenceKey`
4. Copier les tests

**Temps par fonction additionnelle :** 15 minutes

**Temps total pour 10 fonctions :** 45min + (9 × 15min) = 3h45min

#### Temps réel : 44 minutes ✅

---

## Patterns de transformation courants

### Tableau de correspondance C++ → C#

| C++ | C# | Notes |
|-----|-----|-------|
| `pAtt->SetValue("1")` | `parameter.InitialValue = "1"` | Définir la valeur |
| `pGroup->Select(true)` | `parameter.InitialValue = "1"` | Cocher checkbox |
| `pGroup->Enable(false)` | `parameter.EnabledOnUi = false` | Désactiver (grisé) |
| `pGroup->SetHideWidgetFlag(true)` | `parameter.VisibleOnUi = false` | Cacher |
| `GetCresusConfig()->get("PREF_XXX")` | `_preferencesRepository.GetPreference("PREF_XXX")` | Lire préférence |
| `GetPad() == REPORT_CLIENT` | `_requestSourceType == SourceTypes.Client` | Type de source |
| `sPref == "YES"` | `pref?.Value?.ToUpper() == "YES"` | Comparaison (case insensitive) |
| `sPref.CompareCaseInsensitive("YES") == 0` | `pref?.Value?.ToUpper() == "YES"` | Même chose |

### Types de sources (Pad)

| C++ | C# |
|-----|-----|
| `REPORT_CLIENT` | `SourceTypes.Client` |
| `REPORT_ACCOUNT` | `SourceTypes.Account` |
| `REPORT_PORTEF` | `SourceTypes.Portfolio` |
| `REPORT_RELATIONSHIP` | `SourceTypes.Relationship` |

---

## Troubleshooting et FAQ

### ❓ Le paramètre ne s'affiche pas

**Checklist :**
1. ✅ Vérifié que `ValueProviderFunction` est bien défini dans `Parameters.cs`
2. ✅ Vérifié que le nom dans `implementationsDictionary` correspond exactement
3. ✅ Vérifié que la fonction ne retourne PAS `null` (ce qui supprime le paramètre)
4. ✅ Vérifié que `VisibleOnUi` n'est PAS à `false`
5. ✅ Ajouté du logging pour voir si la fonction est appelée

### ❓ Le build échoue

**Causes courantes :**
- Namespace incorrect dans votre nouveau fichier Parameter
- Dépendance manquante dans le constructeur de l'executer
- Using manquant en haut du fichier

**Solution :** Comparez avec un parameter similaire existant.

### ❓ Les tests échouent

**Vérifications :**
- Le mock retourne-t-il bien une valeur ?
- La préférence mockée a-t-elle le bon nom ?
- Les assertions correspondent-elles à la logique ?

**Astuce :** Ajoutez des `Debug.WriteLine()` dans vos tests pour voir les valeurs.

### ❓ Préférence toujours null

**Causes possibles :**
- Nom de la préférence incorrect (typo)
- Préférence inexistante dans la base de données
- Repository mal injecté

**Solution :**
```csharp
if (preference == null)
{
    Logger.Error("Preference {PreferenceName} not found", PreferenceKey);
    throw new Exception($"Preference {PreferenceKey} not found");
}
```

### ❓ Je ne trouve pas le code C++

**Essayez :**
1. Recherche par fragments du nom
2. Recherche par nom du paramètre (PARAM_XXX)
3. Recherche dans tout ReportApi : `grep -rn "FunctionName" Src/ReportApi/`
4. Demandez à un collègue qui connaît bien le legacy

### ❓ La fonction C++ est trop complexe (100+ lignes)

**Approche :**
1. Identifiez les parties UI vs logique métier
2. Cherchez les `SetValue` - ce sont les valeurs importantes
3. Créez un service Domain si la logique est vraiment complexe
4. Documentez bien votre implémentation
5. Prévoyez 2-4h minimum pour ce type de fonction

---

## Checklist finale de migration

### Pour chaque paramètre :

- [ ] Fonction C++ localisée et documentée (fichier + ligne)
- [ ] Complexité évaluée (Niveau 0-4)
- [ ] Dépendances identifiées (repositories requis)
- [ ] Implémentation C# créée (Parameter ou helper class)
- [ ] Logique C++ → C# transformée correctement
- [ ] Enregistré dans executer (ordre alphabétique !)
- [ ] `ValueProviderFunction` ajouté dans `Parameters.cs`
- [ ] Tests unitaires écrits et **passent en vert** ✅
- [ ] Logging ajouté (erreurs critiques minimum)
- [ ] Code review fait par un collègue

### Pour le rapport complet :

- [ ] Tous les paramètres du CSV traités
- [ ] Aucun `UnimplementedParameter()` sans justification
- [ ] Build réussit : `dotnet build`
- [ ] Tests réussissent : `dotnet test`
- [ ] Code coverage > 80% sur les nouveaux fichiers
- [ ] Documentation de migration mise à jour
- [ ] PR créée avec description détaillée
- [ ] Template de rapport testé localement

---

## Bonnes pratiques à retenir

### ✅ DO (À faire)

- ✅ Utilisez `GetPreference(string)` pour UNE préférence
- ✅ Utilisez `GetPreferencesValue(List<string>)` pour PLUSIEURS préférences
- ✅ Loggez toujours les erreurs critiques (préférence manquante)
- ✅ Définissez les constantes : `private const string PreferenceKey = "PREF_XXX"`
- ✅ Documentez la source C++ dans les commentaires
- ✅ Écrivez les tests AVANT ou PENDANT l'implémentation
- ✅ Simplifiez la logique UI complexe (ne migrez que le métier)
- ✅ Utilisez TrueParameter/FalseParameter/StringParameter pour les cas simples

### ❌ DON'T (À éviter)

- ❌ Ne copiez pas les patterns obsolètes du code existant
- ❌ N'oubliez jamais la validation null sur les préférences
- ❌ Ne hardcodez pas de "valeurs magiques" sans constantes
- ❌ Ne migrez pas aveuglément toute la logique C++ (surtout l'UI)
- ❌ N'inventez pas une nouvelle classe Parameter si une helper existe
- ❌ Ne négligez pas les tests
- ❌ Ne mettez pas de logique métier complexe dans un Parameter (créez un service)

---

## Ressources et références

### Documentation interne

- [MIGRATION_PROCEDURE.md](./MIGRATION_PROCEDURE.md) - Version technique détaillée
- [CLAUDE.md](./CLAUDE.md) - Instructions générales du projet
- [BusinessBrowserWebApi](../monolith/README.BusinessBrowserWebApi.md)
- [Contributing](../monolith/CONTRIBUTING.md)

### Code snippets

- `MyCustomSnippets.code-snippets` → `ivalueProvidedParameter`

### PRs de référence

- **PR #5972** - Gains et Pertes Non Réalisés (GP_NON_REALISE)
- **PR #6155** - Fix pour GP_NON_REALISE

### Outils utiles

```bash
# Chercher dans le code C++
grep -rn "FunctionName" repos/CroesusServer/Src/ReportApi/

# Compter les SetValue dans une fonction
sed -n '789,850p' validation_check.c | grep -c "SetValue"

# Trouver toutes les préférences utilisées
grep -o 'PREF_[A-Z_]*' validation_check.c | sort -u

# Exécuter tests avec filtre
dotnet test --filter "FullyQualifiedName~MonParameterTests"
```

---

## En cas de blocage

**N'hésitez pas à :**
1. Demander de l'aide à un collègue
2. Chercher des examples similaires dans le code existant
3. Consulter la PR #5972 pour voir des exemples concrets
4. Créer un TODO bien documenté si vraiment bloqué
5. Documenter votre blocage dans le fichier de migration

**Remember :** Même les experts ont dû apprendre ! Prenez votre temps, comprenez la logique, et n'hésitez pas à simplifier.

---

**Bonne migration ! 🚀**

*Dernière mise à jour : 2025-11-17*
*Créé pour : Développeurs humains migrant des rapports C++ → C#*
