# Diagnostic de bug — <TICKET-ID or task slug>

_Rédigé par l'orchestrateur (repro) + l'investigator (cause racine) · Date : <YYYY-MM-DD>_

## Symptôme
<ce qui est observé vs attendu, avec l'erreur/la sortie exacte et où elle apparaît>

## Reproduction
- **Étapes / test :** <le repro minimal, ou le test en échec qui existe désormais>
- **Statut du repro :** <reproduit de façon fiable / intermittent / pas encore reproduit>
- **Environnement :** <repo, branche, conditions de données>

## Preuves
- `repo/path:line` — <ce qu'elle montre>
- `commit <sha>` — <ce qui a changé et quand> (`git blame` / `git log -S`)
- `JIRA <key>` / `PR #n` — <historique pertinent>
- logs — <lignes pertinentes>

## Hypothèses
| # | Hypothèse | Verdict | Preuve |
|---|---|---|---|
| 1 | <…> | confirmée / réfutée | <…> |
| 2 | <…> | réfutée | <…> |

## Cause racine
<la cause la plus étayée — distingue le déclencheur de la cause sous-jacente et des facteurs contributifs>

- **Confiance :** <high / medium / low>
- **Où doit se trouver un correctif :** `repo/path` — <mais pas la conception du correctif ; ça, c'est le plan>

## Questions ouvertes
- <ce qui reste inconnu, le cas échéant>
