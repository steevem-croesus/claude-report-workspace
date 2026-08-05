# Comment garder cette documentation synchronisée

Ces `docs/` expliquent et indexent les fichiers sous [`.claude/`](../../../.claude/). Les fichiers `.claude/` sont
la **source de vérité** ; la documentation doit les suivre, pas l'inverse. Quand vous changez un
workflow, un agent ou le protocole, mettez à jour la documentation dans le même changement.

## Le mapping

| Si vous éditez… | Mettez à jour ce doc |
|---|---|
| `.claude/conventions/workflows.md` | [reference/workflows.md](../reference/workflows.md) (et tout guide pratique concerné) |
| `.claude/conventions/protocol.md` | [reference/gates-and-protocol.md](../reference/gates-and-protocol.md), [reference/task-directory.md](../reference/task-directory.md) |
| n'importe quel `.claude/agents/*.md` | [reference/agents.md](../reference/agents.md) |
| n'importe quel `.claude/skills/*/SKILL.md` | [reference/skills.md](../reference/skills.md) |
| la grille de notation des plans dans `planner.md` | [how-to/pass-the-plan-gate.md](pass-the-plan-gate.md), [explanation/gates-and-the-build-bar.md](../explanation/gates-and-the-build-bar.md) |

## Règles empiriques

- **Les pages de référence décrivent ; elles ne dupliquent pas.** Gardez-les minces et renvoyez toujours vers le
  fichier `.claude/` faisant autorité. Moins vous copiez mot pour mot, moins il peut y avoir de dérive.
- **Les pages d'explication vieillissent lentement** — elles portent sur le *pourquoi*, qui change rarement. Ne les revisitez que quand
  la philosophie de conception elle-même change (p. ex. un nouveau gate, un workflow abandonné).
- **Les tutoriels doivent rester exécutables.** Si vous renommez une commande slash ou changez le libellé d'un gate, re-parcourez
  [le tutoriel](../tutorials/first-workflow.md) pour confirmer que les étapes correspondent encore à la réalité.

## Vérification rapide de la dérive

Les sept workflows et neuf agents sont énumérables. Si un doc liste un workflow/agent qui n'existe plus
dans `.claude/`, ou en manque un nouveau, c'est de la dérive. Un audit rapide :

```bash
ls .claude/skills/*/SKILL.md          # the seven live workflow skills
ls .claude/agents/*.md                # the nine agents
```

Comparez avec [reference/skills.md](../reference/skills.md) et
[reference/agents.md](../reference/agents.md).
