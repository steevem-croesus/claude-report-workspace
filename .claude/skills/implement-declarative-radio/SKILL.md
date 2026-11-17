---
name: implement-declarative-radio
description: Implémente un paramètre radio button ou combobox déclaratif (valeurs fixes + défaut) découvert dans le C++. Configure RadioParametersImplementation.cs ou ComboParametersImplementation.cs, ajoute les traductions .resx, et documente dans Parameters.cs. Aucune classe custom nécessaire.
allowed-tools: Read, Edit, Grep, Glob, Bash
---

# Skill: Implement Declarative Selection Parameter (Radio / Combo)

Implémente un paramètre radio button ou combobox (dropdown) purement déclaratif à partir de l'analyse d'une fonction C++.

**Utilisé par:** report-developer (après analyze-cpp-function)

---

## Quand utiliser ce skill

**Indicateurs:**
- L'analyse C++ révèle un paramètre de type radio button (WidgetTypes.RadioButton) ou combobox (WidgetTypes.Combo)
- Les valeurs possibles sont **fixes** (pas de logique dynamique, pas d'appel repository)
- Une valeur est désignée comme défaut
- Chaque valeur a un label à afficher (traduit EN/FR)

**Ne PAS utiliser si:**
- Les valeurs sont dynamiques (chargées depuis BD, préférences, ou conditions) → utiliser `.claude/conventions/reference/implementation-guide.md` Pattern 7
- Le paramètre nécessite un filtrage conditionnel → classe custom requise
- Le paramètre n'est ni un radio button ni un combobox

---

## Input

L'utilisateur fournit:
- **Nom du paramètre**: Ex: `PARAM_NameFormat`, `PARAM_SortBy`
- **Nom de la fonction C++**: Ex: `NameFormat`, `AssetsUnderMgtSortByCombo`
- **Type de widget**: Radio ou Combo (déduire du WIDGET_TYPE dans fields.csv: 1=Combo, 2=Radio)
- **Valeurs possibles**: Liste des valeurs avec celle par défaut identifiée
- **Labels d'affichage**: Texte EN et FR pour chaque valeur
- **ID du rapport** (optionnel): Pour localiser Parameters.cs

Si l'utilisateur ne fournit pas toutes les informations, les déduire de l'analyse C++ ou demander.

---

## Déterminer le fichier cible

| WIDGET_TYPE | Type | Fichier |
|-------------|------|---------|
| 1 | Combo (dropdown) | `ComboParametersImplementation.cs` |
| 2 | Radio button | `RadioParametersImplementation.cs` |

Les deux fichiers sont dans:
```
repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/
```

Le pattern est identique pour les deux — même `ParameterEntity` avec `initialValue`, `possibleValues`, `possibleDisplayValues`. Seul le `WidgetTypes` diffère.

---

## Étape 1: Vérifier l'état actuel

### 1.1 Vérifier le fichier d'implémentation

```bash
grep -n "PARAM_NomParametre" repos/ReportFoundations/ReportImplementations/Implementations/Parameters/SpecificTypes/{Radio|Combo}ParametersImplementation.cs
```

Vérifier si le paramètre existe déjà et s'il est déjà configuré avec `initialValue`/`possibleValues`.

### 1.2 Vérifier les traductions existantes

```bash
grep -n "CLÉ_TRADUCTION" repos/ReportFoundations/ReportBusinessLogic/Resources/Resource.en.resx
```

---

## Étape 2: Configurer l'implémentation

### 2.1 Modifier la ligne AddData existante

**Avant (typique):**
```csharp
this.AddData(new ParameterEntity(Params.PARAM_NomParametre, "", "", "NomFonction", WidgetTypes.RadioButton, ""));
```

**Après:**
```csharp
this.AddData(new ParameterEntity(Params.PARAM_NomParametre, "", "", "NomFonction", WidgetTypes.RadioButton, "",
    initialValue: "VALEUR_DEFAUT",
    possibleValues: new List<string> { "VALEUR_1", "VALEUR_2" },
    possibleDisplayValues: new Dictionary<string, string> { { "VALEUR_1", "CLÉ_TRADUCTION_1" }, { "VALEUR_2", "CLÉ_TRADUCTION_2" } }));
```

Pour un Combo, même pattern mais avec `WidgetTypes.Combo`.

### 2.2 Cas spécial Combo: PossibleDisplayValues dans Parameters.cs

Pour les combobox, les `PossibleDisplayValues` peuvent aussi être configurés directement dans le `Parameters.cs` du rapport au lieu du fichier d'implémentation générique. Vérifier si d'autres rapports utilisent le même combobox — si oui, configurer dans `ComboParametersImplementation.cs`. Si c'est spécifique à un seul rapport, configurer dans `Parameters.cs`:

```csharp
this.AddParameter(new ParameterJoinEntity(this.GlobalProviders.Parameters.GetEntity(Params.PARAM_SortBy))
{
    WindowOrder = 1,
    Position = 5,
    PositionH = 1,
    ValidationFunction = "AssetsUnderMgtSortByCombo",
    InitialValue = "AUM_LongName",
    PossibleDisplayValues = new Dictionary<string, string>() { { "AUM_LongName", "PARAM_AUM_LongName" }, { "AUM_Id", "PARAM_AUM_Id" }, { "AUM_TotalValue", "PARAM_AUM_TotalValue" } }
});
```

### 2.3 Convention de nommage des clés de traduction

Suivre le pattern existant dans le fichier. Patterns courants:
- Radio: `RPT_mgr_prm_radio_sec_{Groupe}_{Valeur}`
- Combo: `RPT_mgr_prm_combo_prm_{Groupe}` ou `PARAM_{Valeur}`

Consulter les entrées existantes dans le fichier d'implémentation pour identifier le pattern de nommage approprié.

---

## Étape 3: Ajouter les traductions

### 3.1 Fichiers à modifier

Les 3 fichiers de ressources sont dans:
```
repos/ReportFoundations/ReportBusinessLogic/Resources/
├── Resource.resx      (clés neutres, valeur vide)
├── Resource.en.resx   (anglais)
└── Resource.fr.resx   (français)
```

### 3.2 Format d'insertion

**Resource.resx** (avant `</root>`):
```xml
  <data name="CLÉ_TRADUCTION_1" xml:space="preserve">
    <value />
  </data>
  <data name="CLÉ_TRADUCTION_2" xml:space="preserve">
    <value />
  </data>
```

**Resource.en.resx** (avant `</root>`):
```xml
  <data name="CLÉ_TRADUCTION_1" xml:space="preserve">
    <value>English Label 1</value>
  </data>
  <data name="CLÉ_TRADUCTION_2" xml:space="preserve">
    <value>English Label 2</value>
  </data>
```

**Resource.fr.resx** (avant `</root>`):
```xml
  <data name="CLÉ_TRADUCTION_1" xml:space="preserve">
    <value>Label français 1</value>
  </data>
  <data name="CLÉ_TRADUCTION_2" xml:space="preserve">
    <value>Label français 2</value>
  </data>
```

### 3.3 Vérification post-insertion

```bash
grep "CLÉ_TRADUCTION" repos/ReportFoundations/ReportBusinessLogic/Resources/Resource.*.resx
```

S'assurer que chaque clé apparaît dans les 3 fichiers.

---

## Étape 4: Documenter dans Parameters.cs du rapport

### 4.1 Localiser le fichier

Utiliser le skill `locate-report-classes` ou:
```bash
find -L ReportFoundations -name "Parameters.cs" -path "*{REPORT_ID}*" 2>/dev/null
```

### 4.2 Ajouter le commentaire

Sur le paramètre concerné, ajouter un commentaire confirmant l'approche déclarative:

```csharp
this.AddParameter(new ParameterJoinEntity(this.GlobalProviders.Parameters.GetEntity(Params.PARAM_NomParametre))
{
    WindowOrder = 7,
    Position = 5,
    PositionH = 2,
    ValidationFunction = ""
    // No ValueProviderFunction needed, InitialValue and PossibleValues are set in RadioParametersImplementation.
});
```

Pour un Combo, adapter le commentaire: `...set in ComboParametersImplementation.` ou `...set directly in this Parameters.cs.`

---

## Étape 5: Vérification

### 5.1 Ce qui NE doit PAS être fait

- ❌ Créer une classe `IValueProviderParameter`
- ❌ Enregistrer dans Pre/PostParamEntryValueProviderFunctionsExecuter
- ❌ Écrire des tests unitaires (rien de custom à tester)
- ❌ Ajouter un `ValueProviderFunction` dans Parameters.cs

### 5.2 Checklist finale

- [ ] Fichier d'implémentation modifié (`RadioParametersImplementation.cs` ou `ComboParametersImplementation.cs`) avec `initialValue`, `possibleValues`, `possibleDisplayValues`
- [ ] OU `PossibleDisplayValues` configuré directement dans `Parameters.cs` (cas Combo spécifique à un rapport)
- [ ] Traductions ajoutées dans `Resource.resx`, `Resource.en.resx`, `Resource.fr.resx`
- [ ] Chaque clé de traduction présente dans les 3 fichiers
- [ ] Commentaire ajouté dans `Parameters.cs` du rapport (si applicable)
- [ ] Aucune classe custom créée
- [ ] Aucun enregistrement dans les executers

---

## Rapport de fin

Fournir:
1. **Paramètre**: Nom et fonction C++ source
2. **Type**: Radio ou Combo
3. **Valeurs**: Liste des valeurs possibles avec défaut identifié
4. **Traductions**: Clés ajoutées avec valeurs EN/FR
5. **Fichiers modifiés**: Liste des fichiers touchés
6. **Complexité**: Niveau 0 — déclaratif pur

---

## Référence

**Implémentation de référence (Radio):** `PARAM_NameFormat` dans RPT-18494 (commit `58cd1e8860`)
- Fonction C++: `NameFormat`
- Valeurs: `AUM_ShortName` (défaut), `AUM_LongName`
- Fichier: `RadioParametersImplementation.cs`

**Implémentation de référence (Combo):** `PARAM_SortBy` dans RPT-18494 (commit `58cd1e8860`)
- Fonction C++: `AssetsUnderMgtSortByCombo`
- Valeurs: `AUM_LongName` (défaut), `AUM_Id`, `AUM_TotalValue`
- Fichier: `Parameters.cs` (PossibleDisplayValues directement dans le rapport)

**Skills connexes:**
- `analyze-cpp-function` — pour découvrir les valeurs dans le C++
- `.claude/conventions/reference/generic-functions-reference.md` — pour confirmer que l'approche déclarative est la bonne
- `classify-functions` — pour identifier le type de widget
