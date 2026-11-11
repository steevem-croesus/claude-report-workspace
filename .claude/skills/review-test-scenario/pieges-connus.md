# Pièges connus

Catalogue des pièges déjà rencontrés en revue de cas de test, avec leur preuve dans le code.
**Vérifier que le piège s'applique toujours** dans la version courante avant de l'invoquer : ces notes
vieillissent, et une ligne citée peut avoir bougé.

Premier cas documenté : RPT-21343 (configuration des rapports, Xpert 90.54).

---

## 1. Nommage — le testeur ne voit pas le nom que le ticket cite

Un même champ porte cinq noms. Un cas de test qui cite le mauvais est inexploitable.

| Couche | Exemple (drapeau « lecture seule » d'une configuration) | Où le trouver |
|---|---|---|
| Interface | case **« Lecture seule »** | libellés du frontend / de CroesusClient |
| Base de données | `B_RPT_PARTY_JOIN.READ_ONLY` | `*Implementer.cs`, attribut `FIELDNAME` |
| Champ logique PM | `RGJ_readOnly` | `sp_create_field` dans `PM/SupportFiles/MigrationScripts/` |
| ORM CFF | `ReportParty.ISREADONLY` | `BusinessObjects/.../PropertiesNames` |
| API | `isReadOnly` | modèles `FrontendSerialization` |

Un nom de champ logique PM (`RGJ_*`, `RPT_*`, `CLI_*`) dans un cas de test QA est presque toujours une
erreur de couche : le testeur n'a accès ni à la vue PM ni à l'ORM. Donner le libellé d'interface **et**
la colonne BD.

---

## 2. Liste vs groupe — l'API retourne, l'écran n'offre pas

`ReportConfigurationService.GetGroups()` n'ajoute le niveau `Firm` à la liste des groupes que si
`PREF_EDIT_FIRM_FUNCTIONS` est actif, alors que `GetConfigurableReports()` retourne les configurations de
niveau Firme à tout le monde.

Conséquence : sans la préférence, le rapport de niveau Firme est **inatteignable** dans l'écran — il
n'est pas « affiché avec le bouton grisé ». Tout cas de test qui demande de sélectionner un groupe doit
d'abord vérifier que ce groupe est offert.

**Généralisation** : vérifier séparément le gate *de données* (ce que l'API retourne) et le gate
*d'affichage* (ce que le sélecteur/menu propose). Ils divergent.

---

## 3. Propriétaire ≠ créateur : non produisible

`PartyManager.CreatePartyForUser` → `FindUserOwnedPartyForAccessLevel` n'accepte qu'un party dont
`OWNER_NUM = usager courant` (sauf niveaux partagés : CroesusDefault, SuperFirm, Firme) ; sinon il en
crée un neuf appartenant à l'usager courant. La copie (`ReportItem.CreatePartyForUser`) **et** le
déplacement « Partagé avec » (`ReportPartyInfo`) passent tous deux par là.

Conséquences :

- toute configuration créée depuis l'application a `OWNER_NUM = CREATED_BY` — propriétaire et créateur
  sont le même usager ;
- aux niveaux Firme/Global, `OWNER_NUM` est un usager générique négatif → une comparaison `isOwner` est
  fausse pour tout le monde ;
- la migration `90/11/11` a rétro-rempli `CREATED_BY = OWNER_NUM` pour les partys de niveau > Firme, ce
  qui a achevé de fusionner les deux notions.

Un cas de test qui distribue « propriétaire » et « créateur » à deux usagers différents demande donc un
état que seul un `UPDATE` SQL produit. Redistribuer les rôles, et remonter que la branche de code
correspondante est inatteignable.

**Généralisation** : quand deux colonnes doivent différer, chercher qui les écrit. Si c'est le même code
au même moment, la précondition est fausse.

---

## 4. Surcouche de permission : la branche « administrateur » ne s'applique pas partout

Dans `ReportConfigurationService.HasWriteAccess`, la surcouche lecture seule se lit ainsi :

- `CREATED_BY` **NULL** (configuration livrée) → propriétaire **ou** `PREF_EDIT_FIRM_FUNCTIONS` ;
- `CREATED_BY` **renseigné** (copie créée par un usager) → **créateur uniquement**, sans échappatoire
  administrateur.

Un énoncé du type « actif pour le propriétaire, pour le créateur et pour un administrateur de firme »
décrit donc trois branches **mutuellement exclusives** : il faut trois jeux de données, pas un seul.

**Généralisation** : une cascade de `if/return` ne laisse passer qu'une branche. Lire la condition dans
l'ordre d'évaluation avant d'écrire un attendu multi-usagers.

---

## 5. Portée des données : qui voit quoi

`CurrentUserReports` (scénario flex) ne retourne que les objets rattachés à un party de l'usager courant,
dans **sa firme**. Et `PartyManagerCache.GetData` compose la liste des partys d'un usager avec : les
partys publics, **tous les partys de sa succursale quel qu'en soit le propriétaire**, ses propres partys,
et les partys d'équipe de ses collègues d'équipe.

Donc : une configuration de niveau Usager d'un conseiller n'est visible que par lui ; une configuration
de niveau Succursale est visible par toute la succursale. Un cas de test qui fait observer une donnée par
un autre usager doit fixer la succursale / l'équipe / la firme en précondition.

---

## 6. Filtres d'exclusion — l'attendu négatif qui passe pour la mauvaise raison

Un objet peut être absent de la liste pour des raisons sans rapport avec la règle testée :
read-only de **définition** (distinct du read-only de **configuration**), colonnes de visibilité,
condition de préférence, feature flag par objet, filtre « supporté par le web », objets techniques
exclus par nom.

Tout cas de test avec un attendu « l'objet est affiché » ou « n'est pas affiché » doit fixer ces
colonnes en précondition et fournir la requête SQL qui les vérifie d'un coup.

---

## 7. Préférences mises en cache à l'ouverture de session

`PartyManager.InitializeAccessLevels` lit `PREF_EDIT_FIRM_FUNCTIONS` à la construction du manager, et la
session met les préférences en cache. Toute étape qui modifie une préférence doit être suivie d'une
déconnexion/reconnexion, sinon l'étape suivante observe l'ancienne configuration.

---

## 8. Symétrie des drapeaux d'action

`CanDelete` dérive de `CanEdit` (plus une exclusion de niveau Global). Un cas de test qui ne vérifie que
« Modifier » laisse passer les régressions sur « Supprimer ». Vérifier les deux partout, et vérifier
séparément l'exclusion propre à « Supprimer ».
