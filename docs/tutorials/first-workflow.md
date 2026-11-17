# Your first workflow

Ce tutoriel te fait parcourir deux exécutions, la plus petite d'abord, pour que tu *voies* comment les workflows se comportent
avant de compter sur l'un d'eux pour du vrai travail :

1. un **`/explore` en lecture seule** — pas de gates, pas de risque, produit une carte du code ;
2. une exécution de **`/feature`** — la séquence gated complète, pour que tu rencontres le plan gate, le build, le code
   gate, et la retrospective.

À la fin, tu reconnaîtras le rythme phase par phase et sauras où atterrit chaque artefact. Rien
ici ne modifie un repo produit sans ton approbation.

> C'est une *leçon*, pas une référence. Suis-la dans l'ordre. Une fois que ça fait tilt, les
> [Guides how-to](../how-to/) sont le chemin le plus rapide pour les vraies tâches.

---

## Part 1 — Map some code with `/explore`

`explore` est le workflow le plus sûr : lecture seule, pas de gates, rapide. Parfait pour une première exécution.

### Step 1 — Invoke it

Dans le prompt de Claude Code, tape :

```
/explore where does the report generation request enter ReportManagerApi and what does it call?
```

Tu peux aussi simplement *demander* en langage naturel (« where does…? ») et Claude choisira le workflow `explore`
— mais taper `/explore` rend le choix explicite pendant que tu apprends.

### Step 2 — Watch the phases

Le skill `explore` exécute une courte séquence (voir
[Référence : workflows §5](../reference/workflows.md#5-explore)) :

1. **Scope** — Claude reformule ta question en une ligne et nomme les *repos candidats* qu'il pense
   être en jeu (ici : `ReportManagerApi`, peut-être `ReportFoundations`).
2. **Map** — il dispatche l'agent [`explorer`](../reference/agents.md#explorer), qui cherche
   à travers les repos et retourne une carte `repo/path:line` plus un court flux en prose.

### Step 3 — Read the result

Tu obtiens une carte d'entrées `repo/path:line` cliquables et une description du flux en langage clair. C'est
là tout le livrable — il n'y a **pas de plan, pas de build, pas de gate**. Remarque comme c'était peu coûteux.

✅ **Tu as appris :** un workflow en lecture seule ne fait que répondre puis s'arrête. Passons maintenant à un workflow gated.

---

## Part 2 — Build something with `/feature`

`feature` est le playbook gated complet. Même pour un changement trivial, il exécute les mêmes phases, c'est donc le
meilleur pour apprendre. (Voir [Référence : workflows §1](../reference/workflows.md#1-feature).)

### Step 1 — Invoke it

```
/feature add a `reportFormat` query parameter to GET /api/v1/reports/{generationId} so callers can request PDF or XLSX
```

(Tu n'as pas à *ship* ceci — tu annuleras avant que le changement soit commité. Le but est de voir
la machinerie.)

### Step 2 — Setup & Context

Claude dérive un **slug** pour la tâche (une clé Jira si ton texte en contient une comme `RPT-12345`,
sinon un nom en kebab-case) et crée un répertoire de tâche : `.work/<slug>/`. C'est là que vit chaque
artefact de cette tâche — voir [Référence : le répertoire de tâche](../reference/task-directory.md).

Puis il dispatche [`context-gatherer`](../reference/agents.md#context-gatherer), qui tire tout
contexte Jira/GitHub et écrit `context.md`. Sans ticket, il le dit et travaille depuis les preuves
locales — il n'invente jamais le contenu d'un ticket.

### Step 3 — Explore

Ensuite il dispatche [`explorer`](../reference/agents.md#explorer) (le même agent que dans la Part 1) pour cartographier
le code affecté, en écrivant `exploration.md`.

### Step 4 — Plan, and meet the **plan gate**

[`planner`](../reference/agents.md#planner) écrit `plan.md` — avec une table de couverture des exigences,
des étapes ordonnées, des tests, des risques, et une estimation. Point crucial, le plan porte un en-tête comme :

Deux fichiers comptent ici. `plan.md` s'ouvre par le statut que le planner déclare, et `review-plan.md` par le
verdict du reviewer :

```
**Status:** ready          ← plan.md
**Buildable:** yes         ← review-plan.md
```

C'est la **barre de build**. Claude te laissera *seulement* approuver-pour-build un plan `ready` **et** jugé
`Buildable: yes` — le reviewer répond oui ou non à huit critères, preuve à l'appui. Si l'un est à « non », le
gate ne propose pas approve : il te montre lequel et pourquoi. Voir
[Explication : les gates & la barre de build](../explanation/gates-and-the-build-bar.md).

Au gate on te demandera (via un prompt à choix multiple) : **approve / request changes / cancel**.

- Essaie **request changes** une fois — tape quelque chose comme « also mention how the format maps to the S3
  content-type ». Regarde Claude re-dispatcher le planner et revenir au gate avec un plan révisé.
- Cette fois, s'il est `ready` + `Buildable: yes`, choisis **approve**.

### Step 5 — Build

[`implementer`](../reference/agents.md#implementer) reprend les étapes du plan, écrit le code et
les tests, **build et exécute les tests**, et écrit `build-summary.md` avec la vraie sortie des commandes. Il
stage les nouveaux fichiers avec `git add` mais ne commit **pas**.

### Step 6 — Review, and the **code gate**

[`reviewer`](../reference/agents.md#reviewer) revoit le diff et écrit `review-code.md` — une
ligne concise par constat, taggée par sévérité (🔴 must-fix / 🟡 should-fix / 🟢 consider). Tu atteins le
**code gate** : **approve / request changes / cancel**. S'il y a des constats must-fix, demander des
changements reboucle vers le build (plafonné à 3 itérations).

### Step 7 — Ship? (decline it)

Claude demande s'il faut ship. **Décline** — c'était une exécution d'entraînement. Rien n'est commité ni pushé.
(Quand tu *ship* pour de vrai, il branche par repo avec `--no-track`, commit, et ouvre une PR en suivant les
[règles git de l'org](../reference/gates-and-protocol.md#règles-de-branch-commit--ship).)

### Step 8 — Retrospective

Enfin [`retrospective`](../reference/agents.md#retrospective) écrit `retro.md` et *propose* une
checklist d'apprentissages durables et de mises à jour de docs. Il n'écrit jamais en mémoire ni n'édite les docs de lui-même —
il te remet la checklist pour approbation.

### Step 9 — Look at what you produced

Ouvre le répertoire de tâche et vois la trace :

```
.work/<slug>/
├── task.md
├── context.md
├── exploration.md
├── plan.md
├── build-summary.md
├── review-code.md
├── retro.md
└── _signals/
    └── revision-request.md   ← your "request changes" feedback, recorded
```

✅ **Tu as appris la boucle de base :** *context → explore → plan → [GATE] → build → review → [GATE] →
ship? → retrospective*, chaque phase possédée par un agent nommé, chaque artefact un fichier, et les deux gates
où **c'est toi** qui décides.

---

## Where to go next

- Comprendre *pourquoi* c'est façonné ainsi → [Explication : philosophie de conception](../explanation/design-philosophy.md)
- Accomplir du vrai travail → [How-to : choisir un workflow](../how-to/choose-a-workflow.md)
- Chercher le rôle exact d'un agent → [Référence : agents](../reference/agents.md)
