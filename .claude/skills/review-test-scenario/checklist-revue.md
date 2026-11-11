# Checklist de revue d'un cas de test

Quatre passes, dans cet ordre. Chaque constat se note avec sa référence `fichier:ligne`.

---

## Passe 1 — Produisibilité des préconditions

> *L'application sait-elle créer l'état de données demandé ?*

Pour **chaque** précondition de données, tracer le chemin de création dans le code :

1. Quel écran / quel endpoint crée cette donnée ?
2. Quelle colonne est écrite, par quel code, avec quelle valeur ?
3. Cette valeur est-elle **choisie par l'utilisateur** ou **imposée par le code** ?

Une précondition qui exige deux colonnes indépendantes alors que le code les écrit **ensemble, à partir
de la même source**, n'est pas produisible. C'est le cas le plus fréquent et le plus coûteux : le testeur
perd une journée à essayer.

Vérifier aussi :

- **les migrations qui ont rétro-rempli une colonne** (`PM/SupportFiles/MigrationScripts/**`) : une
  migration qui pose `COLONNE_A = COLONNE_B` fait disparaître une distinction que le cas de test croit
  pouvoir exercer. Chercher les `UPDATE ... SET` dans les scripts touchant la table ;
- **les valeurs sentinelles** (usagers génériques négatifs, ids 0, NULL conventionnel) : une comparaison
  d'égalité contre une sentinelle est toujours fausse, donc la branche de code est inatteignable ;
- **le niveau / la portée** de la donnée : un objet rattaché à une portée que l'usager de test ne partage
  pas ne lui sera jamais retourné, et l'attendu « le rapport est affiché » échouera.

**Sorties possibles :**

| Constat | Action |
|---|---|
| produisible depuis l'interface | documenter la **procédure de création pas à pas**, avec les refus possibles (ex. unicité → 409, cible invalide → 400) |
| produisible seulement par SQL | fournir le SQL, l'étiqueter **« état artificiel : aucune action applicative ne le produit »**, et le rendre optionnel |
| non produisible du tout | redistribuer les rôles du cas de test et remonter l'écart à l'analyste |

---

## Passe 2 — Atteignabilité des étapes

> *Le testeur peut-il réellement cliquer ce que l'étape lui demande de cliquer ?*

Pour chaque étape qui sélectionne, ouvre ou clique un élément :

- l'élément est-il **affiché** dans la configuration de préférences de l'étape ? Le gate d'affichage
  (liste de groupes, onglets, entrées de menu) est souvent **plus restrictif** que le gate de données :
  l'API peut retourner l'élément alors que l'écran n'offre aucun chemin pour l'atteindre ;
- un attendu « le bouton X est grisé » suppose que l'élément est **visible**. Si l'élément est absent,
  l'attendu correct est « l'élément n'est pas offert », pas « le bouton est grisé » — ce sont deux
  comportements différents, et confondre les deux masque un vrai défaut ;
- la préférence modifiée est-elle **relue** sans reconnexion ? Si elle est mise en cache à l'ouverture de
  session, l'étape doit inclure déconnexion/reconnexion, sinon le résultat observé est celui de la
  configuration précédente.

Quand le comportement d'affichage dépend du frontend et que le code frontend n'est pas disponible :
formuler l'attendu pour couvrir les deux cas **et** poser la question dans « à remonter ».

---

## Passe 3 — Cohérence des attendus

> *Les attendus peuvent-ils être vrais en même temps sur la même donnée ?*

- **Exclusivité mutuelle** : si un même objet doit donner « actif » à plusieurs usagers par des branches
  de code différentes, relire la condition. Une suite de `if/return` ne laisse passer qu'une branche :
  dès qu'un prédicat précoce est vrai, les suivants ne sont jamais évalués. Dans ce cas, **éclater le
  jeu de données** : un objet par branche, chacun nommé et vérifiable en SQL.
- **Drapeaux dérivés** : si un drapeau est calculé à partir d'un autre (`canDelete` depuis `canEdit`),
  tout attendu sur l'un doit être doublé sur l'autre. Un cas de test qui ne vérifie que « Modifier »
  laisse passer les régressions sur « Supprimer ».
- **Cause de l'échec** : un attendu négatif (« le rapport n'apparaît pas ») doit être protégé par des
  préconditions qui excluent les **autres** raisons d'absence (visibilité, feature flag, condition de
  préférence, filtre de support). Sinon le test passe pour la mauvaise raison.
- **Application côté serveur** : quand l'interface grise un bouton, vérifier dans le service si la
  mutation est aussi refusée (403/404). Si oui, proposer une vérification d'API **optionnelle** : elle
  prouve que ce n'est pas qu'un masquage d'interface.

---

## Passe 4 — Hygiène d'exécution

- **Isolation** : le cas modifie-t-il un état partagé (préférences d'un usager, configuration de firme) ?
  Si oui, exiger l'exclusivité sur la BD et nommer l'usager concerné.
- **Relevé initial** : toute valeur modifiée doit être relevée à l'étape 1 et restaurée à la dernière.
- **Actions destructives** : un attendu « le bouton Supprimer est actif » se vérifie **sans cliquer**.
  L'écrire explicitement, sinon le testeur détruit la donnée au milieu du cas.
- **Nettoyage** : toute donnée créée pour le test est supprimée à la fin, par l'usager qui peut le faire.
- **Identifiants stables** : nommer les jeux de données (`CFG-SUCC-A`, `RPT-FIRME`…) et fournir la
  requête SQL qui les identifie, plutôt que « une configuration avec X ».
- **Version** : noter la version/build attendue et, côté revue, la branche + le SHA du code consulté.
