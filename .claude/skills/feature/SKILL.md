---
name: feature
description: Build a new feature (or user-facing / API change) in the Croesus report workspace, end to end, following the gated feature workflow — context → explore → plan → [gate] → build → review → [gate] → ship? → retrospective. Pulls context from Jira and GitHub. Use when the user asks to add/implement/build a feature, capability, report field, endpoint, or UI, or hands over a Jira story/ticket to implement. Not for fixing defects (use the bug workflow) or pure restructuring (use refactor).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **feature** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — notes de
> progression, questions (`AskUserQuestion`), résumés et bilan final. Le code, les noms de
> fichiers/d'agents, les chemins et les termes techniques restent inchangés.

Ce skill orchestre les agents de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§1 *feature*) et `.claude/conventions/protocol.md` (répertoire de
tâche, protocole de gate, la **barre de build** du gate de plan, protocole HALT, commandes par repo et
garde-fous). Cite-les et suis-les — ne réénonce pas leurs règles. Dispatche chaque sous-agent avec
l'outil **Agent**, en passant son `subagent_type` (le nom de l'agent) et un prompt de la forme :

```
Task directory: .work/<slug>/
Task: <the task text>
```

Réaffiche une courte note de progression d'une ligne à chaque transition de phase (quelle phase, quel
artefact a été produit).

## 1. Mise en place
- Dérive le **slug** : la clé Jira si le texte de la tâche en contient une (p. ex. `FOG-9412`,
  `CFF-1234`), sinon le kebab-case des ~4 premiers mots. Confirme le slug avec l'utilisateur s'il a été
  deviné.
- `mkdir -p .work/<slug>/_signals/` et écris le texte brut de la tâche dans `.work/<slug>/task.md`.

## 1a. Mode migration de rapport — déléguer au workspace de migration de rapports

**Quand l'activer.** Si cette feature *migre un rapport de Conseiller (C++) vers Xpert* — signaux : la
tâche dit « migrate »/« migration » avec un nom interne de rapport (p. ex. `FOREIGN_PROPERTY`,
`ASSETS_UNDER_MGT`, `PERF_SEC_LEVEL`), « to Xpert », ou porte les paramètres C++ d'un rapport vers
C#/Angular — exécute le **mode migration**. Confirme en une ligne que tu es en mode migration avant de
continuer ; sinon ignore cette section et exécute le flux standard ci-dessous.

En mode migration, le travail de domaine est piloté par les agents spécialistes qui vivent dans le
**workspace de migration de rapports**, *et non* par les `explorer`/`planner`/`implementer`/`reviewer`
génériques de ce workspace. Les **gates de la feature restent** — cette orchestration gatée est
exactement ce que `/feature` apporte.

**Les agents de migration (source unique de vérité — ne les copie PAS dans ce workspace) :**
`C:\Repos\claude-report-migration\.claude\agents\` → `report-analyst`, `backend-migrator`,
`frontend-migrator`, `migration-validator`, `migration-reviewer`. Leurs règles vivent dans
`C:\Repos\claude-report-migration\.claude\conventions\` (`migration-protocol.md` +
`backend-conventions.md` + `frontend-conventions.md`).

**Comment en invoquer un.** Ces agents ne sont **pas enregistrés comme sous-agents ici**, donc tu ne
peux pas passer leur nom en `subagent_type`. Dispatche avec l'outil **Agent** en utilisant
`subagent_type: general-purpose` et un prompt de cette forme exacte (remplis
`<agent>`/`<file>`/rapport/tâche) :

```
You are the <agent> for the Croesus report-migration workspace. Répondre en français.
Working root: C:\Repos\claude-report-migration — treat it as your cwd. All of that workspace's
relative paths (ReportManagerApi/, ReportFoundations/, CroesusServer/, pf-web/, docs/) resolve from
there, and they symlink the SAME monolith/pf-web checkouts this workspace uses, so edits are shared.
Read and follow your definition EXACTLY: C:\Repos\claude-report-migration\.claude\agents\<file>.md,
plus the conventions it cites in C:\Repos\claude-report-migration\.claude\conventions\.
Write your artifacts where your definition says (docs/reports/<REPORT>/…).
Report: <internal report name>.  Task: <the task text>.
```

Note : le dispatch general-purpose n'hérite pas du frontmatter `model:` de l'agent de migration —
c'est correct ; la définition gouverne quand même le comportement.

**Correspondance des phases (phases feature de ce workspace → agents de migration) :**

| Phase feature | Mode migration |
|---|---|
| 2. Contexte | garde `context-gatherer` seulement si une réf Jira/GitHub existe ; sinon saute-le et dis-le |
| 3. Explore | dispatche **`report-analyst`** → `docs/reports/<REPORT>/analysis.md` (la spec) |
| 4. Plan | la spec du `report-analyst` **est** le plan — n'exécute pas le `planner` de ce workspace |
| 5. GATE de plan | présente `analysis.md` ; approuver / changements (re-dispatcher `report-analyst`) / annuler |
| 6. Build | dispatche **`backend-migrator`**, puis **`frontend-migrator`** (ordre backend → frontend) |
| 7. Review | dispatche **`migration-reviewer`** (audit vs conventions) + **`migration-validator`** (JSON Xpert vs XML Conseiller, quand les sorties sont disponibles) |
| 8. GATE de code | comme d'habitude |
| 9. Ship | par repo touché (monolith + pf-web), règles git de l'org comme d'habitude |
| 10. Rétrospective | garde le `retrospective` de ce workspace |

Tout ce qui suit est le flux feature **standard (non-migration)** ; en mode migration, applique la
correspondance ci-dessus à chaque phase numérotée.

## 2. Contexte  →  `context.md`
Dispatche **context-gatherer** avec la clé Jira et/ou toute réf GitHub dans la tâche. Il écrit
`context.md`. S'il renvoie un bloc HALT, suis la boucle HALT de protocol.md (fais remonter via
`AskUserQuestion`, écris `_signals/resume.context-gatherer.md`, re-dispatche ; plafond 3).

## 3. Explore  →  `exploration.md`
Dispatche **explorer** pour cartographier le code affecté à travers les repos. Il écrit
`exploration.md`.

## 3a. Clarifier (seulement si nécessaire)
Lis `context.md` + `exploration.md`. S'il y a une *véritable* ambiguïté qui ferait deviner faux au
planner (emplacement flou avec plusieurs candidats, un choix de comportement non tranché, portée
ouverte), demande via `AskUserQuestion` et écris les Q→R dans `clarifications.md`. Saute en silence si
la tâche est claire. Ne pose pas de questions défensives « es-tu sûr ? ».

> **Spike d'abord ?** Si l'*approche elle-même* est véritablement inconnue (pas seulement les détails),
> dis à l'utilisateur que cela justifie un spike et propose de faire une pause ici — le workflow spike
> est désormais un skill, alors lance `/spike` puis reprends cette feature avec la décision en entrée.

## 4. Plan  →  `plan.md`
Dispatche **planner**. Il écrit un `plan.md` noté et estampillé d'un statut (tableau de couverture des
exigences, étapes, tests, risques, points de décision, estimation). Exécute la boucle HALT s'il en
renvoie une. Résous tout point de décision `needs-user` qu'il fait remonter via `AskUserQuestion` avant
de re-dispatcher.

## 5. Gate de plan — faire respecter la barre de build
Présente `plan.md` (commence par son en-tête **Status** + **Grade**). Applique la **barre de build** de
protocol.md : un plan n'est approuvable **que** lorsqu'il est `ready` **et** noté **A ou S**.
- Si `draft` ou en-dessous de A → **ne propose pas** *approuver*. Fais remonter la note + les bloqueurs,
  puis **changements** (écris le retour dans `_signals/revision-request.md`, re-dispatche le planner,
  reviens à ce gate) ou **annuler**. L'utilisateur peut explicitement passer outre pour approuver un
  plan sous la barre — consigne le passage-outre dans `_signals/revision-request.md`.
- Si `ready` + A/S → demande *approuver / changements / annuler* via `AskUserQuestion`. L'approbation
  reste requise. **annuler** → arrête (« annulé au gate de plan »).

## 6. Build  →  `build-summary.md`
Pour chaque repo/tranche nommé dans les sous-sections `#### <repo>` du plan, dispatche un builder dans
l'ordre du plan/pipeline (analyse C++ → C#/API → UI Angular) :
- **cpp-to-csharp-porter** quand l'étape est un port de value-provider C++→C#,
- **implementer** sinon.
Chacun écrit `build-summary.md` et build + exécute ses tests avant de renvoyer (résultat `ok` /
`tests-failed` / `build-failed`). Exécute la boucle HALT sur tout halt. Les builders `git add`-stagent
mais ne commitent pas.

## 7. Review  →  `review-code.md`
Dispatche **reviewer** en mode code sur le diff de travail. Il écrit `review-code.md` avec des
constats taggés par sévérité et un verdict.

## 8. Gate de code
Présente le verdict + le résultat de `build-summary.md`. Demande *approuver / changements / annuler*.
- **changements** ou `must-fix` présent → écris les constats dans `_signals/revision-request.md`,
  reboucle au §6 (re-build face à la review). **Plafond : 3 itérations build↔review** ; ensuite arrête
  et signale les problèmes restants.
- **approuver** → continue.

## 9. Ship (optionnel, gaté)
Demande s'il faut ship. Si oui, **par repo touché** (il n'y a pas de repo racine partagé) : crée une
branche de feature (`--no-track` depuis une réf protégée), commite, `git push -u`, ouvre une PR. Suis
les règles git de l'org dans protocol.md à la lettre. Saute entièrement si l'utilisateur refuse.

## 10. Rétrospective  →  `retro.md`
Dispatche **retrospective**. Il écrit `retro.md` et propose des entrées de mémoire durables + des mises
à jour doc/CLAUDE.md sous forme de checklist. Fais remonter cette checklist à l'utilisateur pour
approbation — **n'écris pas** automatiquement la mémoire et ne modifie pas les docs.

Termine par un court résumé : ce qui a été shippé/construit, la note du plan, le résultat build/review,
les PR (le cas échéant), et les apprentissages proposés en attente d'approbation.
