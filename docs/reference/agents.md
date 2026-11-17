<!-- Page générée par .claude/scripts/gen-reference-docs.py — ne pas éditer à la main. -->

# Référence — Agents

Un agent par fichier sous [`.claude/agents/`](../../.claude/agents/) ; on le dispatche par son nom (`subagent_type`). Le fichier de l'agent fait autorité : cette page n'en reprend que l'en-tête.

| Agent | Modèle | Écrit du code |
|---|---|---|
| [`backend-migrator`](#backend-migrator) | opus | oui |
| [`context-gatherer`](#context-gatherer) | sonnet | non |
| [`cpp-to-csharp-porter`](#cpp-to-csharp-porter) | opus | oui |
| [`explorer`](#explorer) | sonnet | non |
| [`frontend-migrator`](#frontend-migrator) | opus | oui |
| [`implementer`](#implementer) | opus | oui |
| [`investigator`](#investigator) | opus | non |
| [`learning-guide`](#learning-guide) | sonnet | non |
| [`migration-reviewer`](#migration-reviewer) | opus | non |
| [`migration-validator`](#migration-validator) | sonnet | non |
| [`planner`](#planner) | opus | non |
| [`report-analyst`](#report-analyst) | opus | non |
| [`retrospective`](#retrospective) | sonnet | non |
| [`reviewer`](#reviewer) | opus | non |

## backend-migrator

Migre le backend d'un rapport de Conseiller (C++) vers Xpert (C#, ReportManagerApi). Localise les classes, extrait/classifie les paramètres, analyse le C++, implémente Parameters.cs (InitialValue, ValueProviderFunction, radio/combo déclaratifs), crée les classes VPF custom + tests, enregistre dans les executers et WebRTMRunner, build et teste. Pour du frontend, utiliser frontend-migrator.

- **Modèle :** opus
- **Outils :** `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`, `Skill`, `mcp__ide__getDiagnostics`
- **Définition :** [`.claude/agents/backend-migrator.md`](../../.claude/agents/backend-migrator.md)

## context-gatherer

Read-only. Given a Jira key (e.g. RPT-12345), a GitHub PR/issue ref (#123 or URL), or a free-text task, pulls the ticket, its comments and links, and any related GitHub PRs/issues/commits into a single Context brief. Invoke this FIRST in every feature/bug/refactor/spike/investigate workflow. Does not plan or propose fixes — it only assembles facts.

- **Modèle :** sonnet
- **Outils :** `Read`, `Write`, `Grep`, `Glob`, `Bash`, `WebFetch`, `mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources`, `mcp__plugin_atlassian_atlassian__getJiraIssue`, `mcp__plugin_atlassian_atlassian__listJiraIssueComments`, `mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql`, `mcp__plugin_atlassian_atlassian__getConfluenceContent`, `mcp__plugin_atlassian_atlassian__searchConfluence`, `mcp__plugin_atlassian_atlassian__search`, `mcp__claude_ai_Atlassian__getAccessibleAtlassianResources`, `mcp__claude_ai_Atlassian__getJiraIssue`, `mcp__claude_ai_Atlassian__searchJiraIssuesUsingJql`, `mcp__claude_ai_Atlassian__getJiraIssueRemoteIssueLinks`, `mcp__claude_ai_Atlassian__getConfluencePage`, `mcp__claude_ai_Atlassian__searchConfluenceUsingCql`, `mcp__claude_ai_Atlassian__fetch`
- **Définition :** [`.claude/agents/context-gatherer.md`](../../.claude/agents/context-gatherer.md)

## cpp-to-csharp-porter

Specialist for the recurring cross-repo task — porting a C++ report function from repos/CroesusServer OR repos/ReportServer into a C# IValueProviderParameter in repos/ReportManagerApi. Follows the recipe in repos/ReportManagerApi/copilot-instructions.md exactly: locate + analyze the C++, convert semantics to C#, place the class, register it in the correct executer, add any date-service methods, and write unit tests. Use whenever a report parameter/value must be reimplemented from the C++ monolith or the C++ report engine.

- **Modèle :** opus
- **Outils :** `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`, `mcp__ide__getDiagnostics`
- **Définition :** [`.claude/agents/cpp-to-csharp-porter.md`](../../.claude/agents/cpp-to-csharp-porter.md)

## explorer

Read-only cross-repo code locator and mapper for the report workspace. Answers "where is X", "what calls Y", "how does the report pipeline flow through these repos", "map this subsystem". Returns a file:line map spanning CroesusServer (C++), ReportFoundations + ReportManagerApi (C#), and pf-web (Angular). Use at the start of feature/refactor work and for the `explore` workflow. Does not propose fixes or write code.

- **Modèle :** sonnet
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`
- **Définition :** [`.claude/agents/explorer.md`](../../.claude/agents/explorer.md)

## frontend-migrator

Crée le composant Angular de paramétrage d'un rapport migré dans pf-web. Extrait les paramètres PRE, reproduit la logique C++ (patterns Observer inter-champs, validateurs de dates, visibilité conditionnelle), implémente le composant TypeScript + template HTML, l'enregistre (factory, listes de types, cleanParamType, rapports exclusifs), crée les tests e2e Cypress + fixtures, et vérifie la compilation. Pour le backend C#, utiliser backend-migrator.

- **Modèle :** opus
- **Outils :** `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`, `Skill`, `mcp__ide__getDiagnostics`
- **Définition :** [`.claude/agents/frontend-migrator.md`](../../.claude/agents/frontend-migrator.md)

## implementer

Implements an approved plan.md in the report workspace, adapting to whichever repo/stack it edits (C# .NET, Angular/NX, or C++). Reads the target repo's CLAUDE.md/copilot-instructions, writes code + tests, and always builds (and runs the tests it authored) before returning. Use for the build phase of feature/bug/refactor workflows, after the plan gate. For C++→C# value-provider ports, defer to cpp-to-csharp-porter.

- **Modèle :** opus
- **Outils :** `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`, `mcp__ide__getDiagnostics`
- **Définition :** [`.claude/agents/implementer.md`](../../.claude/agents/implementer.md)

## investigator

Read-only root-cause analyst for the report workspace. Answers "why did X happen / why is Y broken / how did this bug reach production". Gathers evidence from code, git history, Jira, GitHub, and logs; forms hypotheses; verifies or refutes each; concludes with the most-supported root cause. Use for the `investigate` workflow and the diagnose phase of the `bug` workflow. Does not fix — it explains.

- **Modèle :** opus
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `WebFetch`
- **Définition :** [`.claude/agents/investigator.md`](../../.claude/agents/investigator.md)

## learning-guide

Read-only teaching agent for the report workspace. Given a subsystem, concept, or repo area, produces a guided walkthrough that builds a mental model — entry points, data flow, key files, glossary, and hands-on exercises. Use for the `learn` workflow when onboarding onto the report pipeline or a specific area. Teaches; does not change code.

- **Modèle :** sonnet
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `WebFetch`
- **Définition :** [`.claude/agents/learning-guide.md`](../../.claude/agents/learning-guide.md)

## migration-reviewer

Relecteur (lecture seule) d'une migration de rapport. Audite le diff backend et/ou frontend contre les conventions de migration — fidélité C++→C#, catégories/registrations, ordre alphabétique, séparateurs, logique de dates, VPF divergentes, patterns Observer, tests. Une ligne par finding, sévérité taguée, sans complaisance. À utiliser après backend-migrator / frontend-migrator, avant PR.

- **Modèle :** opus
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `Write`
- **Définition :** [`.claude/agents/migration-reviewer.md`](../../.claude/agents/migration-reviewer.md)

## migration-validator

Validateur post-migration (lecture seule). Compare la sortie Xpert (JSON) avec la sortie Conseiller (XML) d'un même rapport pour valider l'équivalence fonctionnelle des paramètres. Classe chaque différence (identique / attendue / fonctionnelle) et propose des pistes d'investigation. À utiliser après une migration backend. Ne modifie aucun code.

- **Modèle :** sonnet
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Skill`
- **Définition :** [`.claude/agents/migration-validator.md`](../../.claude/agents/migration-validator.md)

## planner

Produces an implementation plan for a feature/refactor/bug-fix in the report workspace. Reads context.md + exploration.md, respects each repo's architecture (DDD in pf-web, clean architecture in ReportManagerApi, the value-provider recipe in copilot-instructions.md), and writes a brief, coverage-mapped plan.md with per-repo steps. Its output gates the build. Invoke after context + exploration, before any code is written.

- **Modèle :** opus
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `Write`
- **Définition :** [`.claude/agents/planner.md`](../../.claude/agents/planner.md)

## report-analyst

Analyste de rapport (lecture seule) pour la migration C++ → Xpert. Extrait et classifie les paramètres d'un rapport, localise et analyse le code C++ source, estime la complexité, vérifie les implémentations C# existantes, et produit une spec de migration. À utiliser AVANT d'implémenter quand on veut une analyse revue, ou pour estimer/planifier. Ne modifie aucun code.

- **Modèle :** opus
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`, `Write`, `Skill`
- **Définition :** [`.claude/agents/report-analyst.md`](../../.claude/agents/report-analyst.md)

## retrospective

Runs at the end of a feature/bug/refactor workflow. Reads the task artifacts (context, plan, reviews, build summary, and the final diff) and produces a retrospective — what shipped, what went well, what was surprising, and concrete follow-ups. Proposes durable learnings to save to Claude memory and doc/CLAUDE.md updates. Captures knowledge; does not change production code.

- **Modèle :** sonnet
- **Outils :** `Read`, `Glob`, `Grep`, `Bash`, `Write`
- **Définition :** [`.claude/agents/retrospective.md`](../../.claude/agents/retrospective.md)

## reviewer

Reviews a plan.md (plan gate) or a code diff (code gate) in the report workspace. One line per finding, severity-tagged, no praise, no scope creep. Checks correctness, architecture/layering compliance, test adequacy, and cross-repo contract drift. Use at the review gates of the feature/bug/refactor workflows.

- **Modèle :** opus
- **Outils :** `Read`, `Grep`, `Glob`, `Bash`
- **Définition :** [`.claude/agents/reviewer.md`](../../.claude/agents/reviewer.md)
