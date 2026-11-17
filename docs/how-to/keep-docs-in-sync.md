# Comment garder cette documentation synchronisée

Ces `docs/` expliquent et indexent les fichiers sous [`.claude/`](../../.claude/). Les fichiers `.claude/` sont
la **source de vérité** ; la documentation les suit, jamais l'inverse. La documentation existe en une seule
langue (français) pour qu'il n'y ait qu'une version à tenir.

## Ce qui est généré

Deux pages sont produites à partir des frontmatters et ne s'éditent pas à la main :

```bash
python .claude/scripts/gen-reference-docs.py           # régénère reference/agents.md et reference/skills.md
python .claude/scripts/gen-reference-docs.py --check   # code retour 1 si une page est périmée
```

Lancez la génération dans le même changement dès que vous ajoutez, renommez ou supprimez un agent ou un
skill, ou que vous modifiez sa `description`.

## Ce qui se tient à la main

| Si vous éditez… | Relisez |
|---|---|
| `.claude/conventions/workflows.md` (une chaîne de phases change) | [reference/workflows.md](../reference/workflows.md), qui ne reprend que les chaînes |
| `.claude/conventions/protocol.md` (gates, critères C1 à C8, artefacts) | [reference/gates-and-protocol.md](../reference/gates-and-protocol.md), [reference/task-directory.md](../reference/task-directory.md), [how-to/pass-the-plan-gate.md](pass-the-plan-gate.md) |
| le libellé d'un gate ou une commande slash | [le tutoriel](../tutorials/first-workflow.md), qui doit rester exécutable |

## Règles empiriques

- **Les pages de référence renvoient, elles ne recopient pas.** Une table de phases recopiée dérive ; un
  lien vers le fichier `.claude/` qui fait autorité ne dérive pas.
- **Les pages d'explication vieillissent lentement** : elles portent sur le *pourquoi*. Ne les revisitez que
  lorsque la conception elle-même change (un nouveau gate, un workflow abandonné).
- **Le savoir sur le code ne va pas ici.** Un piège de portage ou un fait d'architecture s'écrit dans
  `.claude/conventions/known-pitfalls.md` ou `rma-architecture-notes.md`, que les agents lisent.
