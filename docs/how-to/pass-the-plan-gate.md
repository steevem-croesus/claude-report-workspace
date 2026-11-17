# Comment faire passer un plan au gate

Le gate de plan a une condition d'entrée stricte, la **barre de build** : un workflow ne construit **que**
depuis un `plan.md` déclaré **`ready`** par le planner *et* jugé **`Buildable: yes`** par le reviewer dans
`review-plan.md`. Ce guide décrit quoi faire quand votre plan revient sous cette barre.

Pour le *pourquoi*, voir [Explication : gates & barre de build](../explanation/gates-and-the-build-bar.md).

## Lisez les deux en-têtes

`plan.md` s'ouvre par le statut déclaré par son auteur :

```
**Status:** <draft | ready>
```

`review-plan.md` s'ouvre par le verdict du reviewer, suivi de huit critères auxquels il répond
**oui / non / n.a.**, chacun avec sa preuve :

```
**Buildable:** <yes | no>
```

| # | Critère | Répond « non » quand… |
|---|---|---|
| C1 | Couverture des exigences | une exigence du contexte n'est reliée à aucune étape ni à un report explicite |
| C2 | Contrats concrets | un endpoint, un DTO ou une méthode publique reste décrit en prose |
| C3 | Décisions résolues | il reste un point `needs-user` ou une question ouverte bloquante |
| C4 | Emplacements vérifiés | un fichier, une classe ou une méthode cité est introuvable |
| C5 | Tests nommés | une étape qui change un comportement n'a pas de test nommé avec son niveau |
| C6 | Pièges connus | une entrée applicable de `known-pitfalls.md` est ignorée |
| C7 | Sécurité / intégrité | une garantie « par construction » ne couvre que le chemin nominal (n.a. sans contrainte) |
| C8 | Estimation cohérente | la confiance annoncée ignore les inconnues du plan |

- **`ready` + `Buildable: yes`** → le gate offre **approve / request changes / cancel**. L'approbation reste
  requise : la revue *déverrouille* le gate, elle ne le franchit pas.
- **`draft`, ou `Buildable: no`** → le gate n'offre **pas** approve. Il présente les critères à « non » avec
  leur preuve et vous route vers changes ou cancel.

## Si le plan est sous la barre

1. **Request changes (le cas usuel).** Claude écrit les critères à « non » et votre retour dans
   `.work/<slug>/_signals/revision-request.md`, redéclenche le `planner`, refait passer le `reviewer`, et
   revient au gate. Répétez jusqu'à `ready` + `Buildable: yes`.
2. **Tranchez les points de décision.** Un plan reste souvent `draft` à cause d'un point `needs-user` — une
   bifurcation que vous seul devez trancher. Répondez (Claude vous le demandera), et le planner peut
   atteindre `ready`.
3. **Passez outre (délibérément).** Pour un changement que vous jugez réellement trivial, vous pouvez
   approuver un plan sous la barre. Le passage outre est consigné dans `revision-request.md`. Sans passage
   outre explicite, la barre tient.

## À ne pas faire

- **Ne demandez pas au planner de « juste le marquer ready ».** Ce n'est plus lui qui décide : un `ready`
  déclaré à tort échoue au critère C3 du reviewer. Corrigez la lacune sous-jacente.
- **Ne contestez pas un « non » sans preuve contraire.** Chaque critère porte sa preuve ; si elle est fausse,
  indiquez la ligne du plan ou le fichier qui la contredit dans votre demande de révision.

## Référence

- Spécification de la barre de build et des critères : [`.claude/conventions/protocol.md`](../../.claude/conventions/protocol.md)
- Gabarit de la revue : [`templates/review-plan.md`](../../.claude/conventions/templates/review-plan.md)
