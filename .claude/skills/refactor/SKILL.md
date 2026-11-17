---
name: refactor
description: Restructure code in the Croesus report workspace without changing behaviour, end to end, following the gated refactor workflow — context → explore → characterize → plan → [gate] → build (small steps) → review → [gate] → ship? → retrospective. Pulls context from Jira and GitHub. Use when the user asks to refactor, clean up, restructure, extract, rename, de-duplicate, or improve the shape of existing code while keeping what it does the same. Enforces characterization-tests-before-edit and behaviour-preservation. Not for new capabilities (use feature) or fixing defects (use bug).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **refactor** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — notes de
> progression, questions (`AskUserQuestion`), résumés et bilan final. Le code, les noms de
> fichiers/d'agents, les chemins et les termes techniques restent inchangés.

Ce skill orchestre les agents de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§3 *refactor*) et `.claude/conventions/protocol.md` (répertoire de
tâche, protocole de gate, la **barre de build** du gate de plan, protocole HALT, commandes par repo et
garde-fous). Cite-les et suis-les — ne réénonce pas leurs règles. Dispatche chaque sous-agent avec
l'outil **Agent**, en passant son `subagent_type` (le nom de l'agent) et un prompt de la forme :

```
Task directory: .work/<slug>/
Task: <the task text>
```

La règle distinctive de ce workflow : **le comportement ne doit pas changer**. Les tests de
caractérisation viennent *avant* toute modification ; chaque consommateur en aval d'une surface
`ReportFoundations` touchée doit être nommé. Réaffiche une courte note de progression d'une ligne à
chaque transition de phase (quelle phase, quel artefact a été produit).

## 1. Mise en place
- Dérive le **slug** (clé Jira si présente, sinon kebab-case des ~4 premiers mots) ; confirme s'il a été deviné.
- `mkdir -p .work/<slug>/_signals/` et écris le texte brut de la tâche dans `.work/<slug>/task.md`.

## 2. Contexte  →  `context.md`
Dispatche **context-gatherer** avec la clé Jira et/ou la réf GitHub — capture *pourquoi* le refactor est
voulu et toute contrainte (échéances, API gelées, appelants à ne pas casser). Boucle HALT selon
protocol.md si nécessaire.

## 3. Explore  →  `exploration.md`
Dispatche **explorer** pour cartographier le **rayon d'impact** : le code à changer et chacun de ses
consommateurs à travers les repos. Pour `ReportFoundations` c'est critique — il est consommé par
`ReportManagerApi` et le Spooler ; la carte doit lister les sites d'appel en aval.

## 4. Caractériser  →  tests filet de sécurité (noté dans `build-summary.md`)
*Avant de toucher quoi que ce soit*, dispatche **implementer** pour ajouter un **filet de sécurité de
tests de caractérisation** qui fige le comportement observable actuel du code en portée, et pour les
build + exécuter au vert. Note tout comportement qui ne peut pas être figé (deps externes,
non-déterminisme) comme une lacune. Ce filet est ce qui prouve que le refactor préserve le comportement.

## 5. Plan  →  `plan.md`
Dispatche **planner**. Le plan doit être une séquence d'**étapes ordonnées, individuellement sûres et
préservant le comportement**, et doit explicitement pointer toute surface à changement cassant (API
publique, contrat, format de fil). Il écrit un `plan.md` noté et estampillé d'un statut. Boucle
HALT/point de décision selon protocol.md.

## 6. Gate de plan — faire respecter la barre de build
Présente `plan.md` (commence par son en-tête **Status** + **Grade**). Applique la **barre de build** de
protocol.md : approuvable **uniquement** lorsque `ready` **et** noté **A ou S**. Sous la barre → ne
propose pas *approuver* ; fais remonter la note + les bloqueurs, puis **changements** (écris le retour
dans `_signals/revision-request.md`, re-dispatche le planner, reviens ici) ou **annuler**. Un
passage-outre explicite de l'utilisateur est consigné dans `_signals/revision-request.md`. À/au-dessus
de la barre → demande *approuver / changements / annuler* via `AskUserQuestion`. **annuler** → arrête.

## 7. Build  →  `build-summary.md`
Pour chaque repo/tranche nommé dans les sous-sections `#### <repo>` du plan, dispatche **implementer** et
applique le refactor dans les **petites étapes** du plan — la caractérisation + les tests existants
doivent rester au vert **après chaque étape**. Si une étape passe au rouge, le changement de cette étape
ne préserve pas le comportement : arrête et signale plutôt que d'ajuster les tests pour qu'ils
correspondent. Les builders `git add`-stagent, pas de commit. Boucle HALT au besoin.

## 8. Review  →  `review-code.md`
Dispatche **reviewer** en mode code sur le diff de travail. La review doit vérifier **aucun changement
de comportement et aucune dérive de contrat** — surtout aux surfaces consommatrices que l'explorer a
cartographiées.

## 9. Gate de code
Présente le verdict + le résultat de `build-summary.md`. Demande *approuver / changements / annuler*.
**changements** ou `must-fix` présent → écris les constats dans `_signals/revision-request.md`, reboucle
au §7 (**plafond 3** itérations build↔review), puis signale les problèmes restants. **approuver** →
continue.

## 10. Ship (optionnel, gaté)
Si l'utilisateur veut ship : **par repo git touché** (monolith et/ou pf-web — jamais le repo racine du workspace), branche (`--no-track`
depuis une réf protégée), commite, `git push -u`, ouvre une PR — selon les règles git de l'org dans
protocol.md. Saute si refusé.

## 11. Rétrospective  →  `retro.md`
Dispatche **retrospective**. Il propose des entrées de mémoire durables + des mises à jour doc/CLAUDE.md
sous forme de checklist. Fais remonter la checklist à l'utilisateur pour approbation — **n'écris pas**
automatiquement la mémoire et ne modifie pas les docs.

Termine par un court résumé : ce qui a été restructuré, la note du plan, si le filet de sécurité a tenu
au vert tout du long, le résultat de la review, les PR (le cas échéant), et les apprentissages proposés
en attente d'approbation.
