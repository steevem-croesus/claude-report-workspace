# Migration Report: FBNGP_Q_ASSETMIX (Backend)
**Date:** 2026-07-23 15:45:00
**Mode:** Backend

[15:45:00] [ÉTAPE 0] Bootstrap depuis l'analyse existante — ✓
- analysis.md trouvé : docs/reports/FBNGP_Q_ASSETMIX/analysis.md
- Ticket Jira : RPT-19569 (En cours) — https://croesus-support.atlassian.net/browse/RPT-19569
- Total paramètres : 21 (2 PRE + 19 POST)
- VPF Cat. A (réutilisation) : 1 | Cat. B (InitialValue) : 5 | Cat. C (nouvelles) : 3 | Cat. D (déclaratif) : 12
- Limites flagged : 2 (DESC_REPARTITION_GP1859 non résolu ; fall-through C++ AssetMixSumGP1859SpecificJoin)

[15:50:00] [ÉTAPE 0.3] Investigation des limites flagged — ✓
- DESC_REPARTITION_GP1859 : introuvable dans CroesusServer/Src, ../monolith/PM, ../monolith/CFF (#define hors sources accessibles)
- AssetMixSumGP1859SpecificJoin : valeurs par pad littérales dans validation_hided.c:9009 ; switch sans `break` → fall-through Client/Account/Link → valeur `-LINK`

[16:05:00] [ÉTAPE 5] Implémentation Parameters.cs (21 params) — ✓
[16:06:00] [ÉTAPE 5] Enregistrement clé "EndOfLastQuarter" (Pre-executer, réutilise LastQuarterEndDateParameter + BatchEndOverride) — ✓
[16:06:30] [ÉTAPE 5] register-ignore-id-masking : FBNGP_Q_ASSETMIX ajouté (liste + InlineData) — ✓
[16:07:00] [ÉTAPE 5] register-web-report : RPT_FBNGPAssetAllocationQuarterly.ReportName ajouté (WebRTMRunner) — ✓
[16:10:00] [ÉTAPE 6] Build ReportManagerApi (dotnet) — ✓ 0 erreur
[16:12:00] [ÉTAPE 6] Tests Infrastructure.SmallTests (filtre GetDisplayUnmaskedId + LastQuarterEndDate) — ✓ 100/100
[16:15:00] [ÉTAPE 6] Build RTMTester (MSBuild) — ✓ ReportServices.dll + RTMTester.exe, 0 erreur

---

## Résumé
| Métrique | Valeur |
|----------|--------|
| Paramètres traités | 21/21 |
| Cat. A (framework / commentaire seul) | 12 |
| Cat. A' (config incomplète) | 0 |
| Cat. B (InitialValue) | 7 |
| Cat. C (Pref) | 0 |
| Cat. D (VPF existante réutilisée) | 2 |
| Cat. E (Radio/Combo) | 0 |
| Cat. F (Nouvelle classe) | 0 |
| Fichiers modifiés | 5 |
| Classes créées | 0 |
| Tests ajoutés | 1 (InlineData GetDisplayUnmaskedId) |
| Traductions | 0 clé |
| Divergences C++ corrigées | 0 |
| Build | ✓ (ReportManagerApi + RTMTester) |
| Tests | ✓ (100/100 sur zones modifiées) |

### Détail par catégorie
- **Cat. B — InitialValue (constantes C++)** : `H_PARAM_AssetMixRepartType` = "Allocation - 1859" (DESC_REPARTITION_GP1859, résolu depuis PM/Foundations/BusinessLogic/Api/BusinessLogicDefs.h) ; `PARAM_AddSpecificJoin` = valeur -LINK (fall-through legacy reproduit) ; `PARAM_DataEntryPoint` = "ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1" ; `PARAM_RPTSubId` = "ASMS_ObjTargetLvl1|ASMS_DisplayColorLvl1|RPT_V_AccClassTypeSpec" ; `PARAM_ReportViewIdentifier` = 3 vues (: → grouped details) ; `PARAM_DontDisplayKeyInHeader` = "1" (CheckTrue) ; `PARAM_HideMinMaxTarget` = "1" (CheckTrue override CheckFalse).
- **Cat. D — VPF réutilisée** : `PARAM_EndDate` → clé "EndOfLastQuarter" réutilise `LastQuarterEndDateParameter` (batch-aware via BatchEndOverride) ; `Hided_PARAM_MutFundBreakDown` → override `ValueProviderFunction = "CheckFalse"` (bypass du VPF dynamique MutualFundBreakDown par défaut).
- **Cat. A — déclaratif** : 12 params couverts par initialValue / initialValueFromPref / valueProviderFunction du *ParametersImplementation.cs.

## Décisions appliquées (limites flagged)
1. `DESC_REPARTITION_GP1859` = "Allocation - 1859" (fourni par l'utilisateur, confirmé dans BusinessLogicDefs.h). Nouvelle directive ajoutée à backend-conventions.md + commande : scanner PM/Foundations/ si un #define est introuvable dans CroesusServer/Src.
2. `AssetMixSumGP1859SpecificJoin` : fall-through C++ reproduit (tous pads → valeur -LINK).

## Fichiers modifiés
- **Modifié** : ReportFoundations/ReportImplementations/Implementations/Reports/Main/FBN/AssetAllocationQuarterly/Parameters.cs (21 params, commentaires 3 parties)
- **Modifié** : ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/PreParamEntryValueProviderFunctionsExecuter.cs (clé "EndOfLastQuarter")
- **Modifié** : ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameter.cs (FBNGP_Q_ASSETMIX)
- **Modifié** : ReportManagerApi/ReportManagerAPI.Infrastructure.SmallTests/Repositories/ValueProviderFunctions/Parameters/Hidden/GetDisplayUnmaskedIdParameterTests.cs (InlineData)
- **Modifié** : ReportFoundations/ReportServices/WebRTMRunner.cs (RPT_FBNGPAssetAllocationQuarterly)
