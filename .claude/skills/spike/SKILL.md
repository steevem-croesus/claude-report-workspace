---
name: spike
description: Run a timeboxed investigation in the Croesus report workspace to reduce uncertainty and reach a decision, following the spike workflow — frame + timebox → context → investigate (throwaway) → findings → [gate (decide)]. Use when the approach itself is genuinely unknown and the user wants to evaluate options before committing ("should we…?", "is X feasible?", "which approach?", "spike this"). Produces a recommendation, not shipped code — prototypes are throwaway. Not for building the chosen approach (use feature/refactor) or explaining existing behaviour (use investigate).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **spike** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — notes de
> progression, questions (`AskUserQuestion`), résumés et bilan final. Le code, les noms de
> fichiers/d'agents, les chemins et les termes techniques restent inchangés.

Ce skill orchestre les agents de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§4 *spike*) et `.claude/conventions/protocol.md` (répertoire de
tâche, protocole de gate, protocole HALT, garde-fous). Cite-les et suis-les — ne réénonce pas leurs
règles. Dispatche chaque sous-agent avec l'outil **Agent**, en passant son `subagent_type` (le nom de
l'agent) et un prompt de la forme :

```
Task directory: .work/<slug>/
Task: <the task text>
```

Les règles distinctives de ce workflow : **aucun code de production** — tout prototype est jetable,
gardé isolé, et ne doit pas être shippé ; le travail est **timeboxé** ; et le livrable est une
**décision**, pas un merge. Il n'y a pas de phase build/review/ship ni de phase rétrospective — mais tu
captures quand même les apprentissages durables en mémoire à la fin. Réaffiche une note de progression
d'une ligne à chaque transition de phase.

## 1. Cadrer + timeboxer
Avant de dispatcher quoi que ce soit, fixe avec l'utilisateur (via `AskUserQuestion` seulement si
flou) :
- la **question précise** à laquelle le spike doit répondre,
- un **timebox** (combien d'effort ça vaut la peine d'y consacrer),
- à quoi ressemble le **« terminé »** — la décision que ça alimente et les options sur la table.
Dérive le **slug** (clé Jira si présente, sinon kebab-case des ~4 premiers mots ; confirme s'il a été
deviné), `mkdir -p .work/<slug>/_signals/`, et écris le cadrage (question, timebox, définition du
terminé) dans `.work/<slug>/task.md`.

## 2. Contexte (léger)  →  `context.md`
Seulement si un ticket ou une réf GitHub existe : dispatche **context-gatherer** pour un brief léger.
Saute si le spike est une pure question « est-ce faisable » sans ticket — dis-le et passe à la suite.

## 3. Investiguer  →  preuves (notes vers `spike.md`)
Dispatche **explorer** (pour cartographier ce qui existe / où sont les jointures) et/ou **investigator**
(pour répondre au *pourquoi/si* quelque chose tient) selon ce que la question demande. Si un prototype
jetable se justifie, construis-le en **isolation** — un emplacement de brouillon, jamais édité dans les
sources des vrais repos — et traite-le comme une preuve jetable, pas un livrable. Reste dans le timebox ;
s'il explose, arrête et signale ce qui est connu jusqu'ici.

## 4. Constats  →  `spike.md`
Synthétise dans `spike.md` : la question, ce qui a été essayé, les **options** avec leurs compromis et
le coût/risque de chacune, et une **recommandation** claire. Sois explicite sur ce qui reste incertain
et sur ce qu'une feature/un refactor de suivi devrait verrouiller.

## 5. Gate de décision
Présente `spike.md` (commence par la recommandation). Demande à l'utilisateur de **décider** via
`AskUserQuestion` — typiquement : choisir une option (qui alimente généralement un workflow `feature` ou
`refactor`), demander plus d'investigation (reboucle au §3, en respectant un nouveau timebox), ou
laisser tomber. Consigne la décision dans `spike.md`.

## 6. Capturer les apprentissages
Même sans phase de rétrospective, fais remonter une courte checklist d'apprentissages durables valant la
peine d'être sauvés en mémoire (verdicts de faisabilité, impasses à éviter, contraintes découvertes).
**N'écris pas** automatiquement la mémoire — propose la checklist pour l'approbation de l'utilisateur.

Termine par un court résumé : la question, la recommandation, la décision de l'utilisateur, le workflow
de suivi qu'elle alimente (le cas échéant), et les apprentissages proposés en attente d'approbation.
