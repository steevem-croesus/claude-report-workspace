# Référence — Workflows

Sept workflows, chacun accordé à un *type* de travail. **Source faisant autorité :**
[`.claude/conventions/workflows.md`](../../.claude/conventions/workflows.md) — elle détaille chaque phase,
l'agent qui la porte et l'artefact produit. Cette page n'en donne que la vue d'ensemble : ne recopiez pas
les tables de phases ici, elles dériveraient.

| Si la tâche est… | Workflow | Gaté |
|---|---|---|
| ajouter ou changer un comportement visible ou une API | `/feature` | oui |
| quelque chose est cassé, mauvaise sortie | `/bug` | oui |
| améliorer la structure sans changer le comportement | `/refactor` | oui |
| « devrait-on… ? », approche inconnue | `/spike` | gate de décision |
| « où est X, comment circule Y ? » | `/explore` | non |
| « pourquoi, comment est-ce arrivé ? » | `/investigate` | non |
| « aide-moi à comprendre cette zone » | `/learn` | non |

Les trois workflows gatés partagent deux gates — le **gate de plan**, précédé d'une revue du plan par le
reviewer, et le **gate de code**, suivi de la rétrospective. Voir [gates & protocole](gates-and-protocol.md).

## 1. feature

> *(spike ?) → context → explore → plan → review-plan → **[GATE]** → build → review → **[GATE]** → retrospective → ship ?*

Les features cross-stack se construisent dans l'ordre du pipeline (C++ → C#/API → Angular) : le C++ et le C#
partagent une branche et une PR dans le monorepo `monolith`, pf-web a les siennes. La **migration d'un
rapport** de Conseiller vers Xpert passe par ce workflow en *mode migration*, avec les agents de migration
à la place des agents génériques. Guide : [exécuter le workflow feature](../how-to/run-the-feature-workflow.md).

## 2. bug

> *context → reproduce → diagnose → plan-fix → review-plan → **[GATE]** → build → verify+review → **[GATE]** → retrospective → ship ?*

Règle distinctive : pas de correction sans reproduction ni test de régression qui échoue avant et passe
après. Le diagnostic est une phase à part. Guide : [corriger un bug](../how-to/fix-a-bug.md).

## 3. refactor

> *context → explore → characterize → plan → review-plan → **[GATE]** → build (petites étapes) → review → **[GATE]** → retrospective → ship ?*

Règle distinctive : le comportement ne change pas. Les tests de caractérisation viennent avant toute
édition, et build + tests restent verts après chaque étape.

## 4. spike

> *frame + timebox → context → investigate (jetable) → findings → **[GATE : décider]***

Le livrable est une décision (`spike.md`), pas du code : les prototypes sont jetables.

## 5. explore

> *scope → map → answer*

Lecture seule, sans gate. Produit une carte `repo/chemin:ligne` (`exploration.md` ou réponse directe).

## 6. investigate

> *frame → context → analyze → conclude*

Lecture seule, sans gate. Plus profond qu'`explore` : il répond au *pourquoi* en écartant les alternatives
(`investigation.md`). C'est aussi la phase de diagnostic du workflow `bug`.

## 7. learn

> *pick target + level → guided walkthrough → glossary → exercises*

Lecture seule, pédagogique (`learning-notes.md`).

## Relationship to code-fleet

Cet ensemble s'inspire du plugin `code-fleet` de l'org et interopère avec lui : les phases build + review
de `feature` et `refactor` peuvent lui être déléguées (`/code-fleet:work`). Les agents du workspace ajoutent
la topologie multi-repos des rapports, le `cpp-to-csharp-porter`, les rôles en lecture seule et la
`retrospective`. À noter : code-fleet écrit dans `.claude/work/<slug>/`, ce workspace dans `.work/<slug>/`.
