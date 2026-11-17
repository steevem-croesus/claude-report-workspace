---
name: feature
description: Build a new feature (or user-facing / API change) in the Croesus report workspace, end to end, following the gated feature workflow — context → explore → plan → [gate] → build → review → [gate] → retrospective → ship?. Pulls context from Jira and GitHub. Use when the user asks to add/implement/build a feature, capability, report field, endpoint, or UI, or hands over a Jira story/ticket to implement. Not for fixing defects (use the bug workflow) or pure restructuring (use refactor).
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
- Dérive le **slug** : la clé Jira si le texte de la tâche en contient une (p. ex. `RPT-12345`,
  `CAR-1234`), sinon le kebab-case des ~4 premiers mots. Confirme le slug avec l'utilisateur s'il a été
  deviné.
- `mkdir -p .work/<slug>/_signals/` et écris le texte brut de la tâche dans `.work/<slug>/task.md`.

## 1a. Mode migration de rapport — piloter les agents de migration natifs

**Quand l'activer.** Si cette feature *migre un rapport de Conseiller (C++) vers Xpert* — signaux : la
tâche dit « migrate »/« migration » avec un nom interne de rapport (p. ex. `FOREIGN_PROPERTY`,
`ASSETS_UNDER_MGT`, `PERF_SEC_LEVEL`), « to Xpert », ou porte les paramètres C++ d'un rapport vers
C#/Angular — exécute le **mode migration**. Confirme en une ligne que tu es en mode migration avant de
continuer ; sinon ignore cette section et exécute le flux standard ci-dessous.

**Slug en mode migration (surcharge le §1).** Le `{slug}` du répertoire de tâche est la **clé Jira**
si un ticket est fourni, **sinon le nom interne du rapport** (p. ex. `FOREIGN_PROPERTY`) — pas le
kebab-case des premiers mots. **Tous les livrables** (analysis, logs, review, PDF)
vivent sous `.work/{slug}/` ; `docs/reports/` n'est qu'une archive des livrables finaux (voir `migration-protocol.md`).

En mode migration, le travail de domaine est piloté par les **agents spécialistes de migration**,
*et non* par les `explorer`/`planner`/`implementer`/`reviewer` génériques de ce workspace. Les
**gates de la feature restent** — cette orchestration gatée est exactement ce que `/feature` apporte.

**Les agents de migration (sous-agents natifs de ce workspace, `.claude/agents/`) :**
`report-analyst`, `backend-migrator`, `frontend-migrator`, `migration-validator`,
`migration-reviewer`. Leurs règles vivent dans `.claude/conventions/` (`migration-protocol.md` +
`backend-conventions.md` + `frontend-conventions.md`). **Livrables :** tous sous `.work/{slug}/`
(analysis.md, logs, review, PDF) — on ne travaille **jamais** directement sous `docs/reports/`. Données globales
partagées (entrées, pas livrables) : `docs/fields.csv` (liste maître des paramètres) et
`docs/template_ids.csv`.

**Comment en invoquer un.** Dispatche avec l'outil **Agent** en passant le nom de l'agent en
`subagent_type` (p. ex. `subagent_type: backend-migrator`) : sa définition + les conventions qu'elle
cite gouvernent le comportement, et son frontmatter `model:` est respecté. Les chemins repo
(`repos/ReportManagerApi/`, `repos/ReportFoundations/`, `repos/CroesusServer/`, `repos/pf-web/`) et
l'état (`docs/…`) résolvent depuis la racine de CE workspace. Réponds en français.

**Correspondance des phases (phases feature de ce workspace → agents de migration) :**

| Phase feature | Mode migration |
|---|---|
| 2. Contexte | garde `context-gatherer` seulement si une réf Jira/GitHub existe ; sinon saute-le et dis-le |
| 3. Explore | dispatche **`report-analyst`** → `.work/{slug}/analysis.md` (la spec) |
| 4. Plan | la spec du `report-analyst` **est** le plan — n'exécute pas le `planner` de ce workspace |
| 5. GATE de plan | présente `analysis.md` ; approuver / changements (re-dispatcher `report-analyst`) / annuler |
| 6. Build | dispatche **`backend-migrator`**, puis **`frontend-migrator`** (ordre backend → frontend) |
| 7. Review | dispatche **`migration-reviewer`** (audit vs conventions) + **`migration-validator`** (JSON Xpert vs XML Conseiller, quand les sorties sont disponibles) |
| 8. GATE de code | comme d'habitude |
| 9. Rétrospective | garde le `retrospective` de ce workspace, dès l'approbation du gate de code |
| 10. Ship | par repo touché (monolith + pf-web), règles git de l'org comme d'habitude |

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
Dispatche **planner**. Il écrit un `plan.md` estampillé d'un statut (`draft`/`ready`) (tableau de couverture des
exigences, étapes, tests, risques, points de décision, estimation). Exécute la boucle HALT s'il en
renvoie une. Résous tout point de décision `needs-user` qu'il fait remonter via `AskUserQuestion` avant
de re-dispatcher.

## 5. Review du plan + gate de plan  →  `review-plan.md`
Dispatche **reviewer** en mode plan sur `plan.md` : il écrit `review-plan.md` (critères C1 à C8 de
protocol.md, puis `Buildable: yes/no`). Cette revue est **systématique** — le plan n'est jamais jugé
par son auteur. Présente ensuite `plan.md` (son **Status**) et `review-plan.md` (son **Buildable** et
les critères à « non »), puis applique la **barre de build** de protocol.md :
- `draft` ou `Buildable: no` → **ne propose pas** *approuver*. Fais remonter les critères à « non » avec
  leur preuve, puis **changements** (écris-les dans `_signals/revision-request.md`, re-dispatche le
  planner, refais passer le reviewer, reviens à ce gate) ou **annuler**. L'utilisateur peut passer outre
  explicitement — consigne-le dans `_signals/revision-request.md`.
- `ready` + `Buildable: yes` → demande *approuver / changements / annuler* via `AskUserQuestion`.
  L'approbation reste requise. **annuler** → arrête (« annulé au gate de plan »).

Si le plan porte une **contrainte de sécurité ou d'intégrité** (contrôle d'accès, donnée à laquelle il
ne faut pas faire confiance, invariant de cohérence, secret, droit), rappelle au reviewer le critère
C7 : toute garantie « fermée par construction » doit être énoncée **canal d'entrée par canal d'entrée**.

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

## 9. Rétrospective  →  `retro.md`
Lance-la **dès que le gate de code est approuvé**, que l'on ship ensuite ou non. Dispatche
**retrospective**. Il écrit `retro.md` et propose des ajouts aux conventions du repo
(`known-pitfalls.md`, `rma-architecture-notes.md`) + des mises à jour doc/CLAUDE.md sous forme de checklist. Fais remonter cette checklist à l'utilisateur pour
approbation — **n'écris pas** automatiquement la mémoire et ne modifie pas les docs.

## 10. Ship (optionnel, gaté)
Demande s'il faut ship. Si oui, **par repo git touché** (monolith et/ou pf-web — jamais le repo racine du workspace) : crée une
branche de feature (`--no-track` depuis une réf protégée), commite, `git push -u`, ouvre une PR. Suis
les règles git de l'org dans protocol.md à la lettre. Saute entièrement si l'utilisateur refuse.

Termine par un court résumé : ce qui a été shippé/construit, le verdict de la revue du plan, le résultat build/review,
les PR (le cas échéant), et les apprentissages proposés en attente d'approbation.
