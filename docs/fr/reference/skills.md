# Référence — Skills

Les skills sont les points d'entrée invocables par le modèle. Deux familles vivent ici.

## Skills de workflow (détenus par ce workspace)

Sous [`.claude/skills/`](../../../.claude/skills/), un par workflow gated/read-only. Chacun est
invocable par le modèle (Claude le choisit à partir de la description) ou exécutable comme slash command. Chacun
**défère à** [`workflows.md`](../../../.claude/conventions/workflows.md) et
[`protocol.md`](../../../.claude/conventions/protocol.md) pour les règles faisant autorité et orchestre
les [agents](agents.md) via l'outil Agent.

| Skill | Slash command | `workflows.md` §  | Détails |
|---|---|---|---|
| feature | `/feature` | §1 | [référence](workflows.md#1-feature) · [guide pratique](../how-to/run-the-feature-workflow.md) |
| bug | `/bug` | §2 | [référence](workflows.md#2-bug) · [guide pratique](../how-to/fix-a-bug.md) |
| refactor | `/refactor` | §3 | [référence](workflows.md#3-refactor) |
| spike | `/spike` | §4 | [référence](workflows.md#4-spike) |
| explore | `/explore` | §5 | [référence](workflows.md#5-explore) |
| investigate | `/investigate` | §6 | [référence](workflows.md#6-investigate) |
| learn | `/learn` | §7 | [référence](workflows.md#7-learn) |

**Forme commune de chaque skill de workflow :**

- `allowed-tools: Agent, Task, AskUserQuestion, Read, Write, Grep, Glob, Bash`.
- Dispatche chaque sous-agent avec l'outil Agent, en passant son `subagent_type` (le nom de l'agent) et un
  prompt de la forme :
  ```
  Task directory: .work/<slug>/
  Task: <the task text>
  ```
- **Setup** dérive le slug (clé Jira si présente, sinon kebab-case des ~4 premiers mots ; confirme si
  deviné) et `mkdir -p .work/<slug>/_signals/`.
- Les gatés (`feature`/`bug`/`refactor`) imposent la [barre de build](gates-and-protocol.md#le-gate-de-plan--la-barre-de-build)
  au gate de plan et plafonnent les boucles build↔review à **3**.
- Les read-only (`explore`/`investigate`/`learn`) n'ont pas de gates, pas de build, pas de ship, pas de retro.

## Skills monolith (symlinkés)

Sept helpers d'authoring/de test du monolith CFF sont **symlinkés** dans `.claude/skills/` depuis
`/c/Repos/monolith/.claude/skills/`. Ce sont des liens spécifiques à la machine — **gitignorés, non trackés**
(voir [`.gitignore`](../../../.gitignore)) — et (re)créés en exécutant `link-monolith-skills.ps1`
en mode élevé, puis en redémarrant Claude Code. Les vrais skills sont détenus par le repo monolith ; **édite-les
là-bas, pas ici.**

| Skill | Objet |
|---|---|
| `croesus-orm` | créer/modifier des classes ORM Croesus (BOs, Repositories, Flex objects, FlexScenarios) |
| `create-small-tests` | tests unitaires xUnit + Moq pour une classe controller/service/BusinessLogic |
| `create-medium-tests` | tests d'intégration via `WebApplicationFactory` |
| `create-large-tests` | tests E2E Python pour une route de produit CFF |
| `create-internal-route` | scaffold d'une nouvelle route API interne (architecture clean) |
| `implement-full-story` | Definition-of-Done complète : route + tous les niveaux de test |
| `croesus-process-conventions` | conventions C# pour la base de code CroesusProcess |

Ceux-ci sont utiles *à l'intérieur* de la phase de build d'un `feature`/`bug` quand on travaille dans les repos C# du monolith.

## Commandes de plugin liées

Ne font pas partie de l'ensemble de ce workspace, mais interopérables — voir
[workflows.md → Relationship to code-fleet](workflows.md#relationship-to-code-fleet):
`/code-fleet:work`, `/code-fleet:review`, et les agents language-pack de `code-fleet`.
