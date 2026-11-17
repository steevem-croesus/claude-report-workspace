# Référence — Gates & protocole

La fondation partagée sur laquelle chaque workflow s'appuie. **Source faisant autorité :**
[`.claude/conventions/protocol.md`](../../../.claude/conventions/protocol.md).

## Protocole de gate (interactif)

Ce workspace fonctionne en mode **gated**. À chaque gate, l'orchestrateur s'arrête et te demande (via une
invite à choix multiple) : *approve / request changes / cancel*.

- **approve** → passer à la phase suivante.
- **request changes** → ton retour est écrit verbatim dans
  `.work/<slug>/_signals/revision-request.md` ; l'agent de la phase est re-dispatché (il lit son artefact
  précédent + la demande de révision) ; puis tu reviens au même gate avec l'artefact révisé.
- **cancel** → arrêter le workflow.

L'orchestrateur **ne dépasse jamais un gate automatiquement.** Les deux gates universels sont le **gate de plan**
(après `plan.md`) et le **gate de code** (après `build-summary.md` + `review-code.md`). Certains workflows
ajoutent le leur (le gate de *décision* du spike).

## Le gate de plan — la barre de build

Le gate de plan a une condition d'entrée supplémentaire, non négociable. `plan.md` porte un en-tête :

```
**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
```

Échelle : **F < D < C < B < A < S**. Le workflow ne peut builder **que** depuis un plan qui est **`ready`** *et*
noté **A ou S**.

- **`draft` ou en dessous de A** → le gate n'offre **pas** *approve*. Il fait remonter le grade + les bloqueurs
  (questions ouvertes, points de décision `needs-user`) et route vers **request changes** (re-dispatcher le
  planner) ou **cancel**.
- **`ready` + A/S** → *approve / changes / cancel* normal. Un grade qualifiant *débloque* le gate ; il
  ne le passe pas automatiquement — l'approbation reste requise.
- **Override** → tu peux approuver explicitement un plan sous la barre (p. ex. un changement délibérément minuscule).
  L'override est enregistré dans `revision-request.md` pour être auditable. En l'absence d'un override explicite, la
  barre tient.

Le barème est détenu par [`planner.md`](../../../.claude/agents/planner.md) ; guide pratique :
[faire passer un plan au gate](../how-to/pass-the-plan-gate.md) ; justification :
[gates & la barre de build](../explanation/gates-and-the-build-bar.md).

## Le gate de code

Après build + review, présenter le verdict du reviewer + le résultat de `build-summary.md`. *approve /
changes / cancel*. **changes** (ou tout constat `must-fix`) reboucle vers build contre la review —
plafonné à **3 itérations build↔review**, après quoi le workflow s'arrête et rapporte les problèmes restants.

## Protocole HALT (agent → orchestrateur)

Tout agent producteur (planner, implementer, porter, context-gatherer, investigator) peut s'arrêter en cours
d'exécution et retourner un bloc HALT sur une véritable décision utilisateur :

```
HALT: need user decision
Reason: <why it can't proceed>
Question: <the specific question>
Proposed default: <recommendation>
State: <progress so far, to resume>
```

L'orchestrateur fait remonter la question, écrit la réponse dans `_signals/resume.<agent>.md`, et
re-dispatche. **Plafond : 3 allers-retours HALT par agent** ; après cela, procéder avec le default indiqué ou
s'arrêter avec un message clair.

## Build / test / lint par repo

| Repo | Build | Test (unique) | Lint |
|---|---|---|---|
| ReportManagerApi | `dotnet build /c/Repos/monolith/CFF/Products/ReportManagerApi/ReportManagerAPI.sln` | `dotnet test <proj> --filter "FullyQualifiedName~<Name>"` | — |
| ReportFoundations | `dotnet build <lib .sln/.csproj>` | `dotnet test <proj.SmallTests>` | — |
| pf-web | `nx build <project>` | `nx test <project> --testFile=<path>` | `nx lint <project>` |
| CroesusServer | CMake / Visual Studio | (généralement référence read-only) | — |
| ReportServer | CMake / Visual Studio | (généralement référence read-only) | — |

Tiers de test : C# `*.SmallTests` (unit, sans deps externes) / `*.MediumTests` (intégration), xUnit + Moq ;
Angular : Vitest. Le projet web API exécutable est `ReportManager.API/ReportManagerAPI.csproj`.

## Règles de branch, commit & ship

Les commits/PRs de produit se font **dans le repo réel derrière le symlink**, jamais dans le repo racine du workspace. Il n'y a
que deux repos produit : le monorepo `monolith` (tous les symlinks sauf pf-web — une branche/PR couvre C# + C++) et `pf-web`. Les agents `git add`-stagent les nouveaux fichiers mais **ne committent
pas** sauf si la tâche le demande explicitement ; le commit est l'étape finale et gatée de *ship* du workflow.

- Brancher depuis une référence protégée (`main`, `master`, `develop`, `release/*`, `support/*`) avec
  **`--no-track`** : `git switch -c <name> --no-track origin/develop`.
- Premier push d'une nouvelle branche : **`git push -u origin <branch>`** — jamais un `git push` nu.
- `pf-web` impose les **Conventional Commits** via commitlint ; les repos .NET suivent les conventions
  d'équipe standard.

> Celles-ci reflètent les garde-fous git au niveau org : ne jamais laisser une nouvelle branche suivre
> silencieusement une référence protégée ; toujours rendre la destination explicite au premier push.

## Garde-fous (chaque agent, chaque phase)

- **Ne jamais** exécuter de CLI org-denied : `aws`, `terraform`/`tofu`, ou des wrappers autour d'eux (`assume`,
  `granted`). ReportManagerApi utilise AWS via le SDK/la config uniquement — jamais la CLI.
- Les agents read-only (explorer, investigator, learning-guide, reviewer, retrospective) ne modifient jamais le code.
- Respecter le `CLAUDE.md` / `copilot-instructions.md` propre à chaque repo — ils l'emportent sur les conseils génériques.

## Collecte de contexte

Toujours dispatcher [`context-gatherer`](agents.md#context-gatherer) en premier dans
`feature`/`bug`/`refactor`/`spike`/`investigate`. Il résout le ticket Jira via l'Atlassian MCP,
résout le contexte GitHub via `gh` dans le repo pertinent, et écrit `context.md`. Si Jira/GitHub est
injoignable (headless/auth), le workflow procède sur les preuves locales et le dit — il ne fabrique jamais
le contenu d'un ticket.
