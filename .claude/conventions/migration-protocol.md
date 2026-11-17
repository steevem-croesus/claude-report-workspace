# Protocole de migration (fondation partagée)

Ce fichier est la **fondation commune** à tous les agents de migration (`../agents/`). Il décrit le
pipeline, comment les agents/skills/commandes s'articulent, les chemins canoniques, la gestion d'état,
les commandes de build/test et les règles git. Les conventions **métier** (backend/frontend) vivent
dans `backend-conventions.md` et `frontend-conventions.md`. Voir le `../../CLAUDE.md` racine pour
l'architecture et la stack.

> **Langue :** ce projet est développé par une équipe francophone. **Toute communication à
> l'utilisateur se fait en français.** Les seuls termes anglais tolérés sont les noms techniques
> (`ValidationFunction`, `InitialValue`, `ValueProviderFunction`, Widget, Observer pattern…) et les
> extraits de code.

## Le pipeline de migration

Migrer un rapport de Conseiller (C++ legacy) vers Xpert (C#/Angular) suit **quatre phases**, chacune
portée par un agent dédié (dispatché via l'outil Agent). `→` est une phase.

> **analyse → backend → frontend → validation** (+ **revue** à la demande)

| # | Phase | Agent | Écrit / produit | Modifie du code ? |
|---|---|---|---|---|
| 1 | Analyse | [`report-analyst`](../agents/report-analyst.md) | `.work/{slug}/analysis.md` (spec) | ✗ (lecture seule) |
| 2 | Backend | [`backend-migrator`](../agents/backend-migrator.md) | code C# + tests, `migration-log-backend.md` | ✏️ |
| 3 | Frontend | [`frontend-migrator`](../agents/frontend-migrator.md) | composant Angular + e2e, `migration-log-frontend.md` | ✏️ |
| 4 | Validation | [`migration-validator`](../agents/migration-validator.md) | `migration-log-validation.md` | ✗ |
| — | Revue (optionnel) | [`migration-reviewer`](../agents/migration-reviewer.md) | findings de revue | ✗ |

L'analyse n'est pas toujours nécessaire : pour un rapport simple, `backend-migrator` fait sa propre
analyse inline. Utiliser `report-analyst` quand on veut une spec revue avant d'implémenter, ou pour
estimer/planifier.

### Lancer une phase

Demander en langage naturel (« migre le backend de FOREIGN_PROPERTY ») — l'assistant principal
dispatche l'agent correspondant — ou passer par `/feature` en mode migration. Les skills de migration
sous `.claude/skills/` servent d'outils aux agents.

## Les skills (outils des agents)

Les agents n'exécutent pas tout eux-mêmes : ils **dispatchent les skills** de `../skills/` et **lisent**
les fichiers de référence de `reference/` (documentation, pas des skills). Ordre type d'utilisation
(analyse + backend) :

1. `locate-report-classes` — trouver RPT_*, la hiérarchie, les `Parameters.cs`
2. `extract-parameters` — extraire les paramètres depuis `docs/fields.csv`
3. `classify-functions` — Default/Specific, PRE/POST
4. `locate-cpp-function` — localiser le C++ dans `validation_*.c`
5. `analyze-cpp-function` — analyser logique + dépendances
6. `check-implementation` — vérifier si déjà implémenté en C#
7. lire `reference/generic-functions-reference.md` — hiérarchie de décision (déclaratif vs custom)
8. `implement-report-parameters` / `implement-declarative-radio` — implémenter
9. `register-parameter` / `register-web-report` / `register-ignore-id-masking` — enregistrer
10. `estimate-complexity` — support

Références à lire au besoin (sous `reference/`) : `implementation-guide.md` (9 patterns de classes VPF),
`read-cpp-patterns.md` (lecture rapide du C++), `migration-examples.md` (4 migrations commentées),
`best-practices-analyst.md` (qualité d'une spec de migration).

Le frontend utilise en plus : `get-template-id`, `compare-report-params` (validation).

## Chemins canoniques (⚠️ utiliser les symlinks du workspace)

**Toujours** travailler via les symlinks à la racine du workspace — jamais des chemins absolus vers
d'autres clones. Certaines anciennes commandes référençaient `c:/Repos/claude-pf-web` et
`c:/Repos/claude-monolith/…` : **ces chemins n'existent pas ici**. Les chemins corrects sont :

| Rôle | Symlink workspace | Cible réelle |
|---|---|---|
| Source C++ (lecture seule) | `repos/CroesusServer/` | `/c/Repos/monolith/PM/Products/CroesusServer` |
| Fondations C# | `repos/ReportFoundations/` | `/c/Repos/monolith/CFF/ReportFoundations` |
| API C# (cible) | `repos/ReportManagerApi/` | `/c/Repos/monolith/CFF/Products/ReportManagerApi` |
| Frontend Angular | `repos/pf-web/` | `/c/Repos/pf-web` |

Emplacements clés :
- **C++ validation** (par paramètre) : `repos/CroesusServer/Src/ReportApi/ReportCtr/ReportCtrParam/validation_*.c`
- **C++ Observer** (inter-champs) : `repos/CroesusServer/Src/ReportApi/ReportView/ReportViewParam/win_prm_grp_*.c`
- **VPF C#** : `repos/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/` (`Hidden/`, `Date/`, `String/`)
- **Executers** : `.../ValueProviderFunctions/Pre|PostParamEntryValueProviderFunctionsExecuter.cs`
- **Parameters.cs du rapport** : `repos/ReportFoundations/ReportImplementations/Implementations/Reports/…/Parameters.cs`
- **Implémentations génériques** : `repos/ReportFoundations/…/Parameters/SpecificTypes/*ParametersImplementation.cs`
- **Frontend templates** : `repos/pf-web/libs/report/domain-view/generate/src/lib/generator/report-templates/templates/`

Mapping Widget → fichier C++ :

| WIDGET_TYPE | ENTRY | Fichier `validation_*.c` |
|---|---|---|
| 1 Combo | PRE | `validation_combo.c` |
| 2 Radio | PRE | `validation_radio.c` |
| 3 Check | PRE | `validation_check.c` |
| 4 List | PRE | `validation_list.c` |
| 5 Date | PRE | `validation_date.c` |
| 7 String | PRE | `validation_file.c` |
| 8 Hidden | POST | `validation_hided.c` |
| 9 MultiLang | PRE | `validation_multilang_textbox.c` |

## Détection des dépendances (C++ → repository C#)

| Signal C++ | Injecter |
|---|---|
| `PREF_` / `GetCresusConfig()->get()` / `HasPref*()` | `IPreferencesRepository` |
| `PARAM_` / `GetParam()` | `IReportCommandAndQueryContextRepository` |
| Dates / périodes | `IParameterDateValueService` / `IDateTimeService` |
| `GetPad()` (type de source) | `SourceTypes` (injection constructeur) |
| Répartitions | `IRepartitionRepository` |
| Transactions | `ITransactionsRepository` |
| Codes industrie | `IIndustryCodeRepository` |
| Indices | `IIndexesRepository` |

## Gestion d'état et livrables

- **Répertoire de tâche (`.work/{slug}/`) — RÈGLE FERME.** TOUS les livrables d'une migration vivent
  sous `.work/{slug}/` à la racine du workspace (non versionné) — on ne **travaille** jamais directement sous
  `docs/reports/`, qui est une archive (voir ci-dessous). C'est la convention
  de répertoire de tâche du workspace (voir `protocol.md`), partagée avec `/feature`. Créer le dossier
  si absent : `mkdir -p .work/{slug}`.
  - **`{slug}`** = la **clé du ticket Jira** si un ticket est fourni (p. ex. `RPT-20590`), **sinon** le
    **nom interne du rapport** (p. ex. `FOREIGN_PROPERTY`). Un seul dossier par migration.
- **Livrables canoniques** sous `.work/{slug}/` :
  - `analysis.md` (spec du `report-analyst`) + artefacts intermédiaires éventuels
    (`analysis-extraction.md`, `analysis-classification.md`).
  - `migration-log-{backend,frontend,validation}.md` (journaux `--log`) et les PDF générés.
  - `review.md` (audit `migration-reviewer`) et le rapport du `migration-validator`.
- **Données globales — NE PAS déplacer :** `docs/fields.csv` (liste maître des paramètres) et
  `docs/template_ids.csv` restent sous `docs/` ; ce sont des **entrées partagées**, pas des livrables.
- **Journaux (`--log`) :** chaque phase peut produire un journal détaillé en français sous
  `.work/{slug}/`, puis un PDF via `docs/scripts/log-to-pdf.mjs` → `.work/{slug}/{Phase}.pdf`.
- **Archive versionnée (`docs/reports/{REPORT_NAME}/`) :** une fois la migration terminée, copier dans
  `docs/reports/{REPORT_NAME}/` les **livrables finaux à conserver dans git** (`analysis.md`,
  `migration-log-*.md`) — sur demande de l'utilisateur, jamais automatiquement. Rien d'autre n'y va :
  pas de brouillon, pas de review intermédiaire, pas de PDF.
- **Reprise :** pas de fichier d'état dédié — une migration interrompue reprend en relisant les artefacts
  de `.work/{slug}/` (`task.md`, `analysis.md`, `build-summary.md`).

## Build & tests

```bash
# Backend (C#)
cd ReportManagerApi && dotnet build ReportManagerAPI.sln
dotnet test ReportManagerAPI.Infrastructure.SmallTests/ReportManagerAPI.Infrastructure.SmallTests.csproj

# Frontend (Angular / NX)
cd pf-web && npx nx build report-view-generate 2>&1 | tail -5
# ou vérification TypeScript seule :
npx tsc --noEmit -p libs/report/domain-view/generate/tsconfig.lib.json 2>&1 | tail -10
```

Les agents qui modifient du code **doivent** builder + exécuter les tests concernés avant de conclure,
et rapporter les résultats réels (jamais « vert » sans avoir exécuté).

## Git (monolith)

- Gitflow + Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`). Voir le
  `../../CLAUDE.md` racine.
- Les agents `git add`-stagent mais **ne committent pas** sauf demande explicite ; le commit/PR est
  une étape finale séparée.
- Ne jamais laisser une nouvelle branche suivre un ref protégé : brancher avec `--no-track`, premier
  push avec `git push -u`.

## Garde-fous (tous les agents, toutes les phases)

- **Jamais** de CLI interdit par l'organisation (`aws`, `terraform`/`tofu`, wrappers `assume`/`granted`).
- Le C++ (`repos/CroesusServer/`) est **lecture seule** — source de vérité, pas une cible de modification.
- Ne jamais modifier une `ValidationFunction` existante dans `Parameters.cs` (voir backend-conventions).
- Ne jamais inventer de traductions .resx / i18n — chercher les valeurs réelles ou demander.
- Respecter le `CLAUDE.md` / `copilot-instructions.md` de chaque repo — ils priment sur l'avis générique.

## Protocole HALT (agent → assistant principal)

Un agent producteur (analyst, backend, frontend) peut s'arrêter et retourner un bloc HALT sur une
vraie décision utilisateur (ex. fonction C++ introuvable, sémantique ambiguë, template ID manquant) :

```
HALT: décision utilisateur requise
Raison : <pourquoi je ne peux pas continuer>
Question : <la question précise>
Défaut proposé : <recommandation>
État : <progression, pour reprendre>
```

Ne pas deviner une logique financière/date ambiguë. Plafond : 3 allers-retours HALT par agent.
