# Comment choisir un workflow

Il y en a sept. Choisissez selon le *type* de travail, pas selon le repo. Voici la table de décision
issue de [`.claude/conventions/workflows.md`](../../../.claude/conventions/workflows.md), qui fait autorité.

| Si la tâche est… | Utiliser | Gaté ? | Modifie le code ? |
|---|---|---|---|
| ajouter/changer un comportement visible par l'utilisateur ou une API | **`feature`** | ✅ | ✅ |
| quelque chose est cassé / sortie erronée | **`bug`** | ✅ | ✅ |
| améliorer la structure, garder le comportement identique | **`refactor`** | ✅ | ✅ |
| « devrait-on… ? » / approche inconnue / évaluer des options | **`spike`** | ✅ (décision) | ✗ (jetable seulement) |
| « où est / comment circule X ? » | **`explore`** | ✗ | ✗ |
| « pourquoi / comment est-ce arrivé ? » | **`investigate`** | ✗ | ✗ |
| « aide-moi à comprendre ce domaine » | **`learn`** | ✗ | ✗ |

## Les frontières délicates

- **`bug` vs `investigate`** — vous savez déjà que c'est cassé et vous voulez que ce soit *corrigé* → `bug` (il exécute
  le diagnostic d'`investigate` comme sa phase 3). Vous voulez seulement *comprendre* un comportement → `investigate`.
- **`explore` vs `investigate`** — `explore` répond au *où/quoi* (une carte du code). `investigate` répond au
  *pourquoi/comment* et écarte les alternatives à l'aide de l'historique git et des logs. `explore` est moins coûteux ; utilisez-le
  en premier quand vous avez juste besoin de localiser des choses.
- **`feature` vs `refactor`** — comportement nouveau/modifié → `feature`. Même comportement, meilleure forme →
  `refactor` (il impose des tests de caractérisation *avant* toute modification).
- **`spike` d'abord ?** — si l'*approche elle-même* est inconnue (pas seulement les détails), exécutez `spike` pour
  aboutir à une décision, puis alimentez cette décision dans un `feature` ou un `refactor`.

## Comment invoquer

Tapez la commande slash avec votre tâche en ligne :

```
/feature add a reportFormat query parameter to the download endpoint
/bug FOG-9412
/explore how does a queued report reach S3?
```

Ou décrivez simplement la tâche en langage clair — Claude la fait correspondre à un workflow à partir des
descriptions de skills. Les commandes slash rendent le choix explicite ; utile quand la tâche se situe près d'une frontière
ci-dessus.

## Ce que vous obtenez dans tous les cas

Chaque workflow partage le [protocole](../reference/gates-and-protocol.md) : un répertoire de tâche `.work/<slug>/`,
des agents nommés par phase, et (pour ceux qui sont gatés) des arrêts interactifs **approve / request changes /
cancel** que vous contrôlez. Voir [Référence : workflows](../reference/workflows.md) pour la liste exacte des phases
de chacun.
