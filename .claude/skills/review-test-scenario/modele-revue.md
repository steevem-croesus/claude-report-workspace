# Modèle du document de revue

Structure de `<ticket>-revue.md`. Supprimer les sections sans contenu plutôt que d'écrire « néant ».

---

```markdown
# <TICKET> — <titre du cas de test>

Revue du cas de test `<fichier d'entrée>`. Scénario révisé : `<ticket>-revise.csv`
(l'original n'est pas écrasé).

Code consulté : `<branche>@<sha>` le <date>.

Références :
- <chemin:ligne du contrôleur / service de référence>
- <autres fichiers déterminants>

---

## 1. Nomenclature

Table de correspondance des champs cités par le cas de test, couche par couche
(interface / base de données / champ logique PM / ORM / API), avec la source de chaque nom.
Conclure par le nom à utiliser dans le cas de test.

## 2. Règles réellement implémentées

Tableau des règles, **une référence `fichier:ligne` par ligne**. Couvrir : barrière d'accès,
alimentation de la liste, filtres d'exclusion, drapeaux d'action et leurs dérivations,
application côté serveur.

## 3. Résultat de la revue

Une sous-section par constat, numérotée, avec pour chacune :
- le constat, prouvé par le code (référence) ;
- pourquoi l'étape ou la précondition d'origine ne tient pas ;
- **Correction** : ce qui est changé dans le scénario.

Terminer par « Points mineurs » : symétrie des drapeaux, préconditions manquantes, précautions.

## 4. Préconditions révisées

- **Environnement** : version, isolation, relecture des préférences.
- **Utilisateurs** : tableau rôle / usager / préférences attendues, avec les contraintes de portée
  (firme, succursale, équipe).
- **Données** : tableau des jeux de données nommés (référence, portée, valeurs des colonnes clés,
  mode d'obtention, règle couverte).
- **Procédure de création** des données produisibles depuis l'interface, pas à pas, avec les refus
  possibles.
- **Requêtes SQL de vérification**, prêtes à coller.
- **Précautions d'exécution** : ne pas cliquer les actions destructives, relevés, restaurations.

## 5. Scénario révisé

Tableau `# | Action | Données | Résultat attendu`, identique au CSV produit.
Puis « Vérifications serveur optionnelles » : appels d'API qui prouvent que le refus n'est pas
qu'un masquage d'interface.

## 6. Annexe — états forgés (optionnel)

Uniquement si une règle n'est couvrable que par un état que l'application ne produit pas.
SQL de forgeage **étiqueté comme artificiel**, attendus, SQL de restauration.

## 7. À remonter à l'analyste

Liste numérotée des écarts entre l'énoncé du ticket et le comportement implémenté, formulés comme
des questions tranchables. Ne rien aligner silencieusement : le code peut être le défaut.
```

---

## Règles de rédaction

- **Français**, phrases courtes, pas de conditionnel de précaution sur un fait vérifié dans le code.
- Chaque affirmation sur le comportement porte une **référence `fichier:ligne`** vérifiée.
- Les attendus du scénario sont **observables par un testeur** : ce qui est affiché, ce qui est grisé,
  ce qui est absent. Jamais « `canEdit` vaut false ».
- Les jeux de données portent des **références stables** réutilisées à l'identique dans le document,
  le CSV et le ticket.
- Distinguer systématiquement **« absent »**, **« affiché et grisé »** et **« affiché et actif »**.
