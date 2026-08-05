---
name: learn
description: Build a mental model of an area of the Croesus report workspace — read-only, teaching — following the learn workflow (pick target + level → guided walkthrough → glossary → exercises). Use when the user wants to understand or be onboarded onto a subsystem or concept ("help me understand X", "walk me through the Spooler batch flow", "teach me the C++→C# port mechanism", "explain pf-web's DDD layering"). Produces a walkthrough with a glossary and safe exercises, changes no code. Not for locating code (use explore) or diagnosing why something happened (use investigate).
allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash
---

Pilote le workflow **learn** pour cette tâche :

**$ARGUMENTS**

> **Langue.** Communique avec l'utilisateur **en français** pendant tout ce workflow — cadrage,
> questions (`AskUserQuestion`), walkthrough, glossaire et clôture. Le code, les noms de
> fichiers/d'agents, les chemins et les termes techniques restent inchangés.

Ce skill orchestre l'agent **learning-guide** de `.claude/agents/`. Les spécifications qui font autorité
sont `.claude/conventions/workflows.md` (§7 *learn*) et `.claude/conventions/protocol.md` (répertoire de
tâche, noms de fichiers canoniques, garde-fous). Cite-les et suis-les — ne réénonce pas leurs règles.
Dispatche le sous-agent avec l'outil **Agent**, en passant son `subagent_type` et un prompt de la
forme :

```
Task directory: .work/<slug>/
Task: teach <the subsystem/concept> at <the learner's level>
```

C'est un workflow **read-only, sans gate, pédagogique**. Il n'y a pas de plan, pas de build, pas de
ship, pas de rétrospective — le livrable est un walkthrough qui laisse l'utilisateur avec un modèle
mental qui fonctionne. Il enseigne ; il **ne change pas** le code.

## 1. Cible + niveau
Fixe deux choses — le **sous-système/concept** à enseigner (p. ex. les params value-provider, le flux
batch du Spooler, le layering DDD de pf-web, le mécanisme de port C++→C#, le pipeline de génération de
rapport de bout en bout) et le **niveau actuel de l'apprenant** (nouveau sur la codebase / connaît un
repo / expérimenté ailleurs). Si l'un ou l'autre est flou, demande une fois via `AskUserQuestion`.
Dérive le **slug** (kebab-case de la cible ; une clé Jira seulement si l'apprentissage y est lié) et
`mkdir -p .work/<slug>/`.

## 2. Enseigner  →  `learning-notes.md`
Dispatche **learning-guide** pour produire le walkthrough, calibré au niveau énoncé : **vue d'ensemble →
trace du chemin nominal** à travers les vrais points d'entrée `repo/path:line` → **abstractions clés** →
un **glossaire** des termes du domaine → quelques **exercices pratiques sûrs** (read-only ou en bac à
sable — jamais rien qui mute les vrais repos). Il écrit `learning-notes.md`.

## 3. Conclure
Fais remonter la forme du walkthrough (le chemin de trace, les fichiers clés, les exercices) et invite à
des questions de suivi ou à une passe plus approfondie sur une partie. Pointe vers le prochain workflow
naturel si l'utilisateur veut maintenant *faire* quelque chose — `explore` pour cartographier plus loin,
`feature`/`refactor` pour construire, `investigate` pour creuser un comportement.
