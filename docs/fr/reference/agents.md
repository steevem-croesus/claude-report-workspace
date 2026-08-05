# Référence — Agents

Neuf agents vivent sous [`.claude/agents/`](../../../.claude/agents/), dispatchés via l'outil Agent par
les skills de workflow. Chacun porte une persona d'ingénierie de niveau distinguished/fellow et un rôle
étroit. Ils se répartissent en **read-only** (ne modifient jamais le code) et **editing**.

| Agent | Rôle | Read-only ? | Modèle | Écrit |
|---|---|---|---|---|
| [`context-gatherer`](#context-gatherer) | intel Jira + GitHub | ✅ | Sonnet | `context.md` |
| [`explorer`](#explorer) | carte de code cross-repo | ✅ | Sonnet | `exploration.md` |
| [`investigator`](#investigator) | analyse de cause racine | ✅ | Opus | `investigation.md` / `bug-diagnosis.md` |
| [`learning-guide`](#learning-guide) | walkthrough pédagogique | ✅ | Sonnet | `learning-notes.md` |
| [`reviewer`](#reviewer) | review de plan/code | ✅ | Opus | `review-plan.md` / `review-code.md` |
| [`retrospective`](#retrospective) | capturer les apprentissages | ✅ (code) | Sonnet | `retro.md` |
| [`planner`](#planner) | plan d'implémentation | écrit `plan.md` uniquement | Opus | `plan.md` |
| [`implementer`](#implementer) | build + test | ✏️ modifie le code | Opus | code, tests, `build-summary.md` |
| [`cpp-to-csharp-porter`](#cpp-to-csharp-porter) | port C++→C# de value-provider | ✏️ modifie le code | Opus | code, tests, `build-summary.md` |

Tous les agents obéissent aux [garde-fous](gates-and-protocol.md#garde-fous-chaque-agent-chaque-phase) partagés : ne jamais exécuter
de CLI org-denied (`aws`, `terraform`/`tofu`), respecter le `CLAUDE.md` propre à chaque repo, et les agents
read-only ne modifient jamais.

## Modèle par agent

Chaque agent épingle son propre modèle via un champ `model:` dans le frontmatter de son
[`.claude/agents/*.md`](../../../.claude/agents/), hiérarchisé selon ce que le rôle exige réellement :

- **Opus** — `planner`, `implementer`, `cpp-to-csharp-porter`, `reviewer`, `investigator` : tout ce
  qui conçoit le changement, écrit ou porte du code, juge la qualité, ou fait du raisonnement de cause
  racine. Ce sont les rôles critiques pour la correction, à fort enjeu — le plan qui gate le build, le
  port C++→C# financier/de date, la review dont dépend la barre de build.
- **Sonnet** — `context-gatherer`, `explorer`, `learning-guide`, `retrospective` : les rôles read-only
  de collecte / cartographie / enseignement / résumé. Largement capables, plus rapides et moins chers.

Pour changer un niveau, modifie la valeur `model:` de cet agent (`opus` / `sonnet` / `haiku`, ou `inherit`
pour suivre le modèle de ta session). Comme le champ vit dans le frontmatter de l'agent, le choix s'applique
partout où l'agent est dispatché, dans chaque workflow.

---

## context-gatherer

- **Rôle :** assembler un brief de Contexte fidèle et cité avant que quiconque n'écrive du code. Ne conçoit
  *pas*, n'estime pas, n'écrit pas de code de production.
- **Invoqué :** en premier, dans chaque exécution `feature`/`bug`/`refactor`/`spike`/`investigate`.
- **Entrées :** une clé Jira, une référence GitHub (`#123` / URL), ou une tâche en texte libre.
- **Outils :** Read, Write, Grep, Glob, Bash, WebFetch, et Atlassian MCP (`getAccessibleAtlassianResources`,
  `getJiraIssue`, `searchJiraIssuesUsingJql`, `getJiraIssueRemoteIssueLinks`, fetch Confluence).
- **Procédure :** résoudre le ticket Jira (résumé, description, commentaires, critères d'acceptation, liens,
  specs Confluence référencées) → résoudre le contexte GitHub via `gh` dans le repo pertinent → recouper
  demandé-vs-existant et signaler les contradictions.
- **Sortie :** `context.md` (template :
  [`templates/context.md`](../../../.claude/conventions/templates/context.md)) + un résumé nommant le/les
  repo(s) cible(s) et les 3 principales questions ouvertes.
- **Garde-fou :** read-only aussi sur Jira/GitHub — ne commente jamais un ticket ni ne le transitionne, n'ouvre
  jamais de PR. S'il ne peut pas atteindre Jira/GitHub, il le dit et travaille à partir des preuves locales ;
  ne fabrique jamais.

## explorer

- **Rôle :** localiser et cartographier le code à travers les repos pour que les autres s'orientent vite.
  Cartographie ; ne juge pas et ne propose pas de correctifs.
- **Invoqué :** workflow `explore` ; début de `feature`/`refactor` ; partout où une carte de code est nécessaire.
- **Outils :** Read, Grep, Glob, Bash.
- **Heuristique notable :** quand une feature lit de la config/des données « default »/de setup, il ne s'arrête
  pas au helper évident — il trace aussi le **chemin de découverte repository / Flex « scenario »**
  (`I*Repository.BuildScenarioData`, `Get*SetupConfig`), parce que le chemin de génération résout souvent les
  données via un scenario que le helper côté query masque. Il signale aussi les surfaces partagées (interfaces
  qui pourraient devoir devenir génériques, classes de base à extraire) quand une feature ajoute un flow
  **à côté** d'un flow existant.
- **Sortie :** un tableau `repo/path:line` groupé par repo + flow en prose + 2–3 meilleurs points d'entrée →
  `exploration.md` (ou en ligne pour les questions rapides).

## investigator

- **Rôle :** trouver la *cause racine* d'un défaut/comportement avec des preuves, pas de la plausibilité.
  Explique ; ne corrige pas.
- **Invoqué :** workflow `investigate` ; la phase de diagnostic de `bug`.
- **Outils :** Read, Grep, Glob, Bash, WebFetch.
- **Procédure :** cadrer → rassembler les preuves (code, `git log`/`git blame`/`git log -S`, tickets/PRs,
  logs) → formuler des hypothèses → **vérifier de manière adversariale** (essayer de réfuter l'hypothèse
  principale ; distinguer le déclencheur de la cause racine) → conclure avec un niveau de confiance
  (high/medium/low).
- **Sortie :** `investigation.md` (ou `bug-diagnosis.md` dans un bug) : symptôme → preuves → hypothèses
  (avec verdicts) → cause racine → confiance → questions ouvertes. Chaque affirmation citée.

## learning-guide

- **Rôle :** rendre un nouveau venu productif dans un domaine choisi, en enseignant à partir du code réel.
- **Invoqué :** workflow `learn`.
- **Outils :** Read, Grep, Glob, Bash, WebFetch.
- **Sortie :** `learning-notes.md` — vue d'ensemble → trace du happy-path (`repo/path:line`) → abstractions
  clés → glossaire (`PREF_`, `PARAM_`, spooler, value-provider, `generationId`, …) → 2–4 exercices sûrs,
  read-only/jetables → où aller ensuite.

## reviewer

- **Rôle :** review adversariale et concise. Pas d'éloges, pas de résumés, pas de scope creep.
- **Invoqué :** le gate de plan (mode plan) et le gate de code (mode code) de `feature`/`bug`/`refactor`.
- **Outils :** Read, Grep, Glob, Bash (peut builder/exécuter des tests pour vérifier un constat — non mutant).
- **Deux modes :**
  - **Review de plan** — le plan satisfait-il sa table de couverture des exigences ? Le placement/layering
    est-il correct, les risques/tests/estimation sont-ils réalistes, et — surtout — **le Grade + Status
    auto-attribués sont-ils honnêtes ?** Un plan sur-noté ou marqué `ready` à tort est un must-fix, parce que
    la barre de build en dépend.
  - **Review de code** — bugs de correction, violations de layering, tests faibles/manquants, dérive de
    contrat cross-repo, fidélité C++→C#.
- **Sortie :** une ligne par constat — `repo/path:line: <emoji> <severity>: <problem>. <fix>.` —
  sévérités 🔴 must-fix / 🟡 should-fix / 🟢 consider ; une ligne **Don't miss** ; un verdict (`clean` /
  `should-fix only` / `must-fix present`) → `review-plan.md` ou `review-code.md`.

## retrospective

- **Rôle :** transformer un travail terminé en connaissance durable. Ne modifie pas le code de production.
- **Invoqué :** dernière phase de `feature`/`bug`/`refactor`.
- **Outils :** Read, Glob, Grep, Bash, Write.
- **Sortie :** `retro.md` (template :
  [`templates/retro.md`](../../../.claude/conventions/templates/retro.md)) — ce qui a été shippé, plan vs
  réalité, ce qui s'est bien/mal passé, *classe* de cause racine (bugs uniquement), suivis, et 1–4 apprentissages
  durables **proposés** (entrées de mémoire + éditions doc/CLAUDE.md) sous forme de checklist. **N'écrit jamais
  la mémoire ni ne modifie la doc lui-même** — il fait remonter la checklist pour que tu l'approuves.

## planner

- **Rôle :** concevoir le changement avant qu'une ligne ne soit écrite. N'écrit pas de code de production.
- **Invoqué :** la phase de plan de `feature`/`bug`/`refactor` (après contexte + exploration).
- **Outils :** Read, Grep, Glob, Bash, Write.
- **Honore les règles d'architecture :** layering DDD de pf-web ; architecture clean de ReportManagerApi +
  la recette du value-provider ; call-outs de surfaces cassantes de ReportFoundations (et la vérification
  de la route de découverte — vérifier si le chemin de *génération* résout les données via un scenario Flex
  avant de sortir RF du scope) ; reshape shared-base/interface de parallel-flow comme point de décision de
  premier plan.
- **Sortie :** `plan.md` (template :
  [`templates/plan.md`](../../../.claude/conventions/templates/plan.md)) avec un **en-tête Status/Grade**,
  Problème, Couverture des exigences, Zones affectées, Étapes (groupées `#### <repo>` pour le multi-repo), Tests,
  Risques, Points de décision (`resolved`/`needs-user`), Estimation (tailles T-shirt + confiance), Questions
  ouvertes.
- **La barre de build :** note sur **F < D < C < B < A < S** ; marque `draft` sauf si honnêtement `ready` +
  (A|S). **Ne gonfle jamais le grade pour passer le gate** — voir
  [gates & la barre de build](../explanation/gates-and-the-build-bar.md).
- **HALT :** s'arrête et demande sur une véritable bifurcation plutôt que de deviner.

## implementer

- **Rôle :** transformer un plan approuvé en code fonctionnel et testé à travers C#/.NET, Angular/TypeScript, ou
  C++. Ne re-planifie pas et ne dépasse pas le scope du plan.
- **Invoqué :** la phase de build (et de characterize de refactor), par tranche de repo — *sauf* les ports de
  value-provider, qui vont au porter.
- **Outils :** Read, Glob, Grep, Edit, Write, Bash, `mcp__ide__getDiagnostics`.
- **Discipline :** respecter exactement les conventions du `CLAUDE.md` du repo cible ; écrire les tests dans le
  tier/style du repo ; **toujours builder puis exécuter les tests écrits avant de retourner** et rapporter la
  sortie réelle des commandes ; `git add`-stager les nouveaux fichiers mais **ne pas committer**.
- **Sortie :** `build-summary.md` — fichiers modifiés par repo, tests ajoutés, commandes exactes + résultats,
  déviations. Résultat ∈ `ok` / `tests-failed` / `build-failed`.
- **HALT :** s'arrête si le plan est ambigu ou contredit le code.

## cpp-to-csharp-porter

- **Rôle :** le spécialiste de la réimplémentation d'une fonction de rapport C++ en `IValueProviderParameter` C#
  dans ReportManagerApi. Suit [`copilot-instructions.md`](../../../repos/ReportManagerApi/copilot-instructions.md)
  exactement.
- **Invoqué :** la phase de build quand une étape est un port de value-provider (à l'intérieur de `feature`/`bug`), ou
  en autonome.
- **Outils :** Read, Glob, Grep, Edit, Write, Bash, `mcp__ide__getDiagnostics`.
- **Procédure & mapping des dépendances :** voir le guide pratique,
  [porter une fonction C++ vers C#](../how-to/port-cpp-to-csharp.md).
- **Sortie :** `build-summary.md` — source C++ (`repo/path:line`) + sémantique, la classe C# + les deps
  injectées, la ligne d'executer ajoutée, tout ajout de `IDateTimeService`, tests, résultats de build/test, et tout
  comportement C++ qu'il n'a **pas** pu reproduire fidèlement.
- **Garde-fou :** fidélité d'abord — le C# doit correspondre à la sémantique du C++ ; les divergences délibérées sont
  signalées. HALT plutôt que de deviner la logique financière/de date.
