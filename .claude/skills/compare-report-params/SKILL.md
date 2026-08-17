---
name: compare-report-params
description: Compare les paramètres d'un rapport entre Conseiller (XML) et Xpert (JSON) pour identifier les différences de valeurs. Utiliser pour valider qu'une migration backend produit les mêmes paramètres.
---

# Skill: Compare Report Params

Compare les paramètres de rapport entre la sortie Conseiller (XML) et la sortie Xpert (JSON) pour détecter les différences. Ce skill fonctionne en **2 phases** alignées avec le cycle de migration.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Phase 1 — AVANT l'implémentation (XML optionnel mais recommandé)

**But :** Avoir une vue d'ensemble des paramètres du rapport et leurs valeurs par défaut pour anticiper les comportements à implémenter.

**À ce stade, le JSON n'existe PAS encore** (il sort seulement après la génération du rapport côté Xpert, ce qui nécessite l'implémentation).

### Que faire avec le XML en Phase 1

Demander à l'utilisateur :
> "Si possible, fournis le XML de génération du rapport depuis Conseiller (legacy WPF) avec les sélections par défaut. Ça permettra d'anticiper les valeurs attendues pour chaque paramètre POST/Hidden."

Si fourni :
- Parser les `<Param>` du XML
- Noter les valeurs attendues pour chaque paramètre (surtout POST/Hidden)
- Utiliser ces valeurs comme référence pendant l'implémentation

Si non fourni : continuer l'implémentation normalement. Le XML sera demandé en Phase 2.

## Phase 2 — APRÈS l'implémentation (validation obligatoire)

**But :** Valider que l'implémentation Xpert produit les mêmes paramètres que le C++ Conseiller.

### Ce qu'il faut demander à l'utilisateur

**Cas A — Le XML a été fourni en Phase 1 :**
- Ne PAS redemander le XML (sauf si l'utilisateur a changé de contexte)
- Demander uniquement le **JSON de génération Xpert**
- **Rappeler explicitement à l'utilisateur** : *"Utilise le même compte/relation, le même source type (Account/Relationship/Portfolio/etc.), et les mêmes choix de paramètres que pour le XML fourni en Phase 1, pour que la comparaison soit valide."*

**Cas B — Le XML n'a PAS été fourni en Phase 1 :**
- Demander les **DEUX** : XML Conseiller ET JSON Xpert
- Préciser qu'ils doivent provenir du même rapport, même compte, même source type et mêmes sélections utilisateur

## Processus de comparaison (Phase 2)

### 1. Valider les inputs

Vérifier :
- Le `RptJoinId` du XML correspond au `rptJoinId` du JSON (même rapport!)
- Le `Name` du XML correspond au rapport attendu
- Le contexte source est cohérent (Account dans les deux, ou Relationship dans les deux)

**Si les IDs ne correspondent pas → ALERTER immédiatement et ne pas continuer.**

### 2. Parser les paramètres

**XML (Conseiller):**
- Extraire chaque `<Param>` avec `<Name>` et `<Value>`
- Stocker dans un dictionnaire `{ name: value }`

**JSON (Xpert):**
- Extraire chaque objet `{ name, value }` du tableau `params`
- **Concaténer** les valeurs des paramètres ayant le même `name` avec le séparateur `|`
- Stocker dans un dictionnaire `{ name: valeur_concatenée }`

### 3. Comparer les paramètres

Pour chaque paramètre, comparer les valeurs entre XML et JSON.

**Classifier chaque différence:**

| Type | Description | Exemple |
|------|-------------|---------|
| **Format de date** | Même date, format différent (`.` vs `-`) | `2026.04.07` vs `2026-04-07` |
| **Valeur de date** | Dates différentes (environnements différents, LastProcessedDate, etc.) | `2026.04.07` vs `2010-01-25` |
| **Valeur utilisateur** | L'utilisateur a fait des choix différents (radio, combo) | `PERSONNAL_ASSETMIX_REPAR` vs `MultiLevelFirmAssetMix` |
| **Valeur différente** | Valeur fonctionnellement différente (non-date, non-choix) | `N` vs `Y` |
| **Manquant dans Xpert** | Paramètre présent dans XML mais absent du JSON | |
| **Manquant dans Conseiller** | Paramètre présent dans JSON mais absent du XML | |
| **Identique** | Même valeur | |

**Règles de comparaison:**
- Ignorer les différences de format de date (`yyyy.MM.dd` vs `yyyy-MM-dd`) — c'est normal
- `PARAM_ReportTitle` aura des valeurs différentes entre environnements — c'est attendu
- Les paramètres PRE (Combo, Radio, Checkbox, Date) peuvent différer si l'utilisateur a fait des choix différents — **ce ne sont PAS des bugs**
- Les vraies différences fonctionnelles sont les **paramètres POST/Hidden** qui diffèrent

### 4. Afficher le résultat

```
📊 Comparaison des paramètres — {NOM_RAPPORT} ({CONTEXT})

Total: {n} paramètres XML | {m} paramètres JSON (après concaténation)

✅ Identiques: {x} paramètres
⚠️ Différences: {y} paramètres
❌ Manquants: {z} paramètres

--- DIFFÉRENCES ---

| Paramètre | Conseiller (XML) | Xpert (JSON) | Type | Action |
|-----------|-----------------|--------------|------|--------|
| ... | ... | ... | ... | ... |

--- VERDICT ---

{Si aucune différence fonctionnelle réelle}
✅ Les paramètres sont fonctionnellement équivalents.

{Si différences fonctionnelles}
❌ {n} différence(s) fonctionnelle(s) détectée(s) — à investiguer et corriger.
```

### 5. Pour chaque différence fonctionnelle, investiguer

**OBLIGATOIRE pour chaque paramètre POST/Hidden avec une valeur différente :**

1. **Lire le VPF C# responsable** — Trouver la classe ValueProviderParameter dans l'executer (Pre ou Post) et lire son code
2. **Lire le C++ original** — Comparer avec la logique C++ de la fonction spécifique
3. **Identifier la cause racine** :
   - VPF a une logique supplémentaire absente du C++ (ex: lecture de cross-parameter metadata)
   - VPF manquant — la logique C++ n'est pas implémentée côté web
   - Infrastructure manquante — le VPF ne peut pas accéder à l'info nécessaire (ex: access level)
4. **Proposer un fix** avec code concret

### 6. Vérifications croisées des VPF (leçon apprise)

**CRITIQUE: Avant de déclarer un paramètre "couvert par le VPF par défaut", vérifier :**

1. **Le VPF lit-il d'autres paramètres ?** Chercher `reportMetaDataFromRtm.Parameters`, `ParametersSoFar`, `GlobalParameters` dans le code du VPF. Si oui, vérifier que les valeurs qu'il lit sont correctes dans le contexte de CE rapport spécifique.

2. **Le VPF a-t-il des shortcuts/court-circuits ?** Chercher des `return parameter` précoces dans le code. Si oui, vérifier que le court-circuit ne se déclenche pas incorrectement pour ce rapport.

3. **Le VPF accède-t-il à des infos utilisateur ?** Chercher `AccessLevel`, `SourceType`, `RequestSourceType`. Vérifier que le contexte web produit le même résultat que le C++ desktop.

## Pièges connus (leçons apprises)

| Piège | Description | Exemple |
|-------|-------------|---------|
| **VPF cross-param** | Un VPF qui lit un autre paramètre depuis les metadata RTM peut produire un résultat incorrect si ce paramètre a été overridé dans Parameters.cs | `IsCliRootManagementParameter` lit `GroupNodeForcedValue.InitialValue` → court-circuite vers "Y" quand InitialValue="1" |
| **Access level via IUserHandler** | `IUserHandler.GetSessionFactory().CurrentUser.AccessLevel` donne le `CroesusAccessLevel` (Sysadm, Firmadm, Rep, etc.). Ajouter `IUserHandler` au constructeur de l'executer si nécessaire | `DisplayFirmNameIfNotFirmAdmParameter` utilise `IUserHandler` pour forcer "0" pour les firm admins |
| **RepartitionService filtre FirmId** | `GetRepartitions()` filtre par `FirmId == CurrentUser.FirmId`. Les repartitions prédéfinies système sont exclues. Utiliser `GetFinancialInstrumentPredefinedRepartition()` pour les inclure | "Instrument Financier" (prédéfinie système) n'apparaissait pas dans le combo IAVM |
| **ValueProviderFunction="" ne marche pas** | `JsonSource.cs` traite `""` comme `null` via `string.IsNullOrEmpty()`. Le VPF par défaut s'exécute quand même. Créer un VPF dédié à la place | `IsCliRootManagementWithoutGroupNodeShortcutParameter` créé car `""` ne bypassait pas le standard |
| **Simplification fausse** | Déclarer "pref couvre le comportement web" sans vérifier que le VPF produit la bonne valeur | Toujours comparer XML vs JSON avant de conclure |
