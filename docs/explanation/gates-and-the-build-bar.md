# Gates et la barre de build

Cette page explique *pourquoi* les workflows gated s'arrêtent pour votre approbation, et pourquoi le gate de plan a une
condition d'entrée inhabituelle — la **barre de build**. Pour la mécanique (quels boutons vous obtenez, comment franchir un
plan sous la barre), voir la reference et le how-to :
[gates et protocole](../reference/gates-and-protocol.md),
[faire passer un plan au gate](../how-to/pass-the-plan-gate.md).

## Pourquoi gater du tout ?

Les workflows tracent une ligne entre le travail **réversible** et **irréversible** :

- *Réversible :* rassembler du contexte, cartographier le code, rédiger un plan, relire un diff. Si c'est faux, vous
  jetez l'artefact et rien n'a été endommagé.
- *Irréversible (ou coûteux à défaire) :* écrire du code, et surtout committer/pousser/ouvrir une PR.

Un gate est placé à chaque transition du réversible vers l'irréversible : le **gate de plan** (avant qu'aucun
code ne soit écrit) et le **gate de code** (avant que quoi que ce soit ne puisse être shippé). Partout ailleurs le workflow
avance simplement — gater les étapes bon marché ne serait que friction sans bénéfice. Le principe : *dépenser
l'attention de l'humain là où une erreur est coûteuse à défaire.*

Les gates sont aussi là où le workflow **refuse de deviner**. « approve / request changes / cancel » est une véritable
bifurcation avec de vrais compromis — exactement le genre de décision que le système vous redonne plutôt que
d'en inventer une réponse.

## Pourquoi la barre de build ?

Voici le choix de conception plus subtil. Le gate de plan ne va même pas *offrir* « approve » à moins que
`plan.md` soit `ready` et que le reviewer ait écrit `Buildable: yes` dans `review-plan.md`.

Le raisonnement : **le plan est le contrat que le constructeur exécute.** Un plan vague n'échoue pas au
gate de plan — il échoue plus tard, silencieusement, quand l'implementer comble les lacunes par des
suppositions. Ces suppositions refont surface sous forme de reprise au gate de *code*, ce qui est bien plus
coûteux (du code a été écrit) et plus facile à laisser passer (cela a l'air fini). En refusant de builder
à partir d'un plan non constructible, le système déplace l'échec vers l'endroit le moins cher pour le
corriger : le plan, où corriger signifie éditer de la prose, pas du code.

## Pourquoi ce n'est plus le planner qui se note

Jusqu'en novembre 2026, le planner attribuait lui-même une note de F à S à son plan, et le gate s'ouvrait à
partir de A. Sur vingt plans produits dans ce workspace, dix-neuf portaient « ready · A » : une note que son
auteur sait être le seuil ne mesure rien.

Deux changements en découlent. **Le juge n'est plus l'auteur** : le planner déclare seulement `draft` ou
`ready`, et c'est le [`reviewer`](../reference/agents.md#reviewer) qui décide. **Le jugement n'est plus une
lettre** : huit critères binaires, chacun avec une preuve vérifiable (une ligne du plan, un fichier ouvert,
un grep). On peut gonfler une note ; il est beaucoup plus difficile de répondre « oui » à « chaque fichier
cité existe-t-il ? » quand la réponse est non. Un critère sans preuve vaut « non ».

Un plan `draft` ou `Buildable: no` n'est donc pas une nuisance — c'est le système qui vous dit, tôt et à bon
marché, ce qui n'est pas encore décidé ou pas encore vérifié, critère par critère.

## Pourquoi alors vous laisser l'outrepasser ?

Parce que la barre est un *défaut*, pas une cage. Certains changements sont réellement triviaux et vous avez déjà
jugé qu'ils étaient corrects ; exiger huit critères à oui pour un changement d'une ligne serait de la bureaucratie. Vous pouvez donc
explicitement outrepasser et approuver un plan sous la barre — mais l'outrepassement est **enregistré** dans
`_signals/revision-request.md`. L'objectif de conception n'est pas de vous empêcher de continuer ; c'est de rendre le
fait de continuer sous la barre un acte *conscient et auditable* plutôt qu'un accident. En l'absence d'un outrepassement
explicite, la barre tient.

## Le plafond de boucle

Le « request changes » du gate de code peut reboucler vers le build, mais seulement **3 fois**. Cela existe pour qu'un
cycle build↔review qui ne converge pas remonte jusqu'à vous plutôt que de tourner indéfiniment — après 3
tours le workflow s'arrête et rapporte ce qui reste ouvert. C'est le même instinct que le plafond de HALT :
automatisation bornée qui escalade vers un humain au lieu de s'agiter.

## Le fil conducteur

Chacun de ces choix — où gater, la barre de build, la séparation entre l'auteur et le juge du plan, l'outrepassement, le
plafond de boucle — revient à une idée de la [philosophie de conception](design-philosophy.md) : *placer le jugement de
l'humain aux moments coûteux et irréversibles, et refuser de simuler un progrès au-delà d'eux.*
