# Workflows

Sept workflows, chacun étant une séquence de phases distincte accordée au *type* de travail. Tous partagent le
socle de `protocol.md` (répertoire de tâche, rassemblement du contexte, gates, HALT, règles par repo). Les gates sont
**interactifs** — l'orchestrateur s'arrête et attend l'approbation. `→` est une phase ; **[GATE]** est un
point d'arrêt-pour-approbation ; les agents sont nommés en `police de code`.

Chaque commande `/<workflow>` pilote la séquence ci-dessous. **Les sept sont des skills vivants** sous
`.claude/skills/` — invocables par le modèle, ou lancés avec `/feature`, `/bug`, `/refactor`, `/spike`,
`/explore`, `/investigate`, `/learn`. Chaque skill orchestre les agents de `../agents/` via
l'outil Agent et défère à ce fichier (son `§N`) et à `protocol.md` pour les règles faisant autorité.

---

## 1. `feature` — construire quelque chose de nouveau

> **spike ? → context → explore → plan → [GATE] → build → review → [GATE] → ship ? → retrospective**

| Phase | Agent | Sortie |
|---|---|---|
| 0. Spike (optionnel) | lancer d'abord le workflow `spike` *uniquement si* l'approche est véritablement inconnue | `spike.md` |
| 1. Context | `context-gatherer` | `context.md` |
| 2. Explore | `explorer` | `exploration.md` |
| 3. Plan | `planner` | `plan.md` (avec table de couverture d'exigences) |
| **GATE de plan** | — | barre de build : le plan doit être `ready` + noté **A/S** pour être approuvable (voir protocol.md) ; sinon approve / changes / cancel |
| 4. Build | `implementer` (ou `cpp-to-csharp-porter` pour les ports de value-provider ; un par repo/tranche) | code + tests, `build-summary.md` |
| 5. Review | `reviewer` (mode code) | `review-code.md` |
| **GATE de code** | — | approve / changes (boucle vers build, plafond 3) / cancel |
| 6. Ship (optionnel, gaté) | orchestrateur | branche + commit + PR **par repo git** — monolith et/ou pf-web (règles git de l'org) |
| 7. Retrospective | `retrospective` | `retro.md` + apprentissages proposés |

Notes : les features cross-repo exécutent la phase 4 dans l'ordre du pipeline (analyse C++ → C#/API → UI Angular). Le C++
et le C# partagent **une seule** branche/PR (monorepo `monolith`) ; pf-web a la sienne. Les sous-sections `#### <repo>` du plan indiquent à chaque `implementer` sa tranche.

**Variante migration de rapport.** Lorsque la feature consiste à *migrer un rapport de Conseiller (C++) vers Xpert*,
le skill `feature` bascule en **mode migration** (voir `../skills/feature/SKILL.md` §1a) : les gates
restent, mais les workers de phase sont les **agents de migration natifs** de ce workspace
(`.claude/agents/` : `report-analyst` → explore/plan, `backend-migrator` + `frontend-migrator` → build,
`migration-reviewer` + `migration-validator` → review), dispatchés en `subagent_type`, et non les
agents génériques. Leurs règles sont dans `.claude/conventions/{migration-protocol,backend-conventions,frontend-conventions}.md`.
Tous les **livrables** d'une migration (analysis, logs, review, PDF) vivent sous
`.work/{slug}/` — `{slug}` = la clé Jira, sinon le nom interne du rapport. `docs/reports/` n'est qu'une archive
versionnée des livrables finaux, alimentée sur demande (voir `migration-protocol.md`).
Les entrées globales partagées restent sous `docs/` (`fields.csv`, `template_ids.csv`).

---

## 2. `bug` — corriger un défaut

> **context → reproduce → diagnose → plan-fix → [GATE] → build → verify+review → [GATE] → ship ? → retrospective**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Context | `context-gatherer` | `context.md` (rapport de bug, étapes de repro, PR liées) |
| 2. Reproduce | orchestrateur (+ `explorer` pour localiser) | un test en échec ou une repro documentée dans `bug-diagnosis.md` |
| 3. Diagnose | `investigator` | cause racine + preuves dans `bug-diagnosis.md` |
| 4. Plan fix | `planner` (portée sur la correction, minimale) | `plan.md` |
| **GATE de plan** | — | barre de build : le plan doit être `ready` + noté **A/S** (voir protocol.md) ; allégé pour les petites corrections, mais la barre tient toujours sauf passage outre explicite |
| 5. Build | `implementer` / `cpp-to-csharp-porter` | correction + **test de régression qui échoue avant, passe après**, `build-summary.md` |
| 6. Verify + review | `reviewer` (mode code) | confirme que la repro a disparu ; `review-code.md` |
| **GATE de code** | — | approve / changes / cancel |
| 7. Ship (optionnel) | orchestrateur | branche + commit + PR |
| 8. Retrospective | `retrospective` | `retro.md` — **doit** inclure la classe de cause racine pour que des bugs similaires soient attrapés plus tôt |

La règle distinctive : **pas de correction sans une reproduction et un test de régression**. Le diagnostic
(phase 3) est obligatoire et séparé de la correction — ne rafistole pas les symptômes.

---

## 3. `refactor` — changer la structure, pas le comportement

> **context → explore → characterize → plan → [GATE] → build (petites étapes) → review → [GATE] → ship ? → retrospective**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Context | `context-gatherer` | `context.md` (pourquoi refactorer, contraintes) |
| 2. Explore | `explorer` | `exploration.md` — cartographier le rayon d'impact / les consommateurs |
| 3. Characterize | orchestrateur + `implementer` | un **filet de sécurité de tests** capturant le comportement actuel *avant* d'y toucher ; noter les lacunes |
| 4. Plan | `planner` | `plan.md` — étapes ordonnées, **préservant le comportement** ; surfaces de changement cassant explicites |
| **GATE de plan** | — | barre de build : le plan doit être `ready` + noté **A/S** pour être approuvable (voir protocol.md) ; sinon approve / changes / cancel |
| 5. Build | `implementer` | petites étapes vérifiées individuellement ; **build+tests verts après chacune** |
| 6. Review | `reviewer` | `review-code.md` — vérifier l'absence de changement de comportement + l'absence de dérive de contrat |
| **GATE de code** | — | approve / changes / cancel |
| 7. Ship (optionnel) | orchestrateur | branche + commit + PR |
| 8. Retrospective | `retrospective` | `retro.md` |

Règle distinctive : **le comportement ne doit pas changer**. Les tests de caractérisation (phase 3) viennent *avant*
toute édition ; les refactors de ReportFoundations doivent signaler chaque consommateur en aval.

---

## 4. `spike` — investigation en timebox pour réduire l'incertitude

> **frame + timebox → investigate (jetable) → findings → [GATE : décider]**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Frame | orchestrateur | la question à répondre + un timebox + ce que « done » signifie |
| 2. Context | `context-gatherer` (léger) | `context.md` si un ticket existe |
| 3. Investigate | `explorer` + `investigator` (+ prototypes jetables, isolés) | preuves, notes de prototype |
| 4. Findings | orchestrateur | `spike.md` — options, arbitrages, une **recommandation**, et le coût/risque de chacune |
| **GATE de décision** | — | choisir une option → alimente généralement un workflow `feature` ou `refactor` |

Règles distinctives : **pas de code de production** (les prototypes sont jetables et ne doivent pas être shippés) ;
en timebox ; le livrable est une décision, pas un merge. Consigne les apprentissages durables en mémoire même
s'il n'y a pas de phase de rétrospective.

---

## 5. `explore` — comprendre où/quoi (lecture seule)

> **scope → map → answer**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Scope | orchestrateur | reformuler la question + repos candidats |
| 2. Map | `explorer` | `exploration.md` (ou inline) — carte `repo/path:line` + flux |

Pas de gates, pas de build, pas de ship. À utiliser pour s'orienter avant une feature/refactor, ou pour répondre à « où vit X
/ comment Y circule-t-il à travers les repos ». Rapide et bon marché.

---

## 6. `investigate` — comprendre pourquoi (lecture seule, plus profond)

> **frame → gather evidence → hypothesize → verify → conclude**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Frame | orchestrateur | la question / l'incident précis |
| 2. Context | `context-gatherer` | `context.md` (tickets, PR liées, historique) |
| 3. Analyze | `investigator` | `investigation.md` — preuves → hypothèses (avec verdicts) → cause racine → confiance |

Pas de gates, pas de build. Plus profond que `explore` : il répond au *pourquoi/comment*, en écartant les alternatives avec
l'historique git, les logs et le code. Souvent la première moitié d'un workflow `bug` quand la cause est inconnue.

---

## 7. `learn` — construire un modèle mental (lecture seule, pédagogique)

> **pick target + level → guided walkthrough → glossary → exercises**

| Phase | Agent | Sortie |
|---|---|---|
| 1. Target | orchestrateur | sous-système/concept + niveau actuel de l'apprenant |
| 2. Teach | `learning-guide` | `learning-notes.md` — vue d'ensemble → trace du chemin nominal → abstractions clés → glossaire → exercices sûrs |

Pas de gates, pas de build. Pour l'onboarding sur le pipeline de rapports ou une zone spécifique (paramètres
value-provider, le flux batch du Spooler, le layering DDD de pf-web, le mécanisme de port C++→C#).

---

## Choisir un workflow

| Si la tâche est… | Utiliser |
|---|---|
| ajouter/changer un comportement destiné à l'utilisateur ou d'API | `feature` |
| quelque chose est cassé / mauvaise sortie | `bug` |
| améliorer la structure, garder le comportement | `refactor` |
| « devrait-on… ? » / approche inconnue / évaluer une option | `spike` |
| « où est / comment X circule-t-il ? » | `explore` |
| « pourquoi / comment est-ce arrivé ? » | `investigate` |
| « aide-moi à comprendre cette zone » | `learn` |

En cas de doute entre `bug` et `investigate` : si tu sais déjà que c'est cassé et que tu veux le corriger →
`bug` (qui exécute le diagnostic de `investigate` en phase 3). Si tu veux seulement comprendre un
comportement → `investigate`.

## Relation avec `code-fleet`

Cet ensemble s'inspire du plugin `code-fleet` de l'org et interopère avec lui. Là où tu préfères
t'appuyer sur les language packs matures de la fleet, les phases **build + review** de `feature`/`refactor` peuvent être
déléguées à `/code-fleet:work` (son pipeline `compass`→`lookout`→`dot-coder`/`ts-coder`→reviewers)
au lieu des `planner`/`implementer`/`reviewer` du workspace. Les agents du workspace ajoutent ce que la fleet
n'a pas : la conscience de la topologie multi-repos des rapports, le `cpp-to-csharp-porter`, et les rôles en lecture seule
`explore`/`investigate`/`learn` et `retrospective`. À noter, code-fleet écrit dans
`.claude/work/<slug>/` tandis que cet ensemble utilise `.work/<slug>/`.
