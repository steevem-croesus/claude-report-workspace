---
name: activate-web-report-pref
description: Active la PREF du rapport (PREF_REPORT_*=YES) dans la BD dev via croesus.sql. Utiliser après register-web-report et avant update-e2e-baselines lors de la migration d'un rapport vers Xpert, sinon le rapport ne sera pas visible sur les BDs dev.
allowed-tools: Read, Edit, Grep, Bash
---

# Skill: Activate Web Report Pref

Active la `PREF_REPORT_*=YES` du rapport dans `B_FIRM.CONFIG_TXT` (firmes 1, 2, 3) via `PM/SupportFiles/DBConfig/croesus.sql`.

**Utilisé par:** report-developer (entre `register-web-report` et `update-e2e-baselines`)

---

## Quand utiliser ce skill

Après avoir enregistré un nouveau rapport dans `WebRTMRunner.cs`. Sans cette étape, le rapport ne sera pas visible dans Xpert sur les BDs dev (firmes 1, 2, 3) parce que sa PREF n'est pas activée dans le backup S3 actuel.

Référence : [RPT-19901](https://croesus-support.atlassian.net/browse/RPT-19901), [PR #10755](https://github.com/croesusfin/monolith/pull/10755).

---

## Input

- **Nom interne du rapport** (REPORT_NAME) : ex `EVAL_AVAN`. Trouvable dans `RPT_NomDuRapport.cs` :
  ```csharp
  public static readonly string ReportName = "EVAL_AVAN";
  ```

---

## Étape 1 : Vérifier la PREF principale et ses dépendances

Lire `B_REPORT.PREF_VALIDATION` pour le rapport. Format typique :
- `PREF_REPORT_EVAL_AVAN=YES,PREF_TAX_LOT=NO` → la PREF a une condition secondaire `PREF_TAX_LOT=NO` qui doit être satisfaite par la firm config dev (sinon le rapport ne sera pas généré même avec la PREF activée).

---

## Étape 2 : Localiser le bloc d'activation dans croesus.sql

```bash
grep -n "Activation des PREFs Xpert manquantes \[RPT-19901\]" PM/SupportFiles/DBConfig/croesus.sql
```

---

## Étape 3 : Insérer la nouvelle PREF en ordre alphabétique

Le bloc ressemble à :

```sql
-- Activation des PREFs Xpert manquantes [RPT-19901]
update B_FIRM set CONFIG_TXT = convert(varchar(16000), CONFIG_TXT) + '
PREF_REPORT_EVAL_AVAN=YES
PREF_REPORT_EVAL_INTER=YES
...
PREF_REPORT_PMFA_COVERPAGE2=YES
'
where FIRM_ID in (1, 2, 3)
  and CONFIG_TXT not like '%PREF_REPORT_EVAL_AVAN=YES%'
go
```

Insérer la nouvelle ligne `PREF_REPORT_<REPORT_NAME>=YES` à la position alphabétique correcte.

**Ne pas modifier** la clause `and CONFIG_TXT not like '%PREF_REPORT_EVAL_AVAN=YES%'` — c'est le canary du guard idempotent.

---

## Checklist finale

- [ ] PREF identifiée et conditions secondaires vérifiées
- [ ] Ligne ajoutée dans le bloc `[RPT-19901]` en ordre alphabétique
- [ ] Guard idempotent préservé
- [ ] Skill `update-e2e-baselines` à invoquer ensuite (les baselines vont casser)

---

## Rapport de fin

1. **PREF activée** : `PREF_REPORT_<REPORT_NAME>=YES`
2. **Position** : entre quelles entrées elle a été insérée
3. **Fichier modifié** : `PM/SupportFiles/DBConfig/croesus.sql`
4. **Prochaine étape** : invoquer `update-e2e-baselines`
