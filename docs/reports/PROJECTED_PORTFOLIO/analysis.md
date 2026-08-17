# Analyse de migration — PROJECTED_PORTFOLIO (Portefeuille projeté)

> Ticket : RPT-18883 « Supporter le rapport Portefeuille projeté par l'api de rapports » · Epic RPT-17650 · Label RTM-WEB.
> Statut : (re)matérialisation de l'analysis.md autoritative. L'analyse embarquée dans le ticket Jira (2026-07-23) a été validée ligne par ligne contre le code réel d'aujourd'hui (C++ CroesusServer, C# ReportFoundations/ReportManagerApi, .resx, docs/fields.csv). Les écarts ticket vs code sont signalés [ECART]. Conventions : .claude/conventions/{migration-protocol,backend-conventions,frontend-conventions}.md.

## 1. Identité du rapport (validée)

| Propriété | Valeur | Source |
|---|---|---|
| Template ID | 5000261 | ticket / docs/template_ids.csv |
| Nom interne | PROJECTED_PORTFOLIO | RPT_ProjectedPortfolio.cs:18 |
| Classe C# | RPT_ProjectedPortfolio : ReportImplementation (partial) | .../Specific/Projected/RPT_ProjectedPortfolio.cs:15 |
| Template | TPL_PortfolioEvaluation, HideProjectedPortefSections = true | RPT_ProjectedPortfolio.cs:45,74 |
| Sub-reports | SUB_ReportHeader, SUB_AccountDetails, SUB_GraphInvObjEval (x2), SUB_MutualFundsAnnex, SUB_CurrencyConversion, SUB_EvalNotes | RPT_ProjectedPortfolio.cs:55-61 |
| Activation | PREF_REPORT_PROJECTED_PORTFOLIO=YES | RPT_ProjectedPortfolio.cs:36 |
| Contexte OrderEntry | IsOrderEntryVisible = true, HelpToken = ORDER_ENTRY_REPORT_PARAM_WINDOW | RPT_ProjectedPortfolio.cs:35,37 |
| Exclusif ? | Non — aucun header.ValidationFunction = SingleSelect / SingleSelectNotSame | frontend : ne PAS ajouter à exclusive-report-names.ts |

Clés .resx (existent, ne pas inventer) : RPT_mgr_rpt_GProjectedPortfolio (nom), RPT_mgr_tit_GProjectedPorfolio (titre — orthographe d'origine Porfolio) dans ReportFoundations/ReportBusinessLogic/Resources/Resource.{,en,fr}.resx.

## 2. Concept fonctionnel

Évaluation d'un portefeuille tel qu'il serait après application d'ordres de rééquilibrage (Order Entry). Par position : quantité actuelle, variation projetée, quantité modifiée, prix/valeur marchande, % du total, gains/pertes réalisés et non réalisés. Sortie : en-tête, détails du compte, graphiques d'allocation (camembert + colonnes), tableau des positions projetées, annexe fonds, conversion de devises, notes.

## 3. RISQUE N.1 — Faisabilité : dépendance au contexte OrderEntry / rééquilibrage

Le rapport est IsOrderEntryVisible = true, HelpToken = ORDER_ENTRY_REPORT_PARAM_WINDOW (RPT_ProjectedPortfolio.cs:35,37). Deux paramètres POST portent le concept projeté :

| Paramètre | Config actuelle | Problème |
|---|---|---|
| PARAM_RebalanceId | Parameters.cs:552 ValidationFunction=GetRebalanceId ; global HiddenParametersImplementation.cs:301 sans valueProviderFunction / initialValue | GetRebalanceId non enregistré (0 Pre/Post). Le RebalanceId vient du wizard desktop (étape 5) — non fourni par le pipeline Xpert async. |
| PARAM_WantProjectedPortfolio | Parameters.cs:515 vide ; global :300 CheckTrue sans initialValue | Constante 1 migrable (cat B), mais sans RebalanceId valide, pas de données projetées à calculer. |

CanCompareReparNo (coeur de EvalGraMustCompareReparNo) lit aussi le contexte desktop vivant : ecran_principale GetNotebook getpad(-1), GetLinkedDataSelection, GetGroupReports (validation_hided.c:7834-7890) — absent en génération web async.

Statut (à valider, section 10 HALT) : même limite que le rapport ORDER_ENTRY. Le paramétrage statique (~55 params structure/prefs/constantes/déclaratifs) est migrable déterministiquement ; la génération réelle du portefeuille projeté reste bloquée sans RebalanceId + contexte de sélection pad.

## 4. Inventaire 67 paramètres (17 PRE + 50 POST)

Rappel (backend-conv) : la clé de lookup C# est valueProviderFunction (named param du *ParametersImplementation.cs) ou la propriété ValueProviderFunction de Parameters.cs. Le 4e positionnel ValidationFunction de Parameters.cs n'est PAS la clé — c'est la config C++ préservée. L'effet réel de chaque POST = le global HiddenParametersImplementation.cs, sauf override (aucun POST override actuellement).

### 4.1 PRE — 17 (visibles)

| # | Paramètre | Widget | Def/Spec | Global (effet réel) | Cat | Cx | Action |
|---|---|---|---|---|---|---|---|
| 1 | PARAM_GeneratedDate | Date | AsOfDate / EvalAsOfDate | DateParametersImplementation.cs:42 AsOfDate, initialValueDateType:LastProcessedDate | D | 1 | Couvert. EvalAsOfDate enreg. PRE (6.1). |
| 2 | PARAM_AssetMixRepartType | Radio | — / AssetMixRadioButton | RadioParametersImplementation.cs:38 initialValue:MultiLevelFirmAssetMix, 3 display (Firm/Basic/Personnal), valueProviderFunction:AssetMixRepartType | E | 2 | [ECART] Specific AssetMixRadioButton non enregistré. Vérifier si SLEEVES requis; override PossibleDisplayValues + ValueProviderFunction dans Parameters.cs. |
| 3 | PARAM_AssetMixRepartitionID | Combo | AssetMixRepartitionCombo / — | ComboParametersImplementation.cs:48 valueProviderFunction:AssetMixRepartitionID (enreg. PRE) | D | 1 | Aucune. |
| 4 | PARAM_AvgCostCalculMethod | Radio | CostCalculation / — | RadioParametersImplementation.cs:41 initialValue:COST_CALC_ACB, 2 display, PrefValidation PREF_TAX_LOT=NO, valueProviderFunction:CostCalculation | E/D | 2 | [ECART] section 7 : CostCalculation non enregistré; risque runtime. Reco : basculer déclaratif. |
| 5 | PARAM_IndCodeCombo | Combo | IndCodeCombo / — | ComboParametersImplementation.cs:57 valueProviderFunction:IndCodeCombo, PrefValidation PREF_DISABLE_INDUSTRY_CODE=NO | D | 1 | Aucune. Observer 8. |
| 6 | PARAM_IndCodeCheck | Check | — / — | CheckBoxParametersImplementation.cs:64 initialValue:0, PrefValidation PREF_DISABLE_INDUSTRY_CODE=NO | D | 0 | Déclaratif. Observer 8. |
| 7 | PARAM_RegionCheck | Check | — / — | CheckBoxParametersImplementation.cs:100 initialValue:0 | D | 0 | Déclaratif. Observer 8. |
| 8 | PARAM_GainLossCostDisplayed | Check | — / CheckTrue | CheckBoxParametersImplementation.cs:54 initialValue:1, PrefValidation PREF_STRIP_BOND_GL1=NO,PREF_ADD_THEORETICAL_VALUE=YES | D | 0 | Specific CheckTrue=1 déjà. |
| 9 | PARAM_OptionCost | Check | CheckFalse / — | CheckBoxParametersImplementation.cs:74 initialValue:0, PrefValidation PREF_OPTION_ALWAYS_TRF_COST=YES | D | 0 | Déclaratif. |
| 10 | PARAM_DisplayCheckDigit | Check | InitDisplayCheckDigit / — | CheckBoxParametersImplementation.cs:53 valueProviderFunction:InitDisplayCheckDigit (enreg. PRE), PrefValidation PREF_DISPLAY_CHECK_DIGIT=YES | D | 0 | Aucune. |
| 11 | PARAM_AccountCurrencyCheck | Check | AccountCurrencyCheck / CheckFalse | CheckBoxParametersImplementation.cs:44 valueProviderFunction:VisibleForRelationOrClientOnly, initialValue:0 | D | 0 | Specific CheckFalse=0 ; VPF gère visibilité. |
| 12 | PARAM_IncludeGraphic | Check | CheckFalse / — | CheckBoxParametersImplementation.cs:62 initialValue:0 | D | 0 | Déclaratif. |
| 13 | PARAM_MutualFundAnnex | Check | — / — | CheckBoxParametersImplementation.cs:70 initialValue:0, PrefValidation PREF_ENABLE_ALLOC_FUNDS=YES | D | 0 | Déclaratif. Observer 8. |
| 14 | PARAM_MutualFundBreakDown | Check | — / — | CheckBoxParametersImplementation.cs:71 initialValue:0, PrefValidation PREF_ENABLE_ALLOC_FUNDS=YES,PREF_ENABLE_ALLOC_FUNDS_IN_REPORT=YES | D | 0 | Déclaratif. Observer 8. |
| 15 | PARAM_UseRepartitionFromInvObj | Check | CheckFalseVisibleForRelOnly / — | CheckBoxParametersImplementation.cs:114 valueProviderFunction:CheckFalseVisibleForRelOnly (enreg. PRE), initialValue:0, PrefValidation PREF_ENABLE_ASSET_INDEX=YES | D | 0 | Aucune. |
| 16 | PARAM_SortByField | Combo | — / EvalSortByCombo | ComboParametersImplementation.cs:74 vide (aucun display, aucun VPF) | E | 1 | EvalSortByCombo non enregistré; combo déclaratif 5 valeurs (6.2). |
| 17 | PARAM_Pagination | Combo | PaginationVisible / PaginationVisible | ComboParametersImplementation.cs:59 valueProviderFunction:PaginationVisible (enreg. PRE) | D | 0 | Aucune. Frontend : radio-parameter. |

Positions (WindowOrder/Position/PositionH) depuis Parameters.cs : WO1 (GeneratedDate P1 ; DisplayCheckDigit P2H2), WO2 (IndCode/Region grouping), WO3 (AvgCost P1 ; OptionCost P3), WO5 (AssetMix radio+combo+UseRepartition), WO6 (GainLoss P2 ; MutualFund P1-P2), WO8 (SortByField P1H2 ; Pagination P1H1).

### 4.2 POST — 50 (Hidden, widget 8)

#### Cat. A — VPF réelle existante à CABLER (2)

Global sans valueProviderFunction ; ajouter ValueProviderFunction=... sur le param dans Specific/Projected/Parameters.cs. Classe réelle (pas stub) :

| Paramètre | Câblage | Classe C# | Validation |
|---|---|---|---|
| PARAM_DontLoadSubReport (Parameters.cs:167) | ValueProviderFunction=EvalDontLoadSubReport | EvalDontLoadSubReportParameter(ctxRepo) Post-Executer.cs:90 | Global :155 = vide. Requis. |
| PARAM_UseGICSBreakDown (Parameters.cs:495) | ValueProviderFunction=IsReportUseGicsBreakdown | IsReportUseGicsBreakdownParameter(...) Post-Executer.cs:153 | [ECART] Default IsBatchUseGicsBreakdown != Specific. Global :291 initialValue:0 sans VPF; résout à 0. Requis. |

[ECART]/nuance : Parameters.cs porte déjà ValidationFunction=EvalDontLoadSubReport / IsReportUseGicsBreakdown (4e positionnel) — PAS la clé de lookup ; d'où le besoin du named ValueProviderFunction. Ticket correct.

#### Cat. B — Constante C++ vers InitialValue (13)

DECOUVERTE MAJEURE [ECART de raisonnement vs ticket] : les fonctions graph/eval de ces params sont enregistrées mais toutes en () => new UnimplementedParameter() (Post-Executer.cs:91-94,154,187-188) — no-op qui perd la valeur. Le ticket parlait de stubs/absentes ; en réalité présentes mais neutralisées. Conclusion identique : poser la constante InitialValue. Valeurs (virgule vers pipe) :

| Paramètre | Ligne | C++ | Valeur | InitialValue |
|---|---|---|---|---|
| PARAM_WantProjectedPortfolio | :515 | global CheckTrue | 1 | 1 (bloqué section 3) |
| T_PARAM_GraphicComparative | :523 | global CheckTrue | 1 | 1 |
| PARAM_RemoveDisclaimer | :531 | global CheckFalse | 0 | 0 |
| PARAM_NestPointField | :354 | validation_hided.c:7274-7287 | ASM_V_DisplayOrder:OBJ_Percent | ASM_V_DisplayOrder:OBJ_Percent [vérifié] |
| PARAM_NestPointValue | :362 | validation_hided.c:7302-7315 | ASM_V_DisplayOrder:ASSETMIX | ASM_V_DisplayOrder:ASSETMIX [vérifié] |
| PARAM_DataEntryPoint | :98 | validation_hided.c:1990-1993 | RAM_V_Level1Name,PAP_V_Value,ASM_V_LongDesc,ACC_Key | RAM_V_Level1Name pipe PAP_V_Value pipe ASM_V_LongDesc pipe ACC_Key [vérifié] |
| PARAM_RPTSubId | :458 | EvlSimpleGraphGetSubRptField (non enreg.) | (ticket) | [à re-vérifier C++] |
| PARAM_RPTSubEntityToUse | :450 | EvalSimpleGraphSubRptEntity :3650 | (ticket) | [à re-vérifier] |
| PARAM_RMInvObjViewPrmIfNotUse | :442 | EvalSimpleGetViewPrmNotUsed (enreg. Unimpl) | (ticket) | [à re-vérifier] |
| PARAM_RMInvObjFieldIfNotNeed | :434 | EvalGraRMInvObjFieldIfNotNeed (enreg. Unimpl) | (ticket) | [à re-vérifier] |
| PARAM_DontUseViewParams | :170 | EvalDontUseViewParam :823 | (ticket) | [à re-vérifier] |
| PARAM_GroupSecForRptBlock | :218 | EvalPortfGroupSecForRptBlock :889 | (ticket) RAM_V_Level1Name | [à re-vérifier] |
| PARAM_ReportViewIdentifier | :426 | SetEvalReportViewIdentifier :3696 | (ticket) | [à re-vérifier] |

Limite : seuls DataEntryPoint, NestPointField, NestPointValue re-lus/confirmés. Les 7 chaînes longues viennent du ticket 2026-07-23 — backend-migrator DOIT relire chaque fonction C++ avant de figer l'InitialValue (valeur + ordre + séparateur). Alternative : enregistrer un StringParameter dans le Post-executer (convention SetTransReportViewIdentifier).

#### Cat. C/F — Dynamique (2)

- PARAM_MustCompareReparNo (Parameters.cs:314) : C++ EvalGraMustCompareReparNo(:7237) donne 1/0 via CanCompareReparNo(:7821, lit pad/notebook desktop). C# : EvalGraMustCompareReparNo enreg. = UnimplementedParameter (:91) ; mais CanCompareReparNo = vraie classe CanCompareReparNoParameter(ctxRepo) (:79). Global :227 défaut CheckTrue (=1). Cat C. Option 1 (reco) : câbler ValueProviderFunction=CanCompareReparNo (valider cat D C# vs C++). Option 2 : créer EvalGraMustCompareReparNoParameter. Option 3 : fallback InitialValue=1. Contexte pad/notebook absent en web; logique non reproductible fidèlement.
- PARAM_RebalanceId (Parameters.cs:547) : GetRebalanceId non enregistré. Cat F bloqué (section 3).

#### Cat. D — Déjà couvert (~33)

- VPF réelle : ReportPad(GetPad), ReportTitle(diff XML/JSON connue), FirmCurrency(+CAD), MultiSourceValue, IsReportsGrouped(N), IgnoreIdMasking(GetDisplayUnmaskedId,0), SortOrder(GetPrintingOrder), AccSummClmnOrder, DisplayDate, IsCliRootManagement(N, PREF_ENABLE_CLIENT_GROUPING=YES), ParseASMFieldsForEntity(FieldsForEntity=StringParameter Y), UnmaskedAccIdNumbers(20).
- initialValue constant : MetricInTermOf(POS_BACKDATED ; MetricInTermOfPosition=Unimpl mais initialValue couvre), DoGraphs(0), HideIntDivBox(0), CompareReparNo(0), AssetMixMaxLevel(1), DisplayIssuerNote(1), FullAccountDetail(1), RemoveAccDetails(0), NeedAssetMixOnly(1), DoRequestIfBrowSource(MustDoRequest+1), UseOpenDay(PARAM_GeneratedDate ; Specific UseOpenDayOnGeneratedDate non enreg. mais initialValue couvre).
- initialValueFromPref : HideTitleCurrency, DisplayFirmName, DisplayDateAndTime, IsLotDefaultPrice, PrefReportBvMvInd, ExtAccountInstitution, NeedAccountCreation(0+pref).
- H_PARAM_AmortizedIncome : initialValue:0 + initialValueFromParam:PARAM_GainLossCostDisplayed. Couvert.

#### [ECART] Cat. D — DIVERGENCES à valider (obligatoire)

| Paramètre | C++ | C# actuel | Divergence |
|---|---|---|---|
| PARAM_DisplayAscCode (Parameters.cs:106) | GetBoolFromPrefUserAccess(PREF_DISPLAY_ASC_CODE) | DisplayAscCode=FalseParameter (Post-Executer.cs:87) — force false | VPF DIVERGENTE : C# ignore la pref. Simplification web volontaire ou bug ? Global :138 câble déjà valueProviderFunction:DisplayAscCode. |
| H_PARAM_CIBCGainLossCalcul (Parameters.cs:42) | Specific GetBoolFromPref(PREF_STRIP_BOND_GL1) | global :66 initialValue:0 figé, aucune pref | pref non lue. Ajouter initialValueFromPref:PREF_STRIP_BOND_GL1 (niveau rapport) ou accepter 0 ? |
| PARAM_IsCliRootManagement | 2 logiques distinctes (note globale :201-205) | classe réelle simplifiée à N | Valider que la simplification convient au grouping client du rapport projeté. |

## 5. Enregistrement WebRTMRunner — REQUIS (confirmé absent)

RPT_ProjectedPortfolio.ReportName est absent de ConstructSupportedWebReportList (ReportFoundations/ReportServices/WebRTMRunner.cs:39-128, 86 entrées). Ticket point #2 validé. Insertion alphabétique entre RPT_ProjectedIncomePeriod (:111) et RPT_ProjectionAccumulatedInterest (:112). Sans cet ajout, le rapport reste invisible dans Xpert (anti-pattern #3). Aussi : PARAM_IgnoreIdMasking a initialValue:0 ; register-ignore-id-masking (GetDisplayUnmaskedIdParameter / ReportsWithInitialValueZero + InlineData).

## 6. Vulgarisation C++ (fonctions non triviales)

### 6.1 EvalAsOfDate (PRE, Date) — PARAM_GeneratedDate

Enregistré PRE : BatchEndOverride(new LastProcessedDateParameter(parameterDateValueService, DateTimeFormat.API_LONG_DATE_STANDARD)) (Pre-Executer.cs:106). Retourne la date de dernier traitement, batch-aware. Le global date (:42) donne déjà ce défaut via initialValueDateType:LastProcessedDate. Câbler ValueProviderFunction=EvalAsOfDate seulement si un affichage PRE le requiert ; format PRE API_LONG_DATE_STANDARD (yyyy-MM-dd).

### 6.2 EvalSortByCombo (PRE, Combo) — PARAM_SortByField vers combo déclaratif

validation_combo.c:7092 (InitEvalSortByCombo) : 5 captions, Select(0) par défaut. GetEvalSortByCombo(:7165) mappe via win_prm_const.h:237-241 (résolus) :

| Idx | Valeur | Caption C++ | Label FR |
|---|---|---|---|
| 0 (défaut) | SBA_ExpDate | CRESUS_rpt_param_lab_GMaturity | Échéance |
| 1 | SBA_V_Desc | CRESUS_rpt_param_lab_GSecurityDescription | Description du titre |
| 2 | PBA_V_PercentTotVal | CRESUS_rpt_param_lab_GPercentageOfTotal | Pourcentage du total |
| 3 | PBA_V_TotalReturnPercentage | CRESUS_rpt_param_lab_GTotReturnPercent | Pourcentage rendement total |
| 4 | PBA_V_GainsLoss | CRESUS_rpt_param_lab_GUnrealGainLoss | Gain/perte non réalisé |

Impl : config déclarative ComboParametersImplementation.cs:74 (vide aujourd hui) : initialValue:SBA_ExpDate, possibleValues (5 clés), possibleDisplayValues (clés RPT_mgr_...). [ECART traductions] Les captions C++ CRESUS_rpt_param_lab_G* sont absentes des .resx de ReportManagerApi (vérifié). Créer 5 clés RPT_mgr_... en récupérant les libellés réels dans la localisation Conseiller (.properties/.rc/.msg) — ne pas inventer (Q3).

### 6.3 EvalGraMustCompareReparNo / CanCompareReparNo

EvalGraMustCompareReparNo(:7237) pose 1 si CanCompareReparNo vrai sinon 0. CanCompareReparNo(:7821) vrai selon provenance pad (compte donne toujours vrai ; portefeuille dépend du nb items liés=1 + type source + GroupReports=Y). Fortement couplé au desktop (notebook). Décision : cat C ci-dessus.

## 7. Point chaud #4 — CostCalculation (PARAM_AvgCostCalculMethod)

RadioParametersImplementation.cs:41 déclare valueProviderFunction:CostCalculation, mais CostCalculation reste non enregistré NI Pre NI Post (0). Risque runtime (clé introuvable à la résolution). Le radio a déjà une config déclarative complète (initialValue:COST_CALC_ACB, 2 display, PrefValidation PREF_TAX_LOT=NO) et la note de code confirme la simplification web (valeur initiale toujours Book Value). Recommandation : basculer déclaratif — retirer le named valueProviderFunction:CostCalculation du global (garder initialValue + displays). [Impact transverse] global partagé par tous les rapports utilisant PARAM_AvgCostCalculMethod ; vérifier qu aucun autre ne dépend d une vraie VPF CostCalculation avant retrait, sinon créer la classe. À trancher au gate (Q1).

## 8. Observer patterns frontend (validés win_prm_grp_*.c)

Constantes win_prm_const.h:268-269 : ASSET_MIX_PERSONNAL=PERSONNAL_ASSETMIX_REPAR, ASSET_MIX_SLEEVES=SLEEVES. Tous pilotés par le radio PARAM_AssetMixRepartType ; ils s activent car source ET cibles sont des PRE présents.

| # | Source vers Cible(s) | Condition | Effet | Réf. C++ | Angular |
|---|---|---|---|---|---|
| 1 | AssetMixRepartType vers IndCodeCheck, RegionCheck, MutualFundBreakDown, MutualFundAnnex | == PERSONNAL OU == SLEEVES | disable + décoche | win_prm_grp_check.c:399-425 (WATCH_DISABLE_CHECK_IF_ASMPERSO_OR_ASMSLEEVES), notif :1273,1279 | setupControlDisabling(form, ASSET_MIX_REPART_TYPE, [IND_CODE_CHECK,REGION_CHECK,MF_BREAKDOWN,MF_ANNEX], v => v===PERSONNAL_ASSETMIX_REPAR OU v===SLEEVES, false) |
| 2 | IndCodeCheck vers IndCodeCombo | décoché | disable | win_prm_grp_combo.c:905-916, notif :1491 | setupControlDisabling(form, IND_CODE_CHECK, [IND_CODE_COMBO], v => v==false) |
| 3 | AssetMixRepartType vers IndCodeCombo | == PERSONNAL | disable | win_prm_grp_combo.c:917-922, notif :1492 | setupControlDisabling(form, ASSET_MIX_REPART_TYPE, [IND_CODE_COMBO], v => v===PERSONNAL_ASSETMIX_REPAR) |
| 4 | AssetMixRepartType vers AssetMixRepartitionID | != PERSONNAL | disable (PERSONNAL donne enable) | win_prm_grp_combo.c:930-941,1494-1497 (WATCH_REPARTITION_COMBO) | setupControlDisabling(form, ASSET_MIX_REPART_TYPE, [ASSET_MIX_REPARTITION_ID], v => v!==PERSONNAL_ASSETMIX_REPAR) |

[ECART vs ticket] conforme, avec 2 précisions : (a) le pattern #1 déclenche aussi un décochage (3e arg false), pas seulement un disable ; (b) aucun Observer pour SortByField, Pagination, AvgCostCalculMethod, OptionCost, IncludeGraphic, GainLossCostDisplayed, DisplayCheckDigit, AccountCurrencyCheck, UseRepartitionFromInvObj, GeneratedDate. Périmètre frontend à trancher (Q0).

## 9. Estimation, confiance, questions

Synthèse catégories (backend) :
- A (câbler VPF réelle) : 2 — DontLoadSubReport, UseGICSBreakDown.
- B (InitialValue constant) : 13 — 6 confirmés (DataEntryPoint, NestPointField, NestPointValue, WantProjectedPortfolio (bloqué), GraphicComparative, RemoveDisclaimer) + 7 chaînes longues à re-vérifier.
- C/F (dynamique) : 2 — MustCompareReparNo (réutiliser CanCompareReparNo / fallback 1) ; RebalanceId (bloqué OrderEntry).
- E (déclaratif/override) : 3 — SortByField (5 valeurs + traductions), AvgCostCalculMethod (déclaratif), AssetMixRepartType (override si Sleeves).
- D (aucune action / valider) : ~33, dont 3 divergences (DisplayAscCode, CIBCGainLossCalcul, IsCliRootManagement).
- Enregistrements : WebRTMRunner (+ register-ignore-id-masking), activate-web-report-pref.

Effort : moyen (M). Essentiel déclaratif/constantes. Poids réel = re-vérif des 7 chaînes C++ + 3 divergences + décision CostCalculation. Confiance : élevée sur structure/catégories (validé contre le code) ; moyenne sur les valeurs des 7 chaînes longues (issues du ticket, non re-lues). Vrai risque = fonctionnel (OrderEntry, section 3), pas technique.

Questions ouvertes (gate) :
- Q0 Périmètre : backend seul, ou backend + frontend (composant + observers section 8) ?
- Q1 CostCalculation : déclaratif (reco, impact transverse à vérifier) ou créer/enregistrer la VPF ?
- Q2 Faisabilité OrderEntry (RISQUE N.1) : migrer le déterministe + différer la génération projetée (comme ORDER_ENTRY), ou attendre le RebalanceId/contexte pad ?
- Q3 Traductions : libellés réels des 5 valeurs SortByField (clés RPT_mgr_...) — récupérer, ne pas inventer.
- Q4 Chaînes C++ longues : re-lecture obligatoire des 7 fonctions avant de figer chaque InitialValue.
- Q5 Divergences D : DisplayAscCode, CIBCGainLossCalcul — corriger ou accepter la simplification web ?

## 10. HALT (décision utilisateur requise)

HALT: décision utilisateur requise

Raison : PROJECTED_PORTFOLIO dépend du contexte OrderEntry/rééquilibrage (PARAM_RebalanceId via GetRebalanceId, NON enregistré ; CanCompareReparNo lit le pad/notebook desktop vivant), non fourni par le pipeline Xpert async standard. Même limite que ORDER_ENTRY. Le paramétrage statique est migrable, mais la génération réelle du portefeuille projeté est bloquée sans RebalanceId.

Question : Migre-t-on maintenant le paramétrage déterministe (enregistrement web + ~55 paramètres statiques/déclaratifs) en différant la génération projetée, ou suspend-on la story jusqu à ce que le pipeline Xpert fournisse le contexte de rééquilibrage ? Et : périmètre backend seul ou backend+frontend ?

Défaut proposé : Migrer le déterministe (comme ORDER_ENTRY), documenter le blocage RebalanceId dans le plan, ne pas promettre de contenu projeté généré. Backend en premier ; frontend en phase 2.

État : Analyse complète et validée contre le code réel. Catégories A-F fixées ; restent au gate Q0-Q5 (dont CostCalculation déclaratif vs VPF, et re-vérification des 7 chaînes C++ longues avant implémentation).

---

report-analyst — validé contre le code réel le 2026-08-11. Sources : RPT_ProjectedPortfolio.cs, Specific/Projected/Parameters.cs, HiddenParametersImplementation.cs, ComboParametersImplementation.cs, RadioParametersImplementation.cs, CheckBoxParametersImplementation.cs, DateParametersImplementation.cs, Pre/PostParamEntryValueProviderFunctionsExecuter.cs, WebRTMRunner.cs, CroesusServer/Src/ReportApi/.../validation_hided.c, validation_combo.c, win_prm_const.h, win_prm_grp_check.c, win_prm_grp_combo.c, docs/fields.csv, ticket RPT-18883.
