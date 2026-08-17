---
name: create-migration-pr
description: Crée une PR monolith pour une migration backend Xpert avec une description structurée (Objectif / Changements clés / Validation / À finaliser) calquée sur le format standard des PR de migration. Configure aussi les Prefs (croesus.sql) des rapports gated par une PREF. À exécuter APRÈS la migration backend d'un ou plusieurs rapports (VPFs implémentées, enregistrements faits, build + tests verts). Respecte les conventions git du monolith (commitlint, squash, draft).
allowed-tools: Read, Grep, Glob, Edit, Bash
---

# Skill: Create Migration PR

Génère et crée une **pull request du monolith** pour une migration backend Xpert, avec une description
riche et fidèle au diff, dans le format standard des PR de migration (références : PR #11943, PR #12036).
Inclut la **configuration des Prefs** (`croesus.sql`) des rapports gated par une PREF.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

**Utilisé par:** `backend-migrator` (ou l'utilisateur) comme **étape finale**, une fois l'implémentation
backend terminée et validée localement.

Pour les règles de branches/commits/titres, s'appuyer sur le skill **`git-conventions-monolith`**. Pour
le détail de l'activation d'une PREF, s'appuyer sur le skill **`activate-web-report-pref`**. Ce skill les
applique, il ne les répète pas.

---

## Quand utiliser ce skill

Après la migration backend d'un ou plusieurs rapports, quand **tous** ces prérequis sont réunis :

- [ ] VPFs implémentées + enregistrées (Pre/PostExecuter), rapport(s) dans `WebRTMRunner`.
- [ ] Prefs configurées dans `croesus.sql` (voir étape 2 — sinon le rapport n'est pas visible en dev).
- [ ] `dotnet build` OK et `Infrastructure.SmallTests` verts (skill `rebuild-before-validation`).
- [ ] Les changements sont **commités** sur une branche `feature/RPT-<ticket>` (pas sur `develop`).

Si un prérequis manque → le signaler et **ne pas** créer la PR.

> ⚠️ La validation `compare-report-params` (XML vs JSON) se fait **sur l'image du PR**, donc APRÈS
> création. Elle figure dans « À finaliser » et remplit la section « Validation » plus tard. Ne pas
> bloquer la création de la PR dessus.

---

## Processus

### 1. Rassembler les informations (ne rien inventer — tout dériver du réel)

**Branche & base :**
```bash
cd /c/Repos/monolith
git rev-parse --abbrev-ref HEAD        # doit être feature/RPT-...
git log develop..HEAD --oneline        # commits de la branche
git diff --stat develop...HEAD         # fichiers touchés
```

**Rapport(s) migré(s) & tickets :** déduire des commits/branche et de `.work/{slug}/` du
workspace si présent (`analysis.md`, `migration-log-*.md`). Un ticket `RPT-XXXXX` par rapport (avec l'URL
`https://croesus-support.atlassian.net/browse/RPT-XXXXX`). Noter la **PR frontend associée** si elle
existe (`croesusfin/pf-web#<num>`).

**Détail des changements** — extraire du diff, classés comme dans les références (§ gabarit) :
- **Dates** : nouvelles VPF date (`Parameters/Date/`) + méthodes `IDateTimeService` ; noter les
  divergences assumées vs le jumeau desktop (ex. fin de trimestre **calendaire sans ajustement au
  vendredi**) avec la réf. C++ (`validation_date.c:ligne`).
- **VPFs liste / POST** : nouvelles classes `*Parameter` (`Parameters/Hidden/`) enregistrées dans
  `PostParamEntryValueProviderFunctionsExecuter.cs` ; conversions listes `,` → `|` ; valeurs **vérifiées
  contre `validation_hided.c`**.
- **Paramètres migrés (`Parameters.cs`)** : joins/vues/points d'entrée FBNGP, overrides, câblage
  `ValueProviderFunction=`/`InitialValue=` (rappeler qu'**aucune `ValidationFunction` n'est modifiée**).
- **Enregistrements & config dev** : `WebRTMRunner`, `GetDisplayUnmaskedId` (si `PARAM_IgnoreIdMasking`)
  + tests, et **`croesus.sql`** (voir étape 2).

### 2. Configuration des Prefs (rapports gated par une PREF)

La plupart des rapports sont **gated par une `PREF_REPORT_<REPORT_NAME>`** : sans activation, ils ne sont
pas visibles dans Xpert sur les BD dev (firmes 1, 2, 3). Détecter et configurer **avant** de rédiger la PR.

1. **Identifier la PREF** et ses conditions secondaires : lire `B_REPORT.PREF_VALIDATION` du rapport
   (format `PREF_REPORT_<NAME>=YES[,PREF_AUTRE=NO]`) et le `ReportName` dans `RPT_<...>.cs`. Une condition
   secondaire (`,PREF_TAX_LOT=NO`) doit être satisfaite par la firm config dev, sinon le rapport ne se
   génère pas même PREF activée.
2. **Choisir le bloc `croesus.sql`** (`PM/SupportFiles/DBConfig/croesus.sql`) :
   - **Rapport d'un package** (famille partageant une PREF de package, ex. `PREF_QUARTERLY_REPORT_GP1859`)
     → **bloc dédié au package** regroupant la PREF de package **et** les `PREF_REPORT_<NAME>=YES`, avec
     son propre guard idempotent :
     ```sql
     -- Activation des PREF du package GP1859 [RPT-XXXXX]
     update B_FIRM set CONFIG_TXT = convert(varchar(16000), CONFIG_TXT) + '
     PREF_QUARTERLY_REPORT_GP1859=YES
     PREF_REPORT_FBNGP_Q_EVAL=YES
     PREF_REPORT_FBNGP_Q_TRANSACTION=YES
     '
     where FIRM_ID in (1, 2, 3)
       and CONFIG_TXT not like '%PREF_REPORT_FBNGP_Q_EVAL=YES%'
     go
     ```
   - **Rapport autonome** → ajouter la ligne `PREF_REPORT_<NAME>=YES` en **ordre alphabétique** dans le
     bloc générique `[RPT-19901]` (déléguer au skill **`activate-web-report-pref`**).
3. **Guard idempotent** : la clause `and CONFIG_TXT not like '%PREF_REPORT_<canary>=YES%'` est le canary —
   **ne jamais la modifier** sur un bloc existant ; pour un nouveau bloc, choisir un canary parmi les PREF
   du bloc.
4. **Visibilité PAD** (`B_REPORT ... VISIBLE='Y'`) = **TEST ONLY, non commité** (géré par le RTM). Ne PAS
   l'ajouter à `croesus.sql` ; l'inclure uniquement comme SQL de setup dev dans le corps de la PR (§ gabarit).

Refléter le résultat dans la sous-section « Enregistrements & config dev » de la description.

### 3. Rédiger la description (gabarit ci-dessous)

Remplir **le gabarit** avec les infos des étapes 1-2. Ne garder que les sous-sections **réellement**
concernées (p. ex. omettre « Dates » si aucune VPF date). Le contenu doit refléter le diff, pas le
gabarit littéral. La section « Validation » : cocher build + tests (prérequis faits) ; le tableau de
comparaison des paramètres XML/JSON reste **⏳ à compléter sur l'image du PR**.

### 4. Faire valider AVANT de créer

Afficher à l'utilisateur le **titre** + le **corps** rendus, et demander confirmation. Créer une PR est
une action externe : ne pas la créer sans accord explicite.

### 5. Créer la PR (draft, base `develop`)

Respecter les règles git de l'organisation (ne jamais laisser une nouvelle branche suivre une ref
protégée ; premier push explicite). Si la branche n'est pas encore poussée :
```bash
cd /c/Repos/monolith
git push -u origin "$(git rev-parse --abbrev-ref HEAD)"
```

Écrire le corps dans un fichier temporaire (évite les soucis d'échappement), puis créer en **draft** :
```bash
gh pr create -d --base develop \
  --title "feat(report): migrate <REPORT_NAME[ & REPORT_NAME]> to Xpert [RPT-XXXX][RPT-YYYY]" \
  --body-file /tmp/migration-pr-body.md
```

Afficher l'URL retournée. Rappeler que le passage en *Ready for review* (`gh pr ready <n>`) déclenche le
CI et se fait quand l'utilisateur le décide.

### 6. Après validation sur l'image (optionnel)

Une fois `compare-report-params` exécuté sur l'image du PR : **mettre à jour le corps**
(`gh pr edit <n> --body-file ...`) — remplir le tableau de comparaison des paramètres et cocher les cases
« À finaliser » correspondantes.

---

## Gabarit de description

````markdown
## Objectif

Migration backend Xpert de **<N rapport(s) / famille>** (<contexte métier — package, produit>) :
- **<REPORT_NAME>** — <Nom FR> — RPT-XXXXX : https://croesus-support.atlassian.net/browse/RPT-XXXXX
- **<REPORT_NAME>** — <Nom FR> — RPT-YYYYY : https://croesus-support.atlassian.net/browse/RPT-YYYYY

Frontend associé : **croesusfin/pf-web#<num>** <!-- si applicable -->

## Changements clés

### Dates <!-- si VPF date -->
- `IDateTimeService.<Méthode>` + `<...Parameter>` → `PARAM_<...>`. <Comportement + réf. `validation_date.c:ligne`.>
- **Pourquoi** : <divergence assumée vs jumeau desktop, ex. date calendaire sans ajustement au vendredi>.

### Nouvelle VPF <!-- si VPF liste/POST -->
- `<...Parameter>` — <rôle, présélection, valeurs vérifiées contre `validation_hided.c`, `,`→`|`>.

### Paramètres migrés (`Parameters.cs`)
- **<REPORT_NAME>** : <joins/vue/point d'entrée FBNGP, overrides, câblage `ValueProviderFunction`/`InitialValue`>. (aucune `ValidationFunction` modifiée)
- Enregistrement `<...>` (constante `Y`, POST) <!-- si applicable -->

### Enregistrements & config dev
- `WebRTMRunner` (les N rapports), `GetDisplayUnmaskedId` + tests <!-- si PARAM_IgnoreIdMasking -->
- `croesus.sql` : <bloc dédié package (`PREF_<PACKAGE>=YES` + `PREF_REPORT_<...>=YES`, guard idempotent) | ligne `PREF_REPORT_<NAME>=YES` dans le bloc [RPT-19901]>

## Validation

- ✅ Build `ReportManagerAPI.sln` (0 erreur) + `RTMTester.sln`
- ✅ <N> tests SmallTests verts (<classes de tests>)

### Comparaison paramètres Conseiller (XML) vs Xpert (JSON) <!-- ⏳ à compléter sur l'image du PR -->

Comparés pour un **client** et une **relation** → <verdict global> :

| Paramètre (point de vigilance) | Client | Relation | Verdict |
|---|---|---|---|
| `PARAM_<...>` | `<val>` | `<val>` | ✅ |

**Différences (bénignes) :**
- `PARAM_ReportTitle` : différence connue XML/JSON, indépendante de la migration.
- <`PARAM_UseRepartitionFromInvObj` : envoyé `=0` par le Conseiller en contexte Client, omis par Xpert — équivalent fonctionnel voulu. — si applicable>

#### Commandes SQL de setup dev (test)
```sql
-- Activer les PREF (désormais dans croesus.sql, bloc dédié)
update B_FIRM set CONFIG_TXT = convert(varchar(16000), CONFIG_TXT) + '
PREF_<PACKAGE>=YES
PREF_REPORT_<NAME>=YES
'
where FIRM_ID in (1, 2, 3)
  and CONFIG_TXT not like '%PREF_REPORT_<NAME>=YES%'
go

-- Rendre les rapports visibles dans le PAD (TEST ONLY, non commité — géré par le RTM)
update B_REPORT set ACCOUNT_VISIBLE='Y', CLIENT_VISIBLE='Y', LINK_VISIBLE='Y'
where REPORT_NAME in ('<NAME>')
go
```

## À finaliser
- [ ] Validation `compare-report-params` (XML Conseiller vs JSON Xpert) sur l'image du PR — écarts POST/Hidden à résoudre (sauf `PARAM_ReportTitle`, diff connue).
- [ ] Baselines E2E d'API (`update_baselines.py`) régénérées sur un backend contenant ces changements, JSONs commités.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
````

---

## Règles de fidélité

- **Tout dériver du diff/commits/tickets réels** — jamais de contenu inventé. Une sous-section sans
  changement correspondant est **retirée**, pas remplie de placeholders.
- **Ne pas prétendre** qu'une validation est faite si elle ne l'est pas : à la création, le tableau de
  comparaison XML/JSON et les baselines E2E restent **⏳/à cocher** (ils se font sur l'image du PR).
- **Prefs** : le bloc `croesus.sql` doit exister et être idempotent (guard préservé) ; la visibilité PAD
  reste hors `croesus.sql` (TEST ONLY).
- **Titre** = Conventional Commits `feat(report): …` + tickets entre crochets `[RPT-XXXX]` (deviendra le
  commit de squash — voir `git-conventions-monolith`).
- **Base = `develop`**, PR créée en **draft** (`-d`).
- Toujours **faire valider** le titre + corps avant `gh pr create`.

## Anti-patterns
1. Créer la PR sur `main`/`master` au lieu de `develop`.
2. Oublier la config Pref (`croesus.sql`) → rapport invisible en dev.
3. Committer la visibilité PAD (`B_REPORT ... VISIBLE='Y'`) — c'est TEST ONLY, géré par le RTM.
4. Modifier le guard idempotent (`... not like '%PREF_REPORT_<canary>=YES%'`) d'un bloc existant.
5. Cocher « Validation `compare-report-params` » alors qu'elle n'a pas été faite (elle se fait post-build).
6. Remplir le gabarit avec des sections vides / placeholders non résolus.
7. Modifier/mentionner une `ValidationFunction` changée (elles ne changent jamais en migration).
8. Créer la PR sans validation préalable de l'utilisateur.
9. Bare `git push` d'une nouvelle branche (utiliser `git push -u origin <branche>`).

## Références
- Formats cibles : PR monolith **#11943** (`feat(report): migrate FBNGP_Q_EVAL & FBNGP_Q_TRANSACTION …` —
  bloc Pref package + section Validation remplie) et **#12036** (checklist « À faire après build »).
- Skill `activate-web-report-pref` (activation d'une PREF dans `croesus.sql`).
- Skill `git-conventions-monolith` (branches, commits, titres, workflow draft → ready → squash).
- Skill `compare-report-params` (validation post-build, listée dans « À finaliser »).
