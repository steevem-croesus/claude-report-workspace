# La philosophie de conception

Cette page traite du *pourquoi* le système `.claude/` existe sous cette forme. Elle ne vous dira pas comment exécuter un
workflow — pour cela, voir les [guides How-to](../how-to/). Elle est là pour vous donner le modèle mental qui
rend tout le reste inévitable plutôt qu'arbitraire.

## Le problème que cela résout

Le pipeline de rapports Croesus Xpert s'étend sur cinq codebases dans trois langages : deux monolithes C++
(`CroesusServer`, `ReportServer`), deux stacks C# (`ReportFoundations`, `ReportManagerApi`), et un
frontend Angular (`pf-web`). Un seul travail de rapport — disons, l'ajout d'un champ de rapport — peut se propager
à travers chacun d'eux, dans un ordre fixe, chacun avec ses propres conventions, sa branche et sa PR.

Cette combinaison est exactement là où l'assistance IA ad hoc dérape : elle devine le mauvais repo, invente
des exigences que le ticket n'a jamais énoncées, écrit du code avant de comprendre le flux existant, ou ship un
port plausible-mais-faux d'un calcul de dates C++ subtil. Le système `.claude/` est une réponse délibérée à
ce mode de défaillance. Son fil conducteur est :

> **Rendre le travail lisible et réversible.** Chaque étape produit un artefact nommé que vous pouvez lire ; chaque
> étape risquée attend votre approbation avant de se produire.

## Idée 1 — Faire correspondre la *forme* du processus au *type* de travail

Il n'existe pas une seule procédure « faire la tâche », car les garde-fous qui comptent diffèrent selon le type de travail :

- Un correctif de **bug** est sans valeur — voire dangereux — sans une reproduction et un test de régression, donc le
  workflow `bug` les rend obligatoires et place le *diagnostic* avant tout patch.
- Un **refactor** ne doit pas changer le comportement, donc `refactor` force des tests de caractérisation *avant* la
  première modification et exige que le build reste vert après *chaque* étape.
- Un **spike** existe précisément parce que l'approche est inconnue, donc sa sortie est une *décision*, ses
  prototypes sont jetables, et il est timeboxé.
- **Explore / investigate / learn** ne changent aucun code, donc ils ne portent aucun gate et restent bon marché.

Sept workflows, chacun encodant la discipline dont son type de travail a réellement besoin. C'est pourquoi
« [choisir un workflow](../how-to/choose-a-workflow.md) » est la première vraie décision — le workflow
*est* le garde-fou.

## Idée 2 — Un artefact par phase, sur disque

Chaque phase écrit exactement un fichier dans `.work/<slug>/` (`context.md`, `exploration.md`, `plan.md`,
`build-summary.md`, `review-code.md`, `retro.md`, …). Ce n'est pas de la paperasse pour elle-même :

- **Cela rend le raisonnement inspectable.** Vous pouvez lire le plan avant qu'aucun code ne soit écrit, et la
  revue avant d'approuver le ship.
- **Cela survit d'une session à l'autre.** Comme le répertoire vit à la racine du workspace (pas à l'intérieur d'un
  repo produit), une tâche peut être reprise plus tard — la trace est toujours là.
- **Cela garde les repos produit propres.** Rien du *processus* ne fuit dans les repos de code.

Voir [Reference : le répertoire de tâche](../reference/task-directory.md) pour la liste complète des artefacts.

## Idée 3 — Les gates placent un humain aux moments irréversibles

Lire du code, le cartographier et planifier sont tous réversibles — vous pouvez jeter l'artefact. Écrire du
code, et surtout le *shipper*, ne le sont pas. Donc les workflows s'arrêtent pour votre approbation à exactement deux
points universels — après le **plan** et après le **build+review** — et nulle part gratuitement entre les deux.
C'est le sujet de sa propre page : [gates et la barre de build](gates-and-the-build-bar.md).

## Idée 4 — Des agents étroits, chacun avec un seul métier

Plutôt qu'un seul agent qui fait tout, le travail est réparti sur
[neuf spécialistes](../reference/agents.md) : un localisateur, un analyste de cause racine, un planificateur, un constructeur, un
relecteur, et ainsi de suite — plusieurs d'entre eux strictement read-only. Un relecteur adversarial et laconique qui ne fait que
relire produit de meilleures revues qu'un généraliste qui a aussi écrit le code. Pourquoi cela importe est
discuté dans [l'orchestrateur et le modèle d'agents](orchestrator-and-agents.md).

## Idée 5 — Déférer à l'autorité locale

Un conseil générique perd face au repo qui est devant vous. Tout le système est bâti pour *déférer* : les skills défèrent
à `workflows.md` + `protocol.md` ; les agents défèrent au propre `CLAUDE.md` /
`copilot-instructions.md` de chaque repo ; le port C++→C# défère à la recette de `copilot-instructions.md`. Les
fichiers `.claude/` disent délibérément « citez-les et suivez-les — ne réénoncez pas leurs règles », de sorte qu'il y a une
source unique de vérité pour chaque chose. (Ces `docs/` suivent le même principe : ils expliquent et indexent les
fichiers `.claude/` plutôt que de les dupliquer — voir
[comment garder les docs synchronisées](../how-to/keep-docs-in-sync.md).)

## Ce que cela vous apporte

- Vous pouvez avoir confiance qu'un correctif de `bug` a un vrai test de régression, et qu'un `refactor` n'a pas changé le comportement.
- Vous voyez le plan — avec ses risques, son estimation et sa note honnête — *avant* que le code n'existe.
- Le travail multi-repo respecte les conventions de chaque repo et atterrit sur des branches/PR séparées, comme les
  règles git de l'organisation l'exigent.
- La connaissance ne s'évapore pas : chaque workflow gated se termine par une rétrospective proposant des
  apprentissages durables.

## Ce qu'il n'est délibérément *pas*

- **Pas autonome.** Il est gated à dessein ; il demande plutôt que de deviner au-delà d'une véritable bifurcation.
- **Pas un remplacement du plugin `code-fleet` de l'organisation** — il interopère avec lui (les phases build/review
  peuvent être déléguées à `/code-fleet:work`). Il ajoute ce qui manque à la fleet : la conscience de la topologie des
  rapports, le `cpp-to-csharp-porter`, et les rôles de compréhension read-only.
