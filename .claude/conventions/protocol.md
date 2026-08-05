# Protocole de travail (partagé par tous les workflows)

Voici le socle commun sur lequel chaque workflow de `workflows.md` s'appuie : où vivent les artefacts,
comment le contexte est rassemblé, comment fonctionnent les gates et les HALT, ainsi que les règles de build/branche
propres à chaque repo. Il s'inspire des conventions du plugin `code-fleet` de l'org (répertoire de tâche, protocole HALT, gates
échelonnés, plans à couverture d'exigences, intel jira/gh) adaptées à ce workspace de rapports multi-repos. Voir le
`../../CLAUDE.md` racine pour la topologie des repos et le pipeline de rapports.

## Le répertoire de tâche — `.work/<TICKET-ID>/`

Chaque exécution de workflow non triviale crée un répertoire par tâche à la **racine du workspace** :
`C:\Repos\claude-report-workspace\.work\<slug>\`.

- **Slug** = la clé Jira lorsqu'elle est détectée (ex. `FOG-9412`, `CFF-1234`) ; sinon le kebab-case des
  ~4 premiers mots de la tâche. Réexécuter la même tâche réutilise le répertoire.
- Il vit à la racine du workspace à dessein — il ne **pollue pas** les repos symlinkés, et il
  survit d'une session à l'autre. Ajoute `.work/` à ton gitignore global si tu ne veux pas qu'il soit suivi.

### Noms de fichiers canoniques (un artefact = un fichier)

| Fichier | Écrit par | Objet |
|---|---|---|
| `context.md` | context-gatherer | Brief d'intel Jira + GitHub |
| `exploration.md` | explorer | Carte du code pour la tâche |
| `investigation.md` | investigator | Analyse de cause racine |
| `learning-notes.md` | learning-guide | Walkthrough / modèle mental |
| `spike.md` | (orchestrateur + explorer) | Constats de spike + recommandation |
| `plan.md` | planner | Plan d'implémentation (gate le build) |
| `bug-diagnosis.md` | investigator | Reproduction + cause racine d'un bug |
| `review-plan.md` | reviewer | Constats du gate de plan |
| `build-summary.md` | implementer / porter | Ce qui a été construit + résultats de build/test |
| `review-code.md` | reviewer | Constats du gate de code |
| `retro.md` | retrospective | Rétrospective + apprentissages proposés |
| `clarifications.md` | orchestrateur | Q→R résolues avant la planification |

## Rassemblement du contexte (début de chaque feature/bug/refactor/spike/investigate)

Dispatche toujours **context-gatherer** en premier. Il :
1. Résout le ticket Jira via le **MCP Atlassian** — `getAccessibleAtlassianResources`
   (pour le `cloudId`) → `getJiraIssue` (description, commentaires, critères d'acceptation, liens) →
   `getJiraIssueRemoteIssueLinks`. Les specs Confluence sont récupérées lorsqu'elles sont référencées.
2. Résout le contexte GitHub via le **`gh` CLI** exécuté à l'intérieur du repo symlinké pertinent —
   `gh pr view/diff`, `gh issue view`, `gh search`, et `git log`.
3. Écrit `context.md` et rapporte le(s) repo(s) cible(s) + les principales questions ouvertes.

Si Jira/GitHub est injoignable (headless/auth), le workflow avance sur les preuves locales et le signale —
il ne fabrique jamais le contenu du ticket.

## Protocole de gate (INTERACTIF — ce workspace tourne en mode gaté)

À chaque **gate**, l'orchestrateur s'arrête et interroge l'utilisateur, via `AskUserQuestion` :

> *« Approuver, demander des changements, ou annuler ? »*

- **approve** → passer à la phase suivante.
- **changes** → écrire le retour de l'utilisateur mot pour mot dans `.work/<slug>/_signals/revision-request.md`,
  redispatcher l'agent de la phase (il lit son artefact précédent + la demande de révision), puis revenir au
  même gate avec l'artefact révisé.
- **cancel** → arrêter le workflow.

Ne jamais franchir automatiquement un gate. Les deux gates universels sont le **gate de plan** (après `plan.md`) et
le **gate de code** (après `build-summary.md` + `review-code.md`) ; certains workflows ajoutent le leur
(ex. le gate de *décision* du spike).

### Gate de plan — la barre de build

Le gate de plan a une condition d'entrée supplémentaire et non négociable. `plan.md` porte un en-tête
`**Status:** <draft|ready> · **Grade:** <F|D|C|B|A|S>` (échelle **F < D < C < B < A < S** ; barème
détenu par `../agents/planner.md`). Le workflow ne peut builder **que** depuis un plan qui est **`ready`**
**et** noté **A ou S**.

- Si le plan est `draft` ou noté **en dessous de A**, le gate n'offre **pas** *approve*. Fais ressortir la
  note + le pourquoi (questions ouvertes bloquantes, points de décision `needs-user`), et achemine vers **changes** —
  redispatche le planner (en résolvant éventuellement d'abord les points de décision `needs-user` via `AskUserQuestion`)
  jusqu'à ce qu'il atteigne `ready` + (A|S), ou **cancel**.
- Ce n'est que lorsque le plan est `ready` + (A|S) que l'utilisateur obtient le choix normal *approve / changes / cancel*.
  L'approbation reste requise — une note qualifiante déverrouille le gate, elle ne le franchit pas automatiquement.
- L'utilisateur peut **passer outre** et approuver explicitement un plan sous la barre (ex. un changement délibérément petit
  qu'il a jugé correct) ; consigne le passage outre dans `revision-request.md` pour qu'il soit auditable. En l'absence d'un
  passage outre explicite, la barre tient.

## Protocole HALT (agent → orchestrateur)

Tout agent producteur (planner, implementer, porter, context-gatherer, investigator) peut s'arrêter en cours d'exécution
et renvoyer un bloc HALT lorsqu'il tombe sur une véritable décision utilisateur :

```
HALT: need user decision
Reason: <why it can't proceed>
Question: <the specific question>
Proposed default: <recommendation>
State: <progress so far, to resume>
```

L'orchestrateur fait ressortir la question (via `AskUserQuestion`), écrit la réponse dans
`.work/<slug>/_signals/resume.<agent>.md`, et redispatche. Plafond : **3 allers-retours HALT par agent** ;
au-delà, procède avec la valeur par défaut énoncée ou arrête avec un message clair.

## Build / test / lint par repo (ce que les agents exécutent réellement)

| Repo | Build | Test (unitaire) | Lint |
|---|---|---|---|
| ReportManagerApi | `dotnet build repos/ReportManagerApi/ReportManagerAPI.sln` | `dotnet test <proj> --filter "FullyQualifiedName~<Name>"` | — |
| ReportFoundations | `dotnet build <the lib .sln/.csproj>` | `dotnet test <proj.SmallTests>` | — |
| pf-web | `nx build <project>` | `nx test <project> --testFile=<path>` | `nx lint <project>` |
| CroesusServer | CMake / Visual Studio | (généralement référence en lecture seule) | — |
| ReportServer | CMake / Visual Studio | (généralement référence en lecture seule) | — |

Paliers de test : C# `*.SmallTests` (unitaire, sans dépendances externes) / `*.MediumTests` (intégration), xUnit + Moq.
Angular : Vitest. Le projet web d'API exécutable est `ReportManager.API/ReportManagerAPI.csproj`.

## Règles de branche, commit & ship (par repo, imposées par l'org)

Les commits/PR se font **par repo symlinké, sur la branche propre de ce repo** — il n'y a pas de repo racine partagé.
Les agents mettent en staging les nouveaux fichiers avec `git add` mais **ne committent pas** sauf si la tâche le demande explicitement ; le commit
est l'étape finale de *ship* du workflow, gatée.

- Brancher depuis une réf protégée (`main`, `master`, `develop`, `release/*`, `support/*`) avec
  **`--no-track`** : `git switch -c <name> --no-track origin/develop`.
- Premier push d'une nouvelle branche : **`git push -u origin <branch>`** — jamais un `git push` nu.
- `pf-web` impose les **Conventional Commits** via commitlint (voir `repos/pf-web/CLAUDE.md`) ; les repos .NET
  suivent les conventions d'équipe standard.

## Garde-fous (s'appliquent à chaque agent et phase)

- **Ne jamais** exécuter les CLI interdites par l'org : `aws`, `terraform`/`tofu`, ou leurs wrappers (ex. `assume`,
  `granted`). ReportManagerApi utilise AWS uniquement via le SDK/la config — jamais la CLI.
- Les agents en lecture seule (explorer, investigator, learning-guide, reviewer, retrospective) n'éditent jamais le code.
- Respecte le `CLAUDE.md` / `copilot-instructions.md` propre à chaque repo — ils priment sur les conseils génériques.
