# Comment porter une fonction de rapport C++ vers C#

Objectif : réimplémenter une fonction de rapport C++ (issue de `CroesusServer` **ou** de `ReportServer`) en tant que
`IValueProviderParameter` C# dans `ReportManagerApi`. C'est la tâche cross-repo la plus récurrente du workspace,
et elle a un agent dédié : [`cpp-to-csharp-porter`](../reference/agents.md#cpp-to-csharp-porter).

**Recette faisant autorité :** [`repos/ReportManagerApi/copilot-instructions.md`](../../repos/ReportManagerApi/copilot-instructions.md).
Ce guide vous oriente ; ce fichier est la source de vérité pour les dossiers et l'enregistrement.

## Quand utiliser quel point d'entrée

- **À l'intérieur d'un feature/bug** — le workflow `feature`/`bug` dépêche automatiquement
  `cpp-to-csharp-porter` (au lieu de l'`implementer` générique) quand une étape de plan est un port de value-provider.
  Vous n'avez rien de spécial à faire.
- **Autonome** — dépêchez l'agent directement (ou décrivez la tâche de port) quand tout le travail *est* un
  port.

## Ce que fait le porter (pour que vous puissiez vérifier son travail)

1. **Trouve & confirme la source C++.** Cherche dans **les deux** `repos/CroesusServer/Src/` et
   `repos/ReportServer/Src/` — la fonction peut se trouver dans l'un ou l'autre — la lit entièrement, et énonce sa
   sémantique (entrées, sorties, cas limites, et surtout le calcul de dates/périodes) avec le `repo/path:line`
   d'où elle provient.

2. **Choisit les dépendances injectées à partir des signaux C++ :**

   | Signal C++ | Injecter |
   |---|---|
   | `PREF_` / preference / config | `IPreferencesRepository` |
   | `PARAM_` / parameter | `IReportCommandAndQueryContextRepository` |
   | logique de date / période | `IParameterDateValueService` / `IDateTimeService` |
   | repartitions | `IRepartitionRepository` |
   | transactions | `ITransactionsRepository` |
   | industry codes | `IIndustryCodeRepository` |
   | indexes | `IIndexesRepository` |

3. **Crée la classe de paramètre** `<FunctionName>Parameter` avec une méthode `ProvideValue`, placée dans :
   - général/pre : `ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/`
   - liée aux dates : `.../Parameters/Date/`

4. **L'enregistre — par ordre alphabétique —** dans l'executer correspondant :
   - pre : `PreParamEntryValueProviderFunctionsExecuter.cs`
   - post : `PostParamEntryValueProviderFunctionsExecuter.cs`
   sous la forme `implementationsDictionary["<FunctionName>"] = () => new <FunctionName>Parameter();`

5. **Ajoute des helpers de date** à `IDateTimeService` (Domain) + `DateTimeService.cs` si de nouvelles opérations de date sont
   nécessaires.

6. **Écrit des tests (obligatoire)** en miroir du style `GetStartYearFromSelectedYMParameter`, couvrant les
   cas limites C++ — tests de paramètre sous `ReportManagerAPI.Infrastructure.SmallTests/...` et
   tests du service de date dans `ReportManagerAPI.Domain.SmallTests/Services/DateTimeServiceTests.cs`.

7. **Construit et teste** avant de retourner :
   `dotnet build /c/Repos/monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.sln` + `dotnet test <the *.SmallTests project>`.

## Ce qu'il faut revérifier en tant que reviewer/approbateur

- **Fidélité.** Le C# doit correspondre à la sémantique du C++. Toute divergence délibérée doit être signalée
  explicitement avec la ligne source — le [`reviewer`](../reference/agents.md#reviewer) signale les divergences
  silencieuses comme must-fix.
- **La bonne interface de repository injectée** (selon la table ci-dessus).
- **Enregistrement alphabétique** dans le bon executer pre/post.
- **Cas limites couverts** — surtout les bornes de date/période (passage d'année, fiscal vs calendaire).

Si le porter ne peut pas trouver la fonction, que la sémantique est ambiguë, ou que la bonne interface de
repository n'est pas claire, il **HALT** et demande plutôt que de deviner une logique financière/de date.

## Référence

- Les indices de mapping sont aussi résumés dans le [`CLAUDE.md`](../../CLAUDE.md) racine.
- Spécification de l'agent : [`.claude/agents/cpp-to-csharp-porter.md`](../../.claude/agents/cpp-to-csharp-porter.md)
