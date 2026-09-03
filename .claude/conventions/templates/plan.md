# Plan — <TICKET-ID or task slug>

_Rédigé par planner · Date : <YYYY-MM-DD>_

**Status:** <draft | ready> · **Grade:** <F | D | C | B | A | S>
<!-- Buildable only when Status = ready AND Grade ∈ {A, S}. Scale: F < D < C < B < A < S. -->

## Problème
<un paragraphe. Nomme le(s) repo(s) et langage(s) cible(s).>

## Couverture des exigences
| Exigence (issue du contexte / des critères d'acceptation) | Couverte par | Notes |
|---|---|---|
| <exigence 1> | Étape 2 | |
| <exigence 2> | Étape 3 | |
| <exigence 3> | — | reportée / hors périmètre — <pourquoi> |

_Rien de ce qui est demandé ne peut être abandonné en silence ; chaque ligne renvoie à une Étape ou à un report explicite._

## Zones affectées
- **<repo>** — `path/to/area` — <ce qui change>
- **<repo>** — `path/to/area` — <ce qui change>

## Contrats & interfaces
_Le design concret que l'implémenteur doit écrire tel quel — pas une description en prose. Ne liste que ce qui est
**créé ou modifié** ; ne recopie pas l'existant inchangé. Omets une sous-section entière si elle ne s'applique pas.
Marque `⚠ à confirmer` toute signature déduite plutôt que lue dans le code. Les noms, types, nullabilité et
conventions (`Result<T>`, `Async`/`CancellationToken`, `readonly`, signals Angular) sont ceux du repo cible._

### Endpoints
| Méthode + route | Auth / policy | Request | Response | Codes | Controller (fichier) |
|---|---|---|---|---|---|
| `POST /api/v1/<…>` | `<policy>` | `<XxxRequest>` | `<XxxResponse>` | 200 / 400 / 404 | `ReportManager.API/Controllers/<Xxx>Controller.cs` (nouveau) |

### DTO, entités & modèles
```csharp
// <repo>/<chemin>/XxxDto.cs (nouveau)
public sealed record XxxDto(
    string Id,                 // <sens / origine>
    DateTime? EffectiveDate);  // nullable ⇒ <sémantique du null>
```

```ts
// repos/pf-web/libs/report/<…>/xxx.model.ts (nouveau)
export interface Xxx {
  readonly id: string;
  readonly effectiveDate: string | null; // ISO-8601
}
```

### Signatures de méthodes
| Fichier (nouveau / modifié) | Signature | Rôle |
|---|---|---|
| `<…>/IXxxService.cs` (nouveau) | `Task<Result<XxxDto>> GetXxxAsync(string id, CancellationToken cancellationToken)` | <une ligne> |
| `<…>/XxxService.cs` (modifié) | `Result<Xxx> Map(<…>)` | <une ligne> |
| `<…>/xxx.component.ts` (nouveau) | `readonly value = input.required<Xxx>()` / `readonly changed = output<Xxx>()` | <une ligne> |

### Persistance & migration
- Table `<…>` — colonne `<…>` (`<type>`, null/not null) via `exec spAddColumn` sous `PM/SupportFiles/MigrationScripts/<ver>/`

### Config, clés & constantes
- `PARAM_<…>` / `PREF_<…>` — <InitialValue, ValueProviderFunction associée, executer Pre/Post>
- Clé de traduction `RPT_mgr_<…>` — <source : rapport frère déjà migré ; jamais inventée>
- Setting `appsettings` `<…>` — <défaut, portée>

## Étapes
<ordonnées et concrètes. Pour un travail multi-repo/multi-langage, regroupe sous `#### <repo-or-lang>`.
Chaque étape qui crée du code renvoie au contrat correspondant ci-dessus plutôt que de le redécrire.>

#### <repo-or-lang A>
1. <étape>
2. <étape>

#### <repo-or-lang B>
1. <étape>

## Tests
- <ce qu'il faut tester> — palier : <SmallTests / MediumTests / Vitest / E2E> — se rattache à l'Étape <n>

## Risques & changements incompatibles
- <répercussion sur une lib partagée, changement de contrat/DTO, migration, risque de fidélité C++→C#>

## Points de décision
| # | Décision | Options considérées | Choix | Justification | Status |
|---|---|---|---|---|---|
| 1 | <…> | A / B | A | <pourquoi> | resolved |
| 2 | <…> | X / Y | — | <pourquoi ça requiert l'utilisateur> | needs-user |

_Toute ligne `needs-user` doit aussi apparaître dans Questions ouvertes et maintient le plan en `draft`._

## Estimation
_Taille en T-shirt → temps-ingénieur idéal : XS ≤ 2h · S ≈ ½ journée · M ≈ 1-2 jours · L ≈ 3-5 jours · XL > 1 semaine (à découper)._

| Étape | Taille | Temps idéal | Notes |
|---|---|---|---|
| Étape 1 — <…> | S | ~½ journée | |
| Étape 2 — <…> | M | ~1-2 jours | |
| Tests (élément 5) | S | ~½ journée | |

- **Par repo (multi-repo uniquement) :** <repo A : M · repo B : S>
- **Global :** <taille> — <fourchette, ex. 3-5 jours idéaux>
- **Confiance :** <high / medium / low>
- **Ce qui la détermine :** <les 1-3 hypothèses / inconnues / risques XL-ou-question-ouverte qui font bouger le chiffre>

## Questions ouvertes (à résoudre au gate plan)
- <…>
