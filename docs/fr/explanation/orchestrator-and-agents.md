# L'orchestrateur et le modèle d'agents

Cette page explique *pourquoi* le travail est réparti entre une skill qui orchestre et de nombreux agents étroits,
au lieu d'un seul assistant capable faisant tout. Pour ce que chaque agent est réellement, voir
[Reference : agents](../reference/agents.md).

## Les deux couches

- **L'orchestrateur** est la skill de workflow (`/feature`, `/bug`, …). Il possède la *séquence* : quelle
  phase s'exécute ensuite, quand s'arrêter à un gate, quand reboucler, comment dériver le slug. Il vous parle à *vous*.
- **Les agents** sont des spécialistes dispatchés par l'orchestrateur via l'outil Agent. Chacun possède une
  *phase* et un artefact. Ils parlent au *code et au ticket*, pas à vous — leur sortie est un
  fichier plus un court résumé que l'orchestrateur relaie.

La division est délibérée : le flux de contrôle (déterministe, gated, face à l'humain) est tenu séparé du
travail lui-même (spécialisé, gourmand en outils). L'orchestrateur n'écrit jamais le plan ; le planner ne
décide jamais s'il faut shipper.

## Pourquoi des agents étroits plutôt qu'un seul généraliste ?

Trois raisons, toutes portant sur la qualité :

1. **Un rôle focalisé produit une sortie focalisée.** Le [`reviewer`](../reference/agents.md#reviewer) reçoit
   l'instruction d'être adversarial et laconique — pas d'éloges, pas de résumés, pas de dérive de périmètre. Cette
   posture produit de meilleures revues qu'un généraliste qui a aussi écrit le code et est enclin à le défendre. De même le
   [`investigator`](../reference/agents.md#investigator) reçoit l'instruction d'*essayer de réfuter* sa propre
   hypothèse principale avant de l'accepter. Ces postures n'ont de sens que comme rôles dédiés.

2. **La séparation empêche l'auto-notation.** Le planner note son propre plan, mais le reviewer
   vérifie indépendamment cette note, et le gate dépend du résultat vérifié. Si le même agent
   planifiait, buildait, relisait *et* notait, il n'y aurait de vérification indépendante nulle part. Scinder les
   rôles crée les vérifications adversariales sur lesquelles s'appuie la [barre de build](gates-and-the-build-bar.md).

3. **Moindre privilège.** La plupart des agents sont strictement **read-only** — ils ne peuvent physiquement pas éditer le code
   (leur liste d'outils omet Edit/Write-vers-code). Seuls l'[`implementer`](../reference/agents.md#implementer)
   et le [`cpp-to-csharp-porter`](../reference/agents.md#cpp-to-csharp-porter) peuvent changer la source. C'est
   pourquoi une exécution `explore`/`investigate`/`learn` est sûre à lancer sans y réfléchir à deux fois.

## Read-only vs édition — la répartition

| | Agents | Pourquoi |
|---|---|---|
| **Read-only** | context-gatherer, explorer, investigator, learning-guide, reviewer, retrospective | comprendre et juger le travail ; ne doivent pas pouvoir le changer |
| **Édition** | planner (n'écrit que `plan.md`), implementer, cpp-to-csharp-porter | produire le plan et le code |

Notez que le planner est un cas intermédiaire : il *écrit*, mais seulement l'artefact de plan — jamais de code de
production. La conception se produit avant, et séparément de, l'implémentation.

## Pourquoi la forme de prompt fixe et le répertoire de tâche ?

Chaque agent est dispatché avec le même minuscule contrat :

```
Task directory: .work/<slug>/
Task: <the task text>
```

L'agent lit les artefacts déjà présents dans ce répertoire (la sortie de ses prédécesseurs) et écrit le sien.
C'est ce qui permet aux phases de se composer sans que l'orchestrateur ait à faire transiter l'état à travers les prompts : le
`planner` lit `context.md` + `exploration.md` ; le `reviewer` lit `plan.md` ; le `retrospective`
lit tout. Le [répertoire de tâche](../reference/task-directory.md) *est* la mémoire partagée entre les
agents.

## Pourquoi HALT plutôt que deviner ?

Un agent producteur qui atteint une véritable bifurcation — exigence ambiguë, une décision que seul l'utilisateur devrait
prendre — ne devine pas. Il renvoie un bloc **HALT** (raison, question, défaut proposé, état), et
l'orchestrateur vous remonte la question, enregistre la réponse et re-dispatche. Deviner au-delà d'une véritable
bifurcation est exactement le mode de défaillance que tout le système est bâti pour éviter ; HALT est la version au niveau agent d'un
gate. Il est plafonné (3 allers-retours par agent) pour la même raison que la boucle build↔review est plafonnée :
automatisation bornée qui escalade plutôt que de s'agiter.

## Comment cela se connecte à code-fleet

Parce que les couches sont proprement séparées, les phases *build + review* de `feature`/`refactor` peuvent être
remplacées par le plugin `code-fleet` de l'organisation (`/code-fleet:work` et ses agents language-pack)
sans perturber l'orchestration ni les rôles read-only. Les agents du workspace restent ceux qui
connaissent la topologie de rapports multi-repo et la recette de port C++→C#. Voir
[Reference : workflows → code-fleet](../reference/workflows.md#relationship-to-code-fleet).
