# Référence — Workflows

Sept workflows, chacun une séquence de phases ajustée à un *type* de travail. Tous partagent la fondation dans
[gates & protocole](gates-and-protocol.md). Notation : `→` est une phase ; **[GATE]** est un point
d'arrêt-pour-approbation ; les agents sont nommés en `code`.

**Source faisant autorité :** [`.claude/conventions/workflows.md`](../../../.claude/conventions/workflows.md).
Chaque workflow est aussi un skill vivant sous `.claude/skills/` (voir [skills](skills.md)), invocable comme
`/feature`, `/bug`, `/refactor`, `/spike`, `/explore`, `/investigate`, `/learn`.

| # | Workflow | Gated | Écrit du code | En une ligne |
|---|---|---|---|---|
| 1 | [feature](#1-feature) | ✅ | ✅ | construire quelque chose de nouveau |
| 2 | [bug](#2-bug) | ✅ | ✅ | corriger un défaut (repro + test de régression requis) |
| 3 | [refactor](#3-refactor) | ✅ | ✅ | changer la structure, pas le comportement |
| 4 | [spike](#4-spike) | ✅ (décision) | ✗ (jetable) | investigation timeboxée → décision |
| 5 | [explore](#5-explore) | ✗ | ✗ | cartographier où/quoi (read-only) |
| 6 | [investigate](#6-investigate) | ✗ | ✗ | cause racine pourquoi/comment (read-only) |
| 7 | [learn](#7-learn) | ✗ | ✗ | construire un modèle mental (read-only) |

---

## 1. feature

> *(spike?) → context → explore → plan → **[GATE]** → build → review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Sortie |
|---|---|---|
| 0. Spike (optionnel) | exécuter `spike` d'abord *seulement si* l'approche est véritablement inconnue | `spike.md` |
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Explore | [`explorer`](agents.md#explorer) | `exploration.md` |
| 3. Plan | [`planner`](agents.md#planner) | `plan.md` (+ table de couverture des exigences) |
| **Plan GATE** | — | barre de build : `ready` + **A/S** pour être approuvable ; sinon changes / cancel |
| 4. Build | [`implementer`](agents.md#implementer) ou [`cpp-to-csharp-porter`](agents.md#cpp-to-csharp-porter) ; un par tranche de repo | code + tests, `build-summary.md` |
| 5. Review | [`reviewer`](agents.md#reviewer) (mode code) | `review-code.md` |
| **Code GATE** | — | approve / changes (boucle vers build, plafond 3) / cancel |
| 6. Ship (optionnel, gated) | orchestrateur | branch + commit + PR **par repo** |
| 7. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` + apprentissages proposés |

Les features cross-repo exécutent la phase 4 dans l'ordre du pipeline (analyse C++ → C#/API → UI Angular), chaque repo sur
sa propre branche/PR. Guide pratique : [exécuter le workflow feature](../how-to/run-the-feature-workflow.md).

**Variante report-migration.** Si la feature consiste à migrer un rapport de Conseiller (C++) vers Xpert,
`/feature` bascule en **mode migration** (`.claude/skills/feature/SKILL.md` §1a) : les gates restent, mais
les workers de phase deviennent les **agents de migration natifs** de ce workspace
(`.claude/agents/`) — `report-analyst` pour explore/plan, `backend-migrator` + `frontend-migrator` pour
build, `migration-reviewer` + `migration-validator` pour review — dispatchés en `subagent_type`. Leurs
règles vivent dans `.claude/conventions/{migration-protocol,backend-conventions,frontend-conventions}.md`.
Tous les **livrables** d'une migration (analysis, logs, review, PDF) vivent sous
`.work/{slug}/` — `{slug}` = la clé Jira, sinon le nom interne du rapport. `docs/reports/` n'est qu'une archive
versionnée des livrables finaux, alimentée sur demande (voir `migration-protocol.md`).
Les entrées globales partagées restent sous `docs/` (`fields.csv`, `template_ids.csv`).

---

## 2. bug

> *context → reproduce → diagnose → plan-fix → **[GATE]** → build → verify+review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Sortie |
|---|---|---|
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Reproduce | orchestrateur (+ [`explorer`](agents.md#explorer) pour localiser) | test échouant / repro dans `bug-diagnosis.md` |
| 3. Diagnose | [`investigator`](agents.md#investigator) | cause racine + preuves dans `bug-diagnosis.md` |
| 4. Plan fix | [`planner`](agents.md#planner) (minimal) | `plan.md` |
| **Plan GATE** | — | la barre de build s'applique |
| 5. Build | [`implementer`](agents.md#implementer) / [`cpp-to-csharp-porter`](agents.md#cpp-to-csharp-porter) | correctif + **test de régression (échoue avant, passe après)**, `build-summary.md` |
| 6. Verify + review | [`reviewer`](agents.md#reviewer) | confirme que le repro a disparu ; `review-code.md` |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optionnel) | orchestrateur | branch + commit + PR |
| 8. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` — **doit** inclure la classe de cause racine |

Règle distinctive : **pas de correctif sans une reproduction et un test de régression.** Le diagnostic (phase 3) est
obligatoire et séparé du correctif. Guide pratique : [corriger un bug](../how-to/fix-a-bug.md).

---

## 3. refactor

> *context → explore → characterize → plan → **[GATE]** → build (small steps) → review → **[GATE]** → ship? → retrospective*

| Phase | Agent | Sortie |
|---|---|---|
| 1. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 2. Explore | [`explorer`](agents.md#explorer) | `exploration.md` — le blast radius / les consommateurs |
| 3. Characterize | orchestrateur + [`implementer`](agents.md#implementer) | tests de filet de sécurité épinglant le comportement actuel *avant* toute édition |
| 4. Plan | [`planner`](agents.md#planner) | `plan.md` — étapes ordonnées, préservant le comportement ; surfaces cassantes explicites |
| **Plan GATE** | — | la barre de build s'applique |
| 5. Build | [`implementer`](agents.md#implementer) | petites étapes ; **build+tests verts après chacune** |
| 6. Review | [`reviewer`](agents.md#reviewer) | `review-code.md` — vérifier aucun changement de comportement / aucune dérive de contrat |
| **Code GATE** | — | approve / changes / cancel |
| 7. Ship (optionnel) | orchestrateur | branch + commit + PR |
| 8. Retrospective | [`retrospective`](agents.md#retrospective) | `retro.md` |

Règle distinctive : **le comportement ne doit pas changer.** Les tests de caractérisation viennent *avant* toute édition ; un
refactor de `ReportFoundations` doit nommer chaque consommateur en aval.

---

## 4. spike

> *frame + timebox → context (light) → investigate (throwaway) → findings → **[GATE: decide]***

| Phase | Agent | Sortie |
|---|---|---|
| 1. Frame | orchestrateur | la question + un timebox + ce que « done » signifie |
| 2. Context (light) | [`context-gatherer`](agents.md#context-gatherer) | `context.md` si un ticket existe |
| 3. Investigate | [`explorer`](agents.md#explorer) + [`investigator`](agents.md#investigator) (+ prototypes jetables isolés) | preuves, notes de prototype |
| 4. Findings | orchestrateur | `spike.md` — options, compromis, une **recommandation** |
| **Decision GATE** | — | choisir une option → alimente généralement un `feature` ou un `refactor` |

Règles distinctives : **pas de code de production** (les prototypes sont jetables et isolés) ; **timeboxé** ;
le livrable est une **décision**, pas un merge. Pas de phase de rétrospective, mais les apprentissages durables sont quand même
capturés en mémoire (avec approbation).

---

## 5. explore

> *scope → map → answer*

| Phase | Agent | Sortie |
|---|---|---|
| 1. Scope | orchestrateur | question reformulée + repos candidats |
| 2. Map | [`explorer`](agents.md#explorer) | `exploration.md` (ou en ligne) — carte `repo/path:line` + flow |

Pas de gates, pas de build, pas de ship. Répond à *où vit X / comment Y circule à travers les repos*. Bon marché ; une
petite tâche one-off peut sauter le répertoire de tâche. Guide pratique : [choisir un workflow](../how-to/choose-a-workflow.md).

---

## 6. investigate

> *frame → context → analyze → conclude*

| Phase | Agent | Sortie |
|---|---|---|
| 1. Frame | orchestrateur | la question / l'incident précis |
| 2. Context | [`context-gatherer`](agents.md#context-gatherer) | `context.md` |
| 3. Analyze | [`investigator`](agents.md#investigator) | `investigation.md` — preuves → hypothèses (avec verdicts) → cause racine → confiance |

Pas de gates, pas de build. Plus profond qu'`explore` : répond au *pourquoi/comment*, en écartant les alternatives avec l'historique
git, les logs, et le code. Souvent la première moitié d'un `bug`.

---

## 7. learn

> *pick target + level → guided walkthrough → glossary → exercises*

| Phase | Agent | Sortie |
|---|---|---|
| 1. Target | orchestrateur | sous-système/concept + niveau actuel de l'apprenant |
| 2. Teach | [`learning-guide`](agents.md#learning-guide) | `learning-notes.md` — vue d'ensemble → trace du happy-path → abstractions clés → glossaire → exercices sûrs |

Pas de gates, pas de build. Pour l'onboarding sur le pipeline ou un domaine spécifique.

---

## Relationship to code-fleet

Cet ensemble est inspiré par et interopère avec le plugin `code-fleet` de l'org. Les phases **build + review**
de `feature`/`refactor` peuvent être déléguées à `/code-fleet:work` (son
pipeline `compass`→`lookout`→`dot-coder`/`ts-coder`→reviewers). Les agents du workspace ajoutent ce que
la fleet n'a pas : la conscience de la topologie de rapport multi-repo, le `cpp-to-csharp-porter`, et les rôles read-only
`explore`/`investigate`/`learn` + `retrospective`. Note : code-fleet écrit dans
`.claude/work/<slug>/` ; cet ensemble utilise `.work/<slug>/`.
