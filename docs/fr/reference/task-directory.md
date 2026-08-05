# Référence — Le répertoire de tâche & la structure du workspace

## `.work/<slug>/`

Chaque exécution de workflow non triviale crée un répertoire par tâche à la **racine du workspace** :
`C:\Repos\claude-report-workspace\.work\<slug>\`.

- **slug** = la clé Jira quand détectée (`FOG-9412`, `CFF-1234`) ; sinon le kebab-case des
  ~4 premiers mots de la tâche. Ré-exécuter la même tâche **réutilise** le répertoire.
- Il vit à la racine du workspace intentionnellement : il ne pollue **pas** les repos symlinkés et il
  survit d'une session à l'autre. Il est **gitignoré** ici (`/.work/` dans [`.gitignore`](../../../.gitignore)).

### Noms de fichiers d'artefacts canoniques (un artefact = un fichier)

| Fichier | Écrit par | Objet |
|---|---|---|
| `task.md` | orchestrateur | le texte brut de la tâche |
| `context.md` | [context-gatherer](agents.md#context-gatherer) | brief d'intel Jira + GitHub |
| `exploration.md` | [explorer](agents.md#explorer) | carte de code pour la tâche |
| `investigation.md` | [investigator](agents.md#investigator) | analyse de cause racine |
| `bug-diagnosis.md` | investigator | reproduction + cause racine pour un bug |
| `learning-notes.md` | [learning-guide](agents.md#learning-guide) | walkthrough / modèle mental |
| `spike.md` | orchestrateur + explorer | constats de spike + recommandation |
| `plan.md` | [planner](agents.md#planner) | plan d'implémentation (gate le build) |
| `review-plan.md` | [reviewer](agents.md#reviewer) | constats du gate de plan |
| `build-summary.md` | [implementer](agents.md#implementer) / [porter](agents.md#cpp-to-csharp-porter) | ce qui a été buildé + résultats de build/test |
| `review-code.md` | reviewer | constats du gate de code |
| `retro.md` | [retrospective](agents.md#retrospective) | rétrospective + apprentissages proposés |
| `clarifications.md` | orchestrateur | Q→R résolues avant la planification |

### Le sous-répertoire `_signals/`

Miettes de contrôle de flux que l'orchestrateur écrit quand il reboucle une phase :

| Fichier | Écrit quand |
|---|---|
| `_signals/revision-request.md` | tu choisis **request changes** à un gate (retour enregistré verbatim ; enregistre aussi un override explicite de la barre de build) |
| `_signals/resume.<agent>.md` | un agent fait HALT et tu réponds à sa question (la réponse, pour que l'agent puisse reprendre) |

**Les templates** des artefacts vivent dans
[`.claude/conventions/templates/`](../../../.claude/conventions/templates/): `context.md`, `plan.md`,
`review.md`, `spike.md`, `bug-diagnosis.md`, `retro.md`.

## Structure du workspace

Ce workspace est une racine mince qui contient des symlinks vers les checkouts de produit réels. La topologie
complète est dans le [`CLAUDE.md`](../../../CLAUDE.md) racine ; en bref :

```
C:\Repos\claude-report-workspace\
├── .git/                 ← this root is a small git repo (docs/, .claude/, CLAUDE.md tracked)
├── .claude/              ← agents, skills, conventions (the subject of these docs)
├── docs/                 ← you are here
├── .work/                ← per-task directories (gitignored)
├── .benchmark/           ← local eval fixtures (gitignored)
├── CLAUDE.md
├── link-monolith-skills.ps1
└── repos/                ← SYMLINKS to the real repos (gitignored; each its own git repo)
    ├── CroesusServer     → C++ Frameworkserver monolith
    ├── ReportServer      → C++ report-generation engine
    ├── ReportFoundations → C# shared reporting libs
    ├── ReportManagerApi  → C# / .NET 8 report API
    └── pf-web            → TypeScript / Angular 21 + NX frontend
```

> **Deux niveaux de git.** La racine du workspace est son propre repo (trackant `.claude/`, `docs/`, `CLAUDE.md`,
> etc.). Chaque symlink sous `repos/` pointe vers un repo *séparé* sur sa propre branche et son propre remote. Les commits
> et PRs pour les changements de produit se font **à l'intérieur du repo symlinké spécifique**, jamais à la racine — voir
> les [règles de branch/commit/ship](gates-and-protocol.md#règles-de-branch-commit--ship).
