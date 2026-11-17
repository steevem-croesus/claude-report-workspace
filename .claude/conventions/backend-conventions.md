# Conventions backend (C# — ReportManagerApi / ReportFoundations)

Base de connaissances backend pour la migration des paramètres C++ → C#. C'est la **source de
vérité** pour `backend-migrator` (et `migration-reviewer`). Le pipeline et les chemins sont dans
`migration-protocol.md`.

## Classification en 8 catégories (A–A', B–F)

Pour **chaque paramètre**, déterminer une catégorie qui dicte l'action :

| Cat. | Situation | Action |
|---|---|---|
| **A** | Déjà géré par le framework (config complète dans `*ParametersImplementation.cs`) | Vérifier + **commentaire seul** |
| **A'** | Config incomplète (validationFunction 4e positionnel existe, mais pas de `initialValue:` ni `valueProviderFunction:` explicite) | Compléter dans `Parameters.cs` + commentaire |
| **B** | Le C++ set une **constante** | `InitialValue = "valeur"` |
| **C** | Le C++ lit **une préférence** | `InitialValueFromPref = "PREF_XXX"` |
| **D** | Une classe VPF **existe déjà** | `ValueProviderFunction = "Func"` + **valider C# vs C++** (obligatoire) |
| **E** | Radio/Combo à valeurs fixes | Config déclarative dans `*ParametersImplementation.cs` + traductions |
| **F** | Logique **complexe/dynamique** non couverte | Créer classe VPF + tests + enregistrement |

Règle Default vs Specific : **`Specific_Function` a toujours priorité** sur `Default_Function`. En cas
de conflit apparent (ex. `CheckTrue` vs `CheckFalse`), lire le C++ pour comprendre, privilégier
Specific, documenter l'anomalie.

Fonctions génériques triviales (pas besoin de lire le C++) : `CheckTrue`→"1", `CheckFalse`→"0",
`PureValueZero`→"0", `PureValueMinusOne`→"-1", `WhiteSpace`→" ". Helpers préfabriqués (dossier
`Parameters/String/`) : `StringParameter("x")`, `TrueParameter`, `FalseParameter`, `EmptyParameter`,
`VoidParameter` — les utiliser au lieu de créer une classe pour les cas triviaux.

## `ValidationFunction` vs `ValueProviderFunction` vs `InitialValue`

- **Ne jamais confondre** le **4e paramètre positionnel** (`validationFunction`, = nom de la fonction
  C++ par défaut) avec le **named parameter** `valueProviderFunction:`. **Seul le named parameter est
  utilisé par le framework C#.**
- Valeur statique / fonction générique → `ValidationFunction` + `InitialValue` hardcodé.
- Logique dynamique (préférences multiples, pad, contexte) → `ValueProviderFunction` + classe VPF
  enregistrée dans l'executer (Pre pour PRE, Post pour POST).
- **Séparateur de listes : C++ `,` → C# `|`** dans les `InitialValue`.
- **Ne JAMAIS modifier une `ValidationFunction` existante** : elle reflète la config d'origine et sert
  d'autres contextes (Conseiller desktop). On **ajoute** des propriétés (`ValueProviderFunction`,
  `InitialValue`…), on ne remplace pas l'existant.
- ⚠️ **Une `ValidationFunction` présente ne veut PAS dire que la VPF C# est enregistrée.** Un
  `ValidationFunction="Xxx"` (ou une clé `vpf:...` dans un `*ParametersImplementation.cs`) peut exister
  alors qu'**aucune classe VPF n'est enregistrée** dans l'executer → **la clé est ignorée en silence à la
  génération** (`AbstractValueProviderFunctionsExecuter.Execute` renvoie le paramètre intact : le build et
  les tests unitaires passent, la valeur calculée par le C++ n'est jamais produite). Toujours grepper les **deux** executers
  (`Pre`/`Post`) pour chaque clé touchée avant le build : `bash .claude/scripts/check-vpf-registration.sh --changed`. Ex. vécu
  RPT-18883 : `CostCalculation` référencée mais jamais enregistrée (aucune classe) — bombe à retardement.

### Commentaire obligatoire en 3 parties (sur CHAQUE paramètre)

1. **PRE/POST + Widget type**
2. **Config du `*ParametersImplementation.cs`** — inclure `validationFunction: "X"` (4e positionnel)
   quand non-vide, puis les named params (`initialValue:`, `valueProviderFunction:`,
   `initialValueFromPref:`, `possibleValues:`, `possibleDisplayValues:`) ou leur absence.
3. **Vulgarisation du C++** — ce que fait la fonction en français simple ; si constante, le dire ; si
   introuvable, « à investiguer ».

```csharp
// Config complète (pas besoin de C++)
ValidationFunction = ""
// POST Hidden. In HiddenParametersImplementation.cs: validationFunction: "GetFirmCurrency", initialValue: "CAD", valueProviderFunction: "FirmCurrency".

// InitialValue basé sur le C++ — inclure la valeur C++ originale + conversion , → |
InitialValue = "PSA_V_AccId|PSR_V_StartingMarketValue|PSP_V_Description"
// POST Hidden. In HiddenParametersImplementation.cs: no initialValue, no valueProviderFunction.
// C++ SummaryPortDataEntryPoint: set "PSA_V_AccId,PSR_V_StartingMarketValue,PSP_V_Description" (converti , → |).
```

Ne PAS ajouter d'`InitialValue` redondant si le `*ParametersImplementation.cs` a déjà un
`initialValue:` explicite qui couvre le comportement C++ — documenter dans le commentaire à la place.

## Catégorie D — valider les VPF existantes contre le C++ (OBLIGATOIRE)

Ne jamais réutiliser une VPF existante sans lire **le code C# ET le code C++** et comparer point par
point : mêmes conditions/branches, mêmes préférences, **même format de parsing**, même défaut en cas
d'erreur, même résultat. Si divergence → classer **⚠️ VPF DIVERGENTE**, corriger la classe C# + tests,
la lister dans le résumé.

> Exemple vécu : `GPCanUseLastYearParameter` parsait `PREF_REPORT_GL_UNTIL_DATE` avec
> `DateTime.TryParse()` alors que le C++ parse un format « mois.jour » (« 3.31 ») et compare mois/jour
> séparément — résultats C# complètement faux.

### Audit « fonction C++ à appelants multiples » — après tout fix de fidélité

Corriger **une** VPF ne clôt pas la famille. Quand la fonction C++ portée appelle un **helper partagé**
(`Check*Configuration`, `Get*ForCfg`, etc.), avant de considérer le sujet clos :

1. Grep le helper sur **tout le monolith** (pas seulement `repos/CroesusServer`) pour lister ses
   appelants C++.
2. Pour chaque appelant, retrouver la VPF C# mappée via la clé string du `Init()` de `validation_*.c`,
   et vérifier qu'elle porte **toutes** les branches — pas seulement le repli.
3. Traiter tout `TODO` renvoyant vers un symbole C++ comme un **défaut ouvert**, pas une note.
4. Se méfier d'une VPF dont le nom promet plus que le corps ne fait.

> Exemple vécu : RPT-20533 a corrigé la lecture de `END_DATE_FUNCTION` sur
> `LastQuarterEndDateDisableParameter` (port de `FinDernierTrimestreDisable`). Mais
> `CheckEndDateConfiguration` (`validation_date.c:1591`) a **deux** appelants ; le second,
> `FinDernierMoisMaxDernierTraitement` (`:1307`), est resté cassé et est devenu RPT-20575 deux mois plus
> tard. Un seul grep des appelants aurait fermé les deux d'un coup.

**Classe de bug à connaître — portage partiel masqué par une valeur par défaut coïncidente** : la VPF
n'a porté que la branche de *repli* du C++ en la transformant en chemin unique, et l'écart est resté
invisible pendant des années parce que la config semée par défaut produisait numériquement la même date
que le calcul codé en dur. « Aucun écart observé » n'est donc **pas** une preuve de fidélité.

## Créer une classe VPF (catégorie F)

- Nom : `<FunctionName>Parameter`, implémente `IValueProvidedParameter`, méthode `ProvideValue(...)`.
  Snippet `ivalueProvidedParameter`.
- Placement : `Parameters/` (général), `Parameters/Hidden/` (POST), `Parameters/Date/` (dates).
- **La classe Parameter ne contient AUCUN `if`, calcul, ni appel `DateTime` (hors `Parse`/`ToString`).**
  Toute logique de date va dans `IDateTimeService`/`DateTimeService` (+ tests `DateTimeServiceTests`).
  Vérifier d'abord si la méthode existe (`GetFirstDayOfYear`, `GetEndDateOfLastQuarter`…).
- Tests : hériter de `ValueProvidedParameterTestBase`, **minimum 3 cas** (normal, edge, null/invalide),
  couvrir les edge cases C++.
- Enregistrer dans le **bon** executer (Pre/Post selon `PARAMETER_ENTRY_TYPE`), **ordre alphabétique**.
- Ajouter aussi `ValueProviderFunction = "Func"` dans `Parameters.cs` pour chaque paramètre concerné.
- **Éviter `UnimplementedParameter`** (no-op qui perd la logique C++) — acceptable seulement si un
  repository/service requis n'existe pas encore ; alors documenter explicitement ce qui manque.

## Checklist avant build (vérifier explicitement, grep/read)

**Enregistrements**
- [ ] `WebRTMRunner.cs` → `RPT_{Name}.ReportName` dans `ConstructSupportedWebReportList` (alpha).
- [ ] `GetDisplayUnmaskedIdParameter.cs` → si `PARAM_IgnoreIdMasking`, nom interne dans
  `ReportsWithInitialValueZero` + `InlineData` dans les tests (skill `register-ignore-id-masking`).
- [ ] Chaque `ValueProviderFunction` de `Parameters.cs` est enregistrée dans l'executer **approprié**.

**Parameters.cs**
- [ ] Chaque paramètre a le commentaire 3 parties.
- [ ] Séparateur `,` → `|` vérifié dans les listes `InitialValue`.
- [ ] Chaque `Specific_Function` analysée (C++ lu ou impl existante vérifiée).
- [ ] Radio/Combo avec `Specific_Function` → clés `PossibleDisplayValues`/`InitialValue` correspondent
  à celles utilisées par la classe C# du VPF ; sinon override dans `Parameters.cs`.
- [ ] Paramètres **List (Widget 4)** → `InitialValue = " "` (un espace) obligatoire (évite le stripping).

**Logique dynamique / classes custom**
- [ ] Tout paramètre à logique dynamique C++ a une VPF qui la reproduit (pas juste une constante).
- [ ] Catégorie D validée C# vs C++, divergences corrigées.
- [ ] Chaque nouvelle classe a ≥ 3 tests + est enregistrée + a `ValueProviderFunction` dans Parameters.cs.
- [ ] Aucune logique de date inline dans une classe Parameter (extraite dans `DateTimeService`).

**Vérifs automatiques (exécuter avant le build)**
```bash
# UnimplementedParameter ajoutés ?
grep -n "UnimplementedParameter" repos/ReportManagerApi/.../Pre*Executer.cs repos/ReportManagerApi/.../Post*Executer.cs
# Logique inline dans les nouvelles classes ?
for f in $(git diff --name-only --diff-filter=A -- "*/ValueProviderFunctions/Parameters/*.cs" | grep -v Tests); do
  grep -n "if \|if(\|switch\|DateTime\.\(Now\|Today\|DaysInMonth\|AddDays\|AddMonths\|AddYears\)" "$f" | grep -v "DateTime.Parse\|\.ToString"; done
# Chaque VPF référencée est-elle enregistrée ? (code retour 1 s'il en manque)
bash .claude/scripts/check-vpf-registration.sh --changed        # fichiers modifiés
bash .claude/scripts/check-vpf-registration.sh --where <Clé>   # Pre ou Post ?
```

## Conventions apprises (issues des revues)

### Classes Date (`Parameters/Date/`)
- **Dual-constructor** : défaut avec `DateTimeFormat.REPORT_SERVER_STANDARD` + un constructeur avec
  format custom (ex. `EndOfLastMonthDateMaxLastProcessDateParameter`).
- Dépendances minimales : `IParameterDateValueService` + `string dateTimeFormat` suffisent souvent.
- **Format PRE vs POST** : VPF de date **PRE** (visibles frontend) → `DateTimeFormat.API_LONG_DATE_STANDARD`
  (`yyyy-MM-dd`, attendu par le date picker Angular) ; VPF **POST** → `REPORT_SERVER_STANDARD`
  (`yyyy.MM.dd`). Dans le `PreParamEntryExecuter`, passer explicitement `API_LONG_DATE_STANDARD`.
- **Batch-aware (OBLIGATOIRE) — décorateur `BatchStartOverride`/`BatchEndOverride`** : si le C++ de la
  fonction de date utilise `SetGetValue(GetBatchStartDate)` ou `SetGetValue(GetBatchEndDate)` (getter
  batch-aware), la VPF C# **doit** être enveloppée dans le décorateur correspondant à l'enregistrement
  dans l'executer — pas seulement instanciée directement. Sinon la valeur n'est pas surchargée par la
  date de batch en génération en lot.
  - `GetBatchEndDate` → `BatchEndOverride(new XxxParameter(...))`
  - `GetBatchStartDate` → `BatchStartOverride(new XxxParameter(...))`
  - Modèle (comme `LastQuarterEndDate`, `EndOfLastMonthDateMaxLastProcessDate`, `PerfEndDate`, etc.) :
    ```csharp
    implementationsDictionary["EndOfLastQuarter"] = () =>
        BatchEndOverride(new EndOfLastQuarterParameter(parameterDateValueService, dateTimeService, DateTimeFormat.API_LONG_DATE_STANDARD));
    ```
  - Vérification lors de l'analyse C++ : lire le bloc de dispatch `else if (in_sFunction == "...")` dans
    `validation_date.c` et repérer la ligne `SetGetValue(...)`. `GetBatchStartDate`/`GetBatchEndDate` →
    batch-aware ; `GetDate`/`GetDisplayDate` seuls → pas de décorateur batch.
- Toute logique de dates dans `IDateTimeService`, jamais inline. Ne pas sur-traduire le C++ (clamping
  DPH, FirmStartDate, PREF_USE_REALTIME, logique UI) — simplifier côté web.
- Toujours lire 2-3 classes existantes du même dossier avant d'en créer une.

### Checkbox
- Chaque checkbox dans `CheckBoxParametersImplementation.cs` **DOIT** avoir `initialValue: "0"`/`"1"` et
  `possibleValues: new List<string>() { "0", "1" }` — sinon exception runtime. Ajouter si legacy manquant.

### Radio/Combo déclaratifs
- Valeurs fixes → `RadioParametersImplementation.cs`/`ComboParametersImplementation.cs` avec
  `initialValue`, `possibleValues`, `possibleDisplayValues` — **pas de classe custom**.
- Chercher les paramètres dans **tout** le dossier du rapport (Base + Standard/Simple).
- Quand `Specific_Function` ≠ `Default_Function`, les clés du `*ParametersImplementation.cs` peuvent ne
  pas matcher celles du VPF Specific → **overrider** `InitialValue`, `PossibleDisplayValues` ET
  `ValueProviderFunction` dans `Parameters.cs`. Inclure **toutes** les valeurs possibles (même celles
  filtrées dynamiquement, ex. `PERSONNAL_ASSETMIX_REPAR`). Toujours lire un rapport déjà migré qui
  utilise le même VPF pour copier les mêmes valeurs.
- `PARAM_AssetMixRepartType` a **6 patterns distincts** (AssetMixRadioButton, SimpleAssetMixRadioButton,
  PerfHistoAssetMixRadioButton, AssetMixSleeves, IAVMAssetMixRadBut, UseFBNGP1859Repartition) — vérifier
  lequel s'applique ; Simple/PerfHisto exigent un override complet.

### Autres
- **Résoudre les `#define` C++** : utiliser la valeur résolue (`"FPR_V_Region"`), pas le nom du define
  (`SORT_ON_FIELD_FORPROP_REGION`). Chercher dans les `.h` (souvent `win_prm_const.h`).
  - **Si introuvable dans `repos/CroesusServer/Src`** : scanner le dossier **`PM/Foundations/`** du monolith
    (`../monolith/PM/Foundations/`), notamment **`BusinessLogic/Api/BusinessLogicDefs.h`** — beaucoup de
    constantes métier partagées (descriptions de répartitions, types, etc.) y sont définies hors du
    symlink `CroesusServer`. Commande type :
    `grep -rn "define NOM_DU_DEFINE" ../monolith/PM/Foundations/`.
  - Exemple résolu : `DESC_REPARTITION_GP1859` = `"Allocation - 1859"`, `DESC_REPARTITION_MATURITY` =
    `"Allocation - Maturity"` (`BusinessLogicDefs.h`).
- **IsReadOnly/Disable** : si la fonction C++ fait `SetEnable(false)`/`SetReadOnly(true)`/contient
  « Disable », le VPF C# doit setter `parameter.IsReadOnly = true` (classe dédiée, ne pas réutiliser une
  VPF qui ne gère que la valeur). **Corollaire : si le C++ ne le fait pas, le VPF ne doit PAS le
  setter** — deux VPF frères portant deux fonctions C++ voisines peuvent diverger sur ce seul point
  (ex. `FinDernierTrimestreDisable` → `IsReadOnly = true` vs `FinDernierMoisMaxDernierTraitement` →
  rien ; RPT-20575).
  - **Piège de test symétrique** : pour asserter qu'un VPF ne pose **pas** `IsReadOnly` (ou toute autre
    propriété publique settable du DTO), poser explicitement la valeur opposée **en Arrange** avant
    d'appeler le SUT, puis asserter `Should().BeFalse()`. Sans cet Arrange, `AutoFixture`/`AutoMoq`
    peuple la propriété avec une valeur arbitraire et l'assertion ne prouve rien.
- **Ordre d'exécution des VPF PRE** : ils s'exécutent dans l'ordre d'`AddParameter()`. Si une VPF de
  date lit un checkbox (ex. `PARAM_UseLastYear`) qui apparaît après elle dans la liste, ajouter
  `InitialValue = "1"` sur le checkbox (réf. GL Realized).
- **Accès niveau utilisateur** : injecter `IHttpContextAccessor` et lire le claim
  `http://croesus.org/claims/accesslevel` directement (jamais `SessionClaim` dans un VPF) ; null-safety
  (`HttpContext?.User` peut être null en batch) + `InitialValue` de fallback.
- **Config absente = exception** : `IConfigRepository.GetPreferenceValue("KEY")` peut **lancer** si la
  clé n'existe pas → try-catch en plus du null check pour les configs optionnelles.
- **Clés .resx** : nouvelles clés préfixées `RPT_mgr_` (pas `CRESUS_rpt_`), sans référence à Croesus.
- **Traductions** : ne JAMAIS inventer — chercher dans la localisation C++
  (`repos/CroesusServer/Src/**/*.properties`, `*.rc`, `*.msg`) ou demander les valeurs exactes affichées dans
  Conseiller. Les acronymes diffèrent entre langues (« PIMG » EN → « GGPP » FR).

## Anti-patterns
1. Créer une classe pour un pattern déclaratif (InitialValue/InitialValueFromPref).
2. Oublier le séparateur `,` → `|`.
3. Oublier `WebRTMRunner` (le rapport n'apparaît pas dans Xpert).
4. Oublier les traductions (3 fichiers .resx : en, fr, neutre).
5. Casser l'ordre alphabétique (WebRTMRunner, executers, GetDisplayUnmaskedId).
6. `UnimplementedParameter` par facilité.
7. Logique de dates dans une classe Parameter.
8. Faire confiance aveuglément à une VPF existante (cat. D).
9. Utiliser un nom de `#define` comme valeur.
10. Inventer des traductions .resx.