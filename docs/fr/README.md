# Documentation — Croesus report workspace

> 🇬🇧 [English version](../README.md)

Cette documentation couvre **les workflows et agents de `.claude/`** qui vivent dans ce workspace : les
sept playbooks gated (`feature`, `bug`, `refactor`, `spike`, `explore`, `investigate`, `learn`),
les agents qui les exécutent, et le protocole partagé auquel ils obéissent tous. Ce n'est *pas* la
documentation du code du pipeline de rapports — pour cela, voir les fichiers `CLAUDE.md` de chaque repo et
le [`../CLAUDE.md`](../../CLAUDE.md) racine.

## Comment cette documentation est organisée (Diátaxis)

Ces docs suivent le framework [Diátaxis](https://diataxis.fr/). Chacun des quatre quadrants répond à un
besoin différent — choisis celui qui correspond à ce que tu essaies de faire en ce moment :

| Quadrant | Quand tu es… | Nature |
|---|---|---|
| 📚 **[Tutoriels](tutorials/)** | en apprentissage, nouveau ici, tu veux qu'on te *montre* | leçons pratiques orientées apprentissage |
| 🔧 **[Guides how-to](how-to/)** | en train d'accomplir une tâche précise | recettes orientées tâche |
| 📖 **[Référence](reference/)** | en train de chercher une info en plein travail | faits secs orientés information |
| 💡 **[Explication](explanation/)** | en train de comprendre *pourquoi* c'est construit ainsi | discussion orientée compréhension |

Une façon rapide de choisir :

- **« Montre-moi comment ça marche depuis zéro. »** → [Tutoriels](tutorials/)
- **« Comment je corrige un bug / lance une feature / passe un gate ? »** → [Guides how-to](how-to/)
- **« C'est quoi déjà que produit l'agent `planner` ? »** → [Référence](reference/)
- **« Pourquoi des gates au juste ? Pourquoi pas un seul gros agent ? »** → [Explication](explanation/)

## Commence ici selon ton rôle

- **Nouveau dans le workspace** → [Tutoriel : ton premier workflow](tutorials/first-workflow.md), puis
  [Explication : la philosophie de conception](explanation/design-philosophy.md).
- **Expérimenté, ici pour travailler** → [How-to : choisir un workflow](how-to/choose-a-workflow.md)
  et la [Référence](reference/).

## Source de vérité

Les specs faisant autorité sont les fichiers sous [`../.claude/`](../../.claude/) — principalement
[`.claude/conventions/workflows.md`](../../.claude/conventions/workflows.md) et
[`.claude/conventions/protocol.md`](../../.claude/conventions/protocol.md). **Ces docs expliquent et
indexent ces fichiers ; elles ne les remplacent pas.** Là où une page de Référence et un fichier `.claude/` divergent,
c'est le fichier `.claude/` qui l'emporte — et merci de [corriger la dérive](how-to/keep-docs-in-sync.md).

> **Note sur l'emplacement.** Cet arbre `docs/` vit à la racine du workspace, qui est elle-même un petit repo
> git (`.git/` existe ici), mais les repos produit symlinkés sous `repos/` sont des repos *séparés*.
> Voir [Référence : le répertoire de tâche & la disposition du workspace](reference/task-directory.md).
