# Comment faire passer un plan au gate

Le gate de plan a une condition d'entrée stricte appelée la **barre de build** : un workflow ne peut construire **que** à
partir d'un `plan.md` qui est **`ready`** *et* noté **A** ou **S**. Ce guide décrit quoi faire quand votre plan
revient sous cette barre.

Pour le *pourquoi* de l'existence de la barre, voir
[Explication : gates & barre de build](../explanation/gates-and-the-build-bar.md).

## Lisez d'abord l'en-tête

Chaque `plan.md` s'ouvre par :

```
**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
```

Échelle de notes (bas → haut) : **F < D < C < B < A < S**.

- **`ready` + A ou S** → le gate offre les habituels **approve / request changes / cancel**. L'approbation
  reste requise ; une note qualifiante *déverrouille* le gate, elle ne le passe pas automatiquement.
- **`draft`, ou noté en dessous de A** → le gate n'offre **pas** approve. Il fait apparaître la note et les
  bloqueurs (questions ouvertes, points de décision `needs-user`) et vous route vers changes ou cancel.

## Si le plan est sous la barre

Vous avez trois options :

1. **Request changes (le cas usuel).** Claude écrit votre retour dans
   `.work/<slug>/_signals/revision-request.md`, redéclenche le `planner`, et revient au gate
   avec un plan révisé. Répétez jusqu'à ce qu'il atteigne `ready` + A/S.

2. **Résolvez les points de décision qu'il attend.** Un plan reste souvent `draft` à cause d'un
   **point de décision** `needs-user` — une bifurcation que vous seul devriez trancher. Répondez-y (Claude vous le demandera), et
   le planner peut alors atteindre `ready`.

3. **Surcharger (délibérément).** Pour un changement que vous avez jugé réellement trivial, vous pouvez explicitement
   approuver un plan sous la barre. La surcharge est consignée dans `revision-request.md` pour qu'elle soit auditable. En l'absence
   d'une surcharge explicite, la barre tient.

## Pourquoi un plan est souvent `draft` au début

- un point de décision `needs-user` non résolu (une vraie bifurcation avec des compromis matériels) ;
- une question ouverte bloquante ;
- une étape assez sous-spécifiée pour que l'implementer doive deviner ;
- pour les features à flux parallèles, le plan n'a pas encore pesé l'extraction d'une classe de base partagée / le
  remodelage d'interface (il est censé considérer cela comme un point de décision, pas défaut à un diff inline minimal).

Ce n'est pas le planner qui fait des difficultés — un `draft` honnête est considéré comme *meilleur* qu'un
`ready` gonflé. Le [`reviewer`](../reference/agents.md#reviewer), en mode plan, signalera un plan sur-noté
ou à tort `ready` comme un must-fix.

## À ne pas faire

- **Ne demandez pas au planner de « juste le marquer ready ».** Il a pour consigne de ne jamais gonfler la note pour
  franchir le gate. Corrigez plutôt la lacune sous-jacente.

## Référence

- Spécification de la barre de build : [`.claude/conventions/protocol.md` → Plan gate](../../../.claude/conventions/protocol.md)
- Grille de notation : [`.claude/agents/planner.md` → Grading & status](../../../.claude/agents/planner.md)
