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

Voici le choix de conception plus subtil. Le gate de plan ne va même pas *offrir* « approve » à moins que `plan.md` soit
`ready` et noté **A** ou **S** (sur l'échelle F < D < C < B < A < S).

Le raisonnement : **le plan est le contrat que le constructeur exécute.** Un plan vague n'échoue pas au
gate de plan — il échoue plus tard, silencieusement, quand l'implementer comble les lacunes par des suppositions. Ces suppositions
refont surface sous forme de reprise au gate de *code*, ce qui est bien plus coûteux (du code a été écrit) et plus facile
à laisser passer (cela a l'air fini). En refusant de builder à partir d'un plan sous-A, le système déplace l'échec
vers l'avant, au lieu le moins cher pour le corriger : le plan, où corriger signifie éditer de la prose, pas du code.

Donc un plan `draft` ou noté B n'est pas une nuisance — c'est le système qui vous dit, tôt et à bon marché, que
quelque chose n'est pas encore décidé : une question ouverte, un point de décision `needs-user`, ou une étape si
sous-spécifiée que le constructeur devrait deviner.

## Pourquoi un `draft` honnête vaut mieux qu'un `ready` gonflé

Le [`planner`](../reference/agents.md#planner) reçoit explicitement l'instruction de **ne jamais gonfler la note
ni basculer vers `ready` pour franchir le gate** — un plan sur-noté est considéré comme *pire* qu'un `draft`
honnête. Et le [`reviewer`](../reference/agents.md#reviewer), en mode plan, traite un plan `ready` à tort
ou sur-noté comme un `must-fix`.

Pourquoi protéger la note avec autant de soin ? Parce que tout le mécanisme dépend de la véracité de la note. Si
les notes pouvaient être gonflées pour déverrouiller le gate, la barre ne protégerait rien — elle ajouterait juste une étape
où le planner corrige lui-même son propre devoir en A. Rendre la note vérifiée de manière adversariale (le reviewer
la vérifie) et faire de la malhonnêteté l'option *la pire* est ce qui donne à « ready + A » son sens. La barre
ne vaut que par l'honnêteté de la note qui la sous-tend.

## Pourquoi alors vous laisser l'outrepasser ?

Parce que la barre est un *défaut*, pas une cage. Certains changements sont réellement triviaux et vous avez déjà
jugé qu'ils étaient corrects ; forcer un plan noté A pour un changement d'une ligne serait de la bureaucratie. Vous pouvez donc
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

Chacun de ces choix — où gater, la barre de build, les règles d'honnêteté de la note, l'outrepassement, le
plafond de boucle — revient à une idée de la [philosophie de conception](design-philosophy.md) : *placer le jugement de
l'humain aux moments coûteux et irréversibles, et refuser de simuler un progrès au-delà d'eux.*
