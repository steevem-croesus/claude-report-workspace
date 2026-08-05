---
name: explore
description: Map where something lives or how it flows across the Croesus report repos — read-only, fast, no gates — following the explore workflow (scope → map → answer). Use when the user asks "where is X", "what calls Y", "how does the report pipeline flow through these repos", "map this subsystem", or wants to orient before a feature/refactor. Produces a repo/path:line map, changes no code. Not for "why did this happen" (use investigate) or "teach me this area" (use learn).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **explore** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — cadrage,
> questions (`AskUserQuestion`) et réponse finale. Le code, les noms de fichiers/d'agents, les chemins
> et les termes techniques restent inchangés.

Ce skill orchestre l'agent **explorer** de `.claude/agents/`. Les spécifications qui font autorité sont
`.claude/conventions/workflows.md` (§5 *explore*) et `.claude/conventions/protocol.md` (répertoire de
tâche, noms de fichiers canoniques, garde-fous). Cite-les et suis-les — ne réénonce pas leurs règles.
Dispatche le sous-agent avec l'outil **Agent**, en passant son `subagent_type` et un prompt de la
forme :

```
Task directory: .work/<slug>/
Task: <the question>
```

C'est un workflow **read-only, sans gate, rapide**. Il n'y a pas de plan, pas de build, pas de ship,
pas de rétrospective. Le livrable est une carte de code qui répond à la question. Il est délibérément
bon marché — ne le sur-échafaude pas.

## 1. Cadrer
Reformule la question en une ligne et nomme les **repos candidats** (lesquels de CroesusServer,
ReportServer, ReportFoundations, ReportManagerApi, pf-web sont probablement en jeu). Si la question est
véritablement ambiguë (plusieurs choses distinctes qu'elle pourrait signifier), demande une fois via
`AskUserQuestion` ; sinon continue. Pour une question ponctuelle rapide sans ticket, tu peux sauter le
répertoire de tâche — pour tout ce qui vaut la peine d'être gardé, dérive le **slug** et
`mkdir -p .work/<slug>/`.

## 2. Cartographier  →  `exploration.md` (ou en ligne)
Dispatche **explorer** pour produire une carte `repo/path:line` plus le flux inter-repos. Pour une
petite question rapide, laisse-le répondre en ligne ; pour une carte substantielle, fais-lui écrire
`exploration.md`.

## 3. Répondre
Résume le constat pour l'utilisateur : la carte, le flux, et les points d'entrée cliquables
`repo/path:line` — plus un pointeur « prochain workflow » d'une ligne si l'exploration mène
naturellement vers un `feature`, un `refactor` ou un `investigate`.
