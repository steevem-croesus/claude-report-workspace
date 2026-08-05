---
name: investigate
description: Find out why or how something happened in the Croesus report workspace — read-only, evidence-driven — following the investigate workflow (frame → context → analyze → conclude). Pulls context from Jira and GitHub. Use when the user asks "why did X happen", "how did this reach production", "why is Y behaving this way", or wants a root-cause understanding without a fix. Rules out alternatives with code, git history, and logs. Not for fixing a known defect (use bug, which runs this as its diagnosis) or locating code (use explore).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **investigate** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — cadrage,
> questions (`AskUserQuestion`) et conclusion finale. Le code, les noms de fichiers/d'agents, les
> chemins et les termes techniques restent inchangés.

Ce skill orchestre les agents de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§6 *investigate*) et `.claude/conventions/protocol.md` (répertoire
de tâche, noms de fichiers canoniques, protocole HALT, garde-fous). Cite-les et suis-les — ne réénonce
pas leurs règles. Dispatche chaque sous-agent avec l'outil **Agent**, en passant son `subagent_type`
(le nom de l'agent) et un prompt de la forme :

```
Task directory: .work/<slug>/
Task: <the question / incident>
```

C'est un workflow **read-only, sans gate**. Il n'y a pas de plan, pas de build, pas de ship, pas de
rétrospective — le livrable est une conclusion de cause racine avec ses preuves à l'appui. C'est **plus
profond qu'`explore`** : il répond au *pourquoi/comment*, en écartant les alternatives plutôt qu'en se
contentant de cartographier où vit le code. Quand la cause est inconnue au début d'un bug, c'est la
moitié avant du workflow `bug`.

## 1. Cadrer
Énonce la **question ou l'incident précis** en une ligne — quel comportement/résultat a besoin d'être
expliqué, et (si connu) quand ça a commencé. Dérive le **slug** (clé Jira si présente, sinon kebab-case
des ~4 premiers mots ; confirme s'il a été deviné) et `mkdir -p .work/<slug>/_signals/` ; écris le
cadrage dans `.work/<slug>/task.md`. Si la question est trop vague pour investiguer, affine-la une fois
via `AskUserQuestion`.

## 2. Contexte  →  `context.md`
Dispatche **context-gatherer** avec la clé Jira et/ou la réf GitHub — il tire le ticket, les PR liées,
les commits et l'historique qui portent sur l'incident. Boucle HALT selon protocol.md si nécessaire.
Saute seulement s'il n'y a véritablement aucun contexte ticket/GitHub, et dis-le.

## 3. Analyser  →  `investigation.md`
Dispatche **investigator** pour travailler les preuves : rassemble depuis le code, l'historique git,
Jira, GitHub et les logs ; forme des **hypothèses** ; vérifie ou réfute chacune avec un verdict ; et
conclus avec la **cause racine la mieux étayée** et un niveau de **confiance**. Il écrit
`investigation.md`. S'il renvoie un HALT (besoin d'une décision ou accès manquant), exécute la boucle
HALT de protocol.md.

## 4. Conclure
Présente la conclusion : la cause racine, les preuves clés qui l'épinglent, les alternatives écartées et
la confiance. Si la prochaine étape naturelle est un correctif, oriente l'utilisateur vers le workflow
`bug` (qui réutilisera ce diagnostic) ou `feature`/`refactor` selon le cas — mais **ne commence pas** à
corriger ici.
