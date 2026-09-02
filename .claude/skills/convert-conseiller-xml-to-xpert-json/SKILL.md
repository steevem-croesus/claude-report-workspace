---
name: convert-conseiller-xml-to-xpert-json
description: Convertit un TaskSpec XML de génération de rapport Conseiller (WPF legacy) en requête JSON Xpert (corps POST de ReportManagerApi, ex. /api/v1/order-entries/reports). Utiliser pour rejouer côté Xpert une génération capturée dans Conseiller, ou préparer un JSON de validation à partir d'un XML de référence.
---

# Skill: Convert Conseiller XML → Xpert JSON

Transforme un `<TaskSpec>` XML (sortie de génération Conseiller / WPF legacy) en **requête de
génération JSON Xpert** — le corps POST attendu par les routes de ReportManagerApi
(ex. `POST /api/v1/order-entries/reports`).

**IMPORTANT : répondre TOUJOURS en français à l'utilisateur.**

> Complément de `compare-report-params` (qui *compare* XML vs JSON). Ici on *génère* le JSON depuis
> le XML. Après conversion, on peut valider avec `compare-report-params`.

## Quand l'utiliser

- Rejouer une génération Conseiller dans Xpert (même rapport, mêmes params).
- Produire un JSON de validation à partir d'un XML de référence.
- Débogage : voir la requête Xpert équivalente à un TaskSpec donné.

## Méthode recommandée : le script

Le mapping est **déterministe** — utiliser le script fourni plutôt que convertir à la main :

```bash
python .claude/skills/convert-conseiller-xml-to-xpert-json/convert_xml_to_json.py \
    input.xml -o output.json \
    --session-id "<uuid>" --session-token "Bearer <jwt>"
```

- Sans `-o` : écrit sur stdout.
- `--session-id` / `--session-token` : voir « Champs non dérivables » ci-dessous.
- Le XML est lu en `ISO-8859-1` (encodage des TaskSpec Conseiller).

Le script est validé sur des paires XML/JSON réelles (ORDER_ENTRY, PROJECTED_PORTFOLIO).

## Le mapping (source de vérité : paires réelles + `report_definitions.proto`)

### Structure

| XML Conseiller | JSON Xpert | Note |
|---|---|---|
| *(constante)* | `name` | `"ReportBatchService"` (pas dans le XML ; override via `--name`) |
| `<Priority>` | `priority` | int |
| `<StandardReportList>/<StandardReport>` | `standardReports[]` | **seuls `rptJoinId` + `params` sont gardés** |
| ↳ `<RptJoinId>` | ↳ `rptJoinId` | int |
| ↳ `<ParamList>/<Param>` | ↳ `params[]` | voir transforms params |
| ↳ `<Name>`,`<RptType>`,`<Order>`,`<LanguageSpec>`,`<CurrencySpec>` | *(supprimés)* | absents du JSON |
| `<CommonBasicReportInfo>` | `commonReportInfo` | sous-ensemble ci-dessous |
| ↳ `<StartPageFrom>` | ↳ `startPageFrom` | int |
| ↳ `<NbPDFTotPage>` | ↳ `pdfTotPage` | int |
| ↳ `<GenerationOrder><FieldToSort>` | ↳ `generationOrder.fieldToSort` | string |
| ↳ `<GenerationOrder><OrderToSort>` | ↳ `generationOrder.sortOrder` | **enum SortOrder** |
| ↳ `<Currency>`,`<Language>`,`<UserTitle>`,`<UserName>` | ↳ `currency`,`language`,`userTitle`,`username` | string |
| ↳ `<Filter>` | ↳ `filter` | **nombre** (`-1.000000` → `-1`) |
| ↳ `<AddUserName>`,`<GroupNode>` | ↳ `addUserName`,`groupNode` | **bool** (`1`→true,`0`→false) |
| ↳ `<MessageInfo>` | ↳ `messageInfo` | `{}` |
| ↳ `<Source>` | ↳ `source` | voir détection source |
| ↳ `<GroupReports>`,`<GroupSecurities>`,`<UsePrimaryAddress>`,`<AddBranchAddress>`,`<UsePdfNamingConvention>`,`<AddContentManagement>`,`<PublishReport>`,`<IsAccessible>` | *(supprimés)* | absents du JSON |
| `<CommonBrokersDiaryReportInfo>` | `brokersDiary` | `{}` |
| `<CommonOrderEntryReportInfo>` | `ordersEntry` | `{}` (noter le pluriel `ordersEntry`) |
| `<GenerationOutput>` | `generationOutput` | **enum GenerationOutput** |
| `<ResultFormat>` | `resultFileFormat` | **enum ResultFileFormat** |
| `<TaskSpecVersion>`,`<TimeZoneDifferential>`,`<DoubleSidedOutput>`,`<SpecialReportList>` (vide) | *(supprimés)* | absents de ce format de requête |

### Transforms sur les paramètres (`<Param>` → `params[]`)

1. **Nom** : `*Hided*PARAM_X` → `*H*PARAM_X`. Les préfixes déjà canoniques `*H*` (hidden) et
   `*T*` (transient) sont **conservés tels quels**. Nom nu → inchangé.
2. **Éclatement des pipes** : une `<Value>` contenant `|` est **éclatée en N entrées**
   `{name, value}` (une par segment), l'ordre est préservé.
   Ex. `PARAM_DataEntryPoint = "A|B|C"` → 3 objets `{name:PARAM_DataEntryPoint, value:A/B/C}`.
   ⚠️ **Ne jamais** splitter sur `:`, `-`, `.` (séparateurs internes de tuples de join).
3. **Normalisation numérique** : un décimal entier `11.000000` → `"11"`. Une date `2026.08.18`
   (pattern `\d{4}.\d{2}.\d{2}`) **n'est pas touchée**. Règle : ne normaliser que `^-?\d+\.0+$`.
4. La valeur reste une **string** dans le JSON (contrairement à `filter`, qui est un nombre).

### Détection du type de source (`<Source>` → `source`)

`BasicReportSourceType` selon le sous-élément peuplé :

| Sous-élément XML peuplé | `sourceType` | Contenu |
|---|---|---|
| `<Selections>/<SelectionList>/<Value>` | `BASIC_RPT_SRC_TYPE_SELECTION` | `selections:[{fieldName, values[]}]` |
| `<Criteria>` non vide | `BASIC_RPT_SRC_TYPE_CRITERIA` | — |
| `<Browser>/<RecordList>` non vide | `BASIC_RPT_SRC_TYPE_BROWSER` | — |
| aucun | `BASIC_RPT_SRC_TYPE_NONE` | — |

`source.browsers` sort toujours à `[{}]` (parité avec la requête réelle). Noter qu'une sélection
`<Value>SOURCE_ALL</Value>` reste une **valeur de sélection** ordinaire (`values:["SOURCE_ALL"]`),
ce n'est pas un type de source distinct.

### Tables d'enum (protobuf `report_definitions.proto` — autoritatif)

**GenerationOutput** (`<GenerationOutput>` → `generationOutput`)
| int | string |
|---|---|
| 0 | `GEN_OUT_UNSPECIFIED` |
| 1 | `GEN_OUT_SINGLE_RESULT_FILE` |
| 2 | `GEN_OUT_MULTI_RESULT_FILE` |
| 3 | `GEN_OUT_EMAIL` |
| 4 | `GEN_OUT_DEBUG_DATASET` |
| 5 | `GEN_OUT_DEBUG_PACKAGE` |
| 6 | `GEN_OUT_TASK_PREVIEW` |

**ResultFileFormat** (`<ResultFormat>` → `resultFileFormat`)
| int | string |
|---|---|
| 0 | `RESULT_FILE_FORMAT_NONE` |
| 1 | `RESULT_FILE_FORMAT_PDF` |
| 2 | `RESULT_DATASET` |
| 3 | `RESULT_DEBUG_PACKAGE` |
| 4 | `RESULT_TASK_PREVIEW` |

**SortOrder** (`<OrderToSort>` → `generationOrder.sortOrder`)
| int | string |
|---|---|
| 0 | `SORT_ORDER_UNSPECIFIED` |
| 1 | `SORT_ORDER_ASCENDING` |
| 2 | `SORT_ORDER_DESCENDING` |

## Champs non dérivables du XML (jetons runtime)

`sessionId` et `sessionToken` **n'existent pas** dans le TaskSpec Conseiller — ce sont des jetons
d'authentification/session produits au runtime Xpert. Le script les laisse vides et émet un
avertissement. Avant d'envoyer la requête à l'API, les renseigner via `--session-id` /
`--session-token` (ou copier ceux d'une requête réelle capturée dans les DevTools réseau /
`launchSettings`).

## Après conversion — valider

Comparer le JSON produit avec la sortie Xpert réelle du même rapport via le skill
`compare-report-params`. Vérifier surtout que :
- le `rptJoinId` correspond au bon rapport ;
- les params POST/Hidden éclatés matchent (après concaténation `|` inverse) ;
- les différences de dates/titres sont attendues (voir `compare-report-params`).

## Pièges connus

| Piège | Détail |
|---|---|
| Splitter un `:`/`-`/`.` | Seul `\|` sépare des valeurs multiples. `:` `-` `.` sont internes → ne pas toucher. |
| Normaliser une date | `2026.08.18` a des points mais n'est **pas** un décimal. Ne normaliser que `^-?\d+\.0+$`. |
| Oublier `*Hided*`→`*H*` | Le XML Conseiller peut écrire `*Hided*`, le JSON Xpert veut `*H*`. `*H*`/`*T*` déjà canoniques. |
| Garder Name/RptType/Order dans le report | Le JSON ne garde que `rptJoinId` + `params` par report. |
| `ordersEntry` vs `orderEntry` | La clé JSON est `ordersEntry` (pluriel). |
| sessionId/Token inventés | Jamais inventer un JWT. Laisser vide et demander à l'utilisateur, ou copier d'une requête réelle. |
