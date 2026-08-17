# Migration Report: FBNGP_Q_ASSETMIX (Validation)
**Date:** 2026-07-30 11:37:22
**Mode:** Validation (Conseiller XML vs Xpert JSON)

[11:37:22] [ÉTAPE 1] Collecte des fichiers XML (Conseiller) et JSON (Xpert) — Résultat ✓
[11:37:22] [ÉTAPE 2] Comparaison des paramètres (21 XML / 20 JSON) — Résultat ✓

## Comparaison détaillée

### PARAM_EndDate (1/21)
- XML: `"2026.06.30"` | JSON: `"2026.06.30"` | ✓ Identique

### PARAM_DataEntryPoint (2/21)
- XML: `"ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1"` | JSON: `"ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1"` | ✓ Identique

### PARAM_ForceCurrency (3/21)
- XML: `"DEFAULT"` | JSON: `"DEFAULT"` | ✓ Identique

### PARAM_RPTSubId (4/21)
- XML: `"ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1|RPT_V_AccClassTypeSpec"` | JSON: `"ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1|RPT_V_AccClassTypeSpec"` | ✓ Identique

### *H*PARAM_AssetMixRepartType (5/21)
- XML: `"Allocation - 1859"` | JSON: `"Allocation - 1859"` | ✓ Identique

### PARAM_AddSpecificJoin (6/21)
- XML: `"ASMS_ObjTargetLvl1:ASSET_MIX_SUM_GP1859-LINK|ASMS_DisplayColorLvl1:ASSET_MIX_SUM_GP1859-LINK"` | JSON: `"ASMS_ObjTargetLvl1:ASSET_MIX_SUM_GP1859-LINK|ASMS_DisplayColorLvl1:ASSET_MIX_SUM_GP1859-LINK"` | ✓ Identique

### PARAM_DisplayDateAndTime (7/21)
- XML: `"1"` | JSON: `"1"` | ✓ Identique

### PARAM_ReportTitle (8/21)
**Valeurs:**
- Conseiller (XML): `"20101331"`
- Xpert (JSON): `"20100717"`

**Verdict: ⚠️ Différence connue**
- `PARAM_ReportTitle` diffère systématiquement entre Conseiller (XML) et Xpert (JSON). C'est une différence connue et indépendante de la migration (identifiant de titre généré différemment dans chaque système). Aucune investigation requise.

### *Hided*PARAM_MutFundBreakDown (9/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_DisplayFirmName (10/21)
- XML: `"1"` | JSON: `"1"` | ✓ Identique

### PARAM_ReportViewIdentifier (11/21)
- XML: `"ASMS_ObjTargetLvl1:AssetMixSummaryDetails|ASMS_DisplayColorLvl1:AssetMixSummaryGroupedDetails|RPT_V_AccClassTypeSpec:ReportAccountTypeReportDetails"` | JSON: `"ASMS_ObjTargetLvl1:AssetMixSummaryDetails|ASMS_DisplayColorLvl1:AssetMixSummaryGroupedDetails|RPT_V_AccClassTypeSpec:ReportAccountTypeReportDetails"` | ✓ Identique

### PARAM_IncludeCoverPage (12/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_UseNbPageTotal (13/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_ReportPad (14/21)
- XML: `"1"` | JSON: `"1"` | ✓ Identique

### PARAM_FirmCurrency (15/21)
- XML: `"CAD"` | JSON: `"CAD"` | ✓ Identique

### PARAM_HideMinMaxTarget (16/21)
- XML: `"1"` | JSON: `"1"` | ✓ Identique

### PARAM_HideTitleCurrency (17/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_IgnoreIdMasking (18/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_DontDisplayKeyInHeader (19/21)
- XML: `"1"` | JSON: `"1"` | ✓ Identique

### PARAM_DisableParamButton (20/21)
- XML: `"0"` | JSON: `"0"` | ✓ Identique

### PARAM_UseRepartitionFromInvObj (21/21)
**Valeurs:**
- Conseiller (XML): `"0"`
- Xpert (JSON): `<absent>`

**Verdict: ❌ Différence fonctionnelle**
- Le paramètre `PARAM_UseRepartitionFromInvObj` est présent dans Conseiller (valeur `"0"`) mais **absent** du JSON Xpert.
  - Piste d'investigation: vérifier le `Parameters.cs` du rapport FBNGP_Q_ASSETMIX — le paramètre est-il déclaré ? Si oui, vérifier s'il a un `InitialValue` (une valeur vide serait strippée avant l'envoi au report server).
  - Cause probable: paramètre non déclaré dans la liste des paramètres du rapport Xpert, ou `InitialValue` vide/manquant provoquant le stripping. La valeur attendue est `"0"`.

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres comparés | 21 |
| Identiques | 19 |
| Différences attendues (date/env) | 1 |
| Différences fonctionnelles | 1 |
| Paramètres XML uniquement | 1 |
| Paramètres JSON uniquement | 0 |
| Verdict | ❌ Échec |

## Différences fonctionnelles

| Paramètre | Conseiller (XML) | Xpert (JSON) | Cause probable | Action suggérée |
|-----------|-----------------|--------------|----------------|-----------------|
| PARAM_UseRepartitionFromInvObj | `0` | `<absent>` | Paramètre non déclaré dans Parameters.cs, ou `InitialValue` vide → strippé | Déclarer le paramètre dans le `Parameters.cs` du rapport avec `InitialValue = "0"` (vérifier d'abord la Default/Specific_Function C++) |

## Différences attendues (connues)

| Paramètre | Conseiller (XML) | Xpert (JSON) | Note |
|-----------|-----------------|--------------|------|
| PARAM_ReportTitle | `20101331` | `20100717` | Différence connue, indépendante de la migration |
