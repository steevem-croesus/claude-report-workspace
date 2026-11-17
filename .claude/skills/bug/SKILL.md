---
name: bug
description: Fix a defect in the Croesus report workspace, end to end, following the gated bug workflow — context → reproduce → diagnose → plan-fix → [gate] → build → verify+review → [gate] → retrospective → ship?. Pulls context from Jira and GitHub. Use when the user reports something broken/wrong (bad report output, error, crash, incorrect value, regression) or hands over a Jira bug ticket. Enforces no-fix-without-a-reproduction-and-a-regression-test. Not for new capabilities (use feature) or pure restructuring (use refactor).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **bug** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — notes de
> progression, questions (`AskUserQuestion`), résumés et bilan final. Le code, les noms de
> fichiers/d'agents, les chemins et les termes techniques restent inchangés.

Ce skill orchestre les agents de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§2 *bug*) et `.claude/conventions/protocol.md` (répertoire de
tâche, protocole de gate, la **barre de build** du gate de plan, protocole HALT, commandes par repo et
garde-fous). Cite-les et suis-les — ne réénonce pas leurs règles. Dispatche chaque sous-agent avec
l'outil **Agent**, en passant son `subagent_type` (le nom de l'agent) et un prompt de la forme :

```
Task directory: .work/<slug>/
Task: <the task text>
```

La règle distinctive de ce workflow : **aucun correctif ne ship sans une reproduction et un test de
régression** qui échoue avant le correctif et passe après. Le diagnostic est obligatoire et séparé du
correctif — ne rapièce pas les symptômes.

## 1. Mise en place
- Dérive le **slug** (clé Jira si présente, sinon kebab-case des ~4 premiers mots) ; confirme s'il a été deviné.
- `mkdir -p .work/<slug>/_signals/` et écris le rapport dans `.work/<slug>/task.md`.

## 2. Contexte  →  `context.md`
Dispatche **context-gatherer** avec la clé Jira et/ou la réf GitHub — il capture le rapport de bug, les
étapes de repro et toute PR/tout commit lié. Boucle HALT selon protocol.md si nécessaire.

## 3. Reproduire  →  `bug-diagnosis.md`
Établis une reproduction avant de diagnostiquer. Dispatche **explorer** si tu dois d'abord localiser le
chemin défaillant. Puis reproduis : préfère écrire un **test qui échoue** capturant le défaut ; sinon
documente les étapes de repro exactes. Consigne le statut de repro (fiable / intermittent /
pas-encore-reproduit) dans `bug-diagnosis.md`. Si ça ne peut pas être reproduit, fais-le remonter à
l'utilisateur via `AskUserQuestion` (plus de détails, ou continuer sur les meilleures preuves) avant de
poursuivre — ne rapièce pas à l'aveugle.

## 4. Diagnostiquer  →  `bug-diagnosis.md`
Dispatche **investigator** pour trouver la cause racine (preuves → hypothèses avec verdicts → cause
racine → confiance). Il ajoute à `bug-diagnosis.md`. Distingue le déclencheur de la cause sous-jacente.

## 5. Planifier le correctif  →  `plan.md`
Dispatche **planner** (cadré sur le correctif, minimal — le plan doit inclure le test de régression dans
sa section Tests). Il écrit un `plan.md` estampillé d'un statut (`draft`/`ready`). Boucle HALT/point de décision
comme dans protocol.md.

## 6. Review du plan + gate de plan  →  `review-plan.md`
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

## 7. Construire le correctif  →  `build-summary.md`
Dispatche **implementer** (ou **cpp-to-csharp-porter** si le correctif est dans un port de
value-provider C++→C#). Le build **doit** inclure le test de régression prouvant que le bug est corrigé.
Le builder build + exécute les tests avant de renvoyer. Boucle HALT au besoin. `git add`-stage, pas de
commit.

## 8. Vérifier + review  →  `review-code.md`
Confirme que la reproduction d'origine a disparu (ré-exécute le test qui échouait / la repro). Dispatche
**reviewer** en mode code ; il écrit `review-code.md`. La review doit confirmer que le test de
régression couvre réellement la cause racine, pas seulement le symptôme.

## 9. Gate de code
Demande *approuver / changements / annuler*. **changements** ou `must-fix` présent → écris les constats
dans `_signals/revision-request.md`, reboucle au §7 (**plafond 3** itérations build↔review), puis signale
les problèmes restants. **approuver** → continue.

## 10. Rétrospective  →  `retro.md`
Lance-la **dès que le gate de code est approuvé**, que l'on ship ensuite ou non. Dispatche **retrospective**. Son `retro.md` **doit** inclure la *classe* de cause racine (pour que des
bugs similaires soient attrapés plus tôt) et proposer des ajouts aux conventions du repo et des mises à jour de doc sous forme de
checklist pour approbation de l'utilisateur — ne les écris pas automatiquement.

## 11. Ship (optionnel, gaté)
Si l'utilisateur veut ship : **par repo touché**, branche (`--no-track` depuis une réf protégée),
commite, `git push -u`, ouvre une PR — selon les règles git de l'org dans protocol.md. Saute si refusé.

Termine par un court résumé : la cause racine, le correctif + le test de régression, le résultat
vérification/review, les PR (le cas échéant), et les apprentissages proposés en attente d'approbation.
