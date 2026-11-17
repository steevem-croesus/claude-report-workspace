# Review du plan — <TICKET-ID or task slug>

_Rédigée par reviewer · Date : <YYYY-MM-DD> · Plan relu : `plan.md` (Status déclaré : <draft | ready>)_

**Buildable:** <yes | no>
<!-- yes seulement si tous les critères sont à oui ou n.a. Critères définis dans protocol.md § Gate de plan. -->

## Critères

| # | Critère | Réponse | Preuve (ligne du plan, fichier ouvert, grep) |
|---|---|---|---|
| C1 | Couverture des exigences | <oui / non> | |
| C2 | Contrats concrets | <oui / non / n.a.> | |
| C3 | Décisions résolues | <oui / non> | |
| C4 | Emplacements vérifiés | <oui / non> | |
| C5 | Tests nommés | <oui / non> | |
| C6 | Pièges connus traités | <oui / non / n.a.> | |
| C7 | Sécurité / intégrité : canaux énumérés | <oui / non / n.a.> | |
| C8 | Estimation cohérente | <oui / non> | |

## À corriger pour passer le gate
_Un point par critère à « non » : ce qui manque, et ce qui le ferait passer à « oui »._

- C<n> : <manque>. <correctif attendu>.

## Constats non bloquants
- `plan.md:<ligne>` : 🟡 should-fix : <problème>. <correctif>.
- `plan.md:<ligne>` : 🟢 consider : <problème>. <correctif>.
