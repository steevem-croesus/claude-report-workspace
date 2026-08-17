# Conventions & références du monolithe (`doc/references`)

Le dépôt monolithe CFF/PM tient une **bibliothèque de références curées** décrivant ses conventions de
code et son architecture. Elle vit **hors** des symlinks `repos/` de ce workspace, à un chemin absolu :

- **Windows / Read** : `C:\Repos\monolith\doc\references\`
- **bash** : `/c/Repos/monolith/doc/references/`

C'est la **source de vérité** pour *comment écrire du code dans le monolithe* et pour *comprendre le
système* qui entoure le pipeline de rapports. Tout agent qui génère, révise ou explique du code touchant
au monolithe (ReportManagerApi, ReportFoundations, CroesusServer, ReportServer, et le reste de CFF/PM)
doit s'y référer. Les docs sont en anglais ; ce workspace reste en français — c'est normal.

> Ces docs se déclarent eux-mêmes « curated, not exhaustive ». Traite-les comme faisant autorité là où ils
> parlent, mais si le code réel les contredit, fais confiance au code et signale l'écart.

## Chaîne de précédence (quand deux règles se contredisent)

1. Le **`CLAUDE.md` / `copilot-instructions.md` propre au repo cible** (ex. `repos/ReportManagerApi/copilot-instructions.md`,
   `repos/pf-web/CLAUDE.md`) — prime toujours pour le travail repo-local.
2. Ces **conventions du monolithe** ci-dessous — avec une nuance : pour les **fichiers ORM**, les conventions
   de `croesus-orm/conventions.md` **priment** sur les règles C# générales (le doc le dit explicitement).
3. Les indications génériques (Clean Code, bon sens).

---

## A. Conventions de code — à APPLIQUER à tout code généré

À lire/appliquer dès que tu écris ou révises du C# (ou que tu touches au build) dans le monolithe.

| Doc | Quand la lire / ce qu'elle impose |
|---|---|
| `coding-conventions-csharp.md` | **Toujours, pour tout C#.** Clean Code, `var` quand le type est apparent, méthodes de service qui renvoient `Result<T>` (`.Succeeded`/`.Status`/`.Data`/`.Messages`), **pas** de préfixe `_` sur les champs privés, et le **StyleCop restrictive ruleset** (`CFF/SupportFiles/CodeAnalysis/Croesus_Restrictive.ruleset`) où tout `Action="Error"` est obligatoire. Règles souvent ratées : SA1101 (`this.`), SA1122 (`string.Empty` pas `""`), SA1503 (accolades toujours), SA1512/SA1515/SA1516 (blank lines), Serilog004 (templates constants, pas d'interpolation) / Serilog006 (PascalCase). Désactivées : SA1200, SA1201-1206 (ordre), SA1600-1652 (doc XML), SA1633-1643 (file headers). |
| `appservice-conventions.md` | Avant d'ajouter/modifier un **AppService** sous `CFF/Products/`. |
| `central-package-management.md` | Avant d'ajouter/mettre à jour un **package NuGet** : CPM — versions centralisées dans `Directory.Packages.props`, jamais de version dans les `.csproj`. |
| `nuke-build-reference.md` | Pour **builder** le monolithe ou comprendre la CI : commandes Nuke exécutées depuis `CFF/`, entrée `CFF/Build/Build.cs`. |
| `code-signing-reference.md` | Seulement pour du **packaging/signature** (`CroesusClient.exe`, `.exe.manifest`, `.application`). |

### ORM Croesus — `croesus-orm/` (référence de la skill `croesus-orm`)

À lire dès que tu crées/modifies une classe ORM (BO, CompositeBusinessObject, Repository, Flex, FlexScenario).
La skill `croesus-orm` pilote déjà ce workflow ; ces docs sont sa référence détaillée.

| Doc | Objet |
|---|---|
| `croesus-orm/conventions.md` | **Conventions de fichiers & de code ORM — priment sur les règles C# générales pour les fichiers ORM.** À lire en premier. |
| `croesus-orm/concept.md` | Concepts noyau (BO, CBO, Flex, Repository, Implementer, Serializer). |
| `croesus-orm/ddl-to-csharp-mapping.md` | Mapping d'un `CREATE TABLE` (DDL) → Implementer → type C#, colonne par colonne. |
| `croesus-orm/composite-bo-patterns.md` | Patterns CompositeBusinessObject (vanilla et Flex). |
| `croesus-orm/repository-patterns.md` | Patterns Repository (`RepositoryBase` vanilla vs `FlexRepository`). |
| `croesus-orm/flex-collections.md` | Collections 1-to-many (satellite) sur un CBO Flex. |
| `croesus-orm/flex-scenario-tests.md` | Tests de FlexScenarios via le harness `RecordingFlexBuilder`. |

---

## B. Références d'architecture — pour COMPRENDRE le système

À lire pour se construire un modèle mental avant de planifier/investiguer/enseigner. Ordonné par pertinence
pour le **pipeline de rapports**.

| Zone | Docs | Ce que ça couvre |
|---|---|---|
| **ReportServer** (moteur C++ de génération) | `report-server/` — `README`, `concept`, `external-interface`, `tasks`, `dataset-construction`, `namevalue-resolution`, `affinity-and-state`, `business-templates`, `theme-composition`, `report-generator-handoff` | **Le plus pertinent.** Comment une demande devient un rapport rendu : API XML-RPC, session par worker, `B_RPT_TASK`/batches, construction du dataset, résolution des NameValue, affinité vers un module AgentServer stateful, composition du thème, handoff vers ReportGenerator (service Java Crystal). |
| **RTM** (Report Template Manager) | `rtm/` — `README`, `concept`, `entry-points`, `execution-steps`, `report-class-structure`, `shared-definitions`, `subreports`, `tables`, `template-lifecycle`, `localized-text` | **Très pertinent.** Comment les déclarations C# des rapports deviennent des lignes DB + binaires compilés que ReportServer/ReportGenerator consomment : structure des classes de rapport, définitions partagées, subreports, cycle de vie des templates, texte localisé (messages). |
| **FrameworkServer** | `frameworkserver-worker-architecture.md` | FrameworkServer ↔ FrameworkWorker et le pooling de connexions — le Frameworkserver joint sur le **port 8999** du pipeline. |
| **AgentServer** | `agent-server/` — `README`, `concept`, `agent-registration`, `task-definitions`, `affinity`, `uma-sleeves` | Le process C# CFF qui expose les opérations métier comme des **tâches** (action IDs) ; enregistrement/dispatch des agents, modules **stateful** + affinity ID, sourcing de données UMA/sleeves. |
| **CoreApi** | `core-api/` — `README`, `concept`, `logical-model`, `canvas-and-data-tree`, `load-paths`, `calculated-fields`, `agent-server-load` | Le C++ (PM) qui bâtit un **data tree** en mémoire depuis SQL ou une tâche AgentServer ; modèle logique, load paths, champs calculés (`_V`). |
| **Loader** | `loader-architecture.md` | Carte globale du Loader C++ (`PM/Products/Loader`). |
| **Recalc** | `recalc-lifecycle.md` | Cycle de reprocessing : `TRANS_RECALC_DATE` & `RECALC_MODE`. |
| **UMA** | `uma-allocator.md` | Nouveau moteur d'allocation de transactions UMA (PF-19489 / PF-19350). |

---

## Comment s'en servir (par rôle d'agent)

- **planner / implementer / cpp-to-csharp-porter** — avant d'écrire du C#, applique la **section A** (surtout
  `coding-conventions-csharp.md` + le ruleset StyleCop, et `croesus-orm/` pour tout fichier ORM). Le repo-local
  `copilot-instructions.md` reste prioritaire.
- **explorer / investigator / learning-guide** — utilise la **section B** pour ancrer le modèle mental du
  pipeline (ReportServer, RTM, FrameworkServer) au lieu de tout redériver du code brut ; cite le doc de référence
  à côté du `repo/path:line`.
- **reviewer** — vérifie la conformité à la **section A** (violations StyleCop `Action="Error"`, `Result<T>`
  manquant, champs préfixés `_`, interpolation dans les logs Serilog) comme des constats à part entière.
