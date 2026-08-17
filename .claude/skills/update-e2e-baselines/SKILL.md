---
name: update-e2e-baselines
description: Met à jour les baselines des tests E2E d'APIs après l'ajout d'un nouveau rapport dans WebRTMRunner. Rouler update_baselines.py et pousser les JSONs mis à jour.
---

# Skill: Update E2E Baselines

Met à jour les baselines des tests E2E d'APIs du monolith après l'ajout d'un nouveau rapport.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Quand utiliser

**Cas nominal (proactif, avant `git push`)** — dès qu'on ajoute ou modifie un rapport qui touche `WebRTMRunner.cs`, les baselines doivent être mises à jour **avant** de pousser la PR pour éviter un CI rouge.

**Cas fallback (réactif)** — si la PR a déjà été poussée et que le CI E2E échoue sur des diffs de baseline, on peut rattraper à partir de l'image Docker du job CI.

**IMPORTANT :** Le script nécessite un backend déployé avec les changements du rapport (sinon l'API ne retourne pas le nouveau rapport et les baselines ne changent pas).

## Cas nominal — Déploiement local + RTMLauncher (avant push)

1. **Build local du ReportManagerApi** avec les derniers changements du rapport
2. **Configurer Monolith Dev Helper** (onglet .Net) :
   - Path ReportManagerApi : `{Path du repo}/src/ReportManagerAPI/bin/debug/net{XXX}`
   - Cocher **Deploy** pour ReportManagerApi
3. **Ouvrir le port nécessaire** : Port 8999 (FrameworkServer) — cocher "Open Port"
4. **Lancer le container** via Monolith Dev Helper
5. **Rouler RTMLauncher** pour appliquer les modifications RTM à la base de données (sans ça, les nouveaux paramètres du rapport ne seront pas dans `B_REPORT_META_DATA` et le script retournera des valeurs obsolètes)
6. Demander à l'utilisateur de confirmer que le container tourne et que RTM est terminé, puis passer à l'étape "Rouler le script"

## Cas fallback (après CI rouge)

Si la PR a déjà été poussée et que le CI E2E échoue, deux options selon la disponibilité d'une image qui contient déjà les modifs.

### Option 1 — Image Docker de la PR (si disponible)

L'image Docker produite par le job CI **de la PR elle-même** contient déjà toutes les modifs du rapport (code + migrations RTM appliquées lors du build de l'image) :

1. Récupérer l'image depuis le job CI de la PR (étape "Assemble Image / ghcr to ecr")
2. Lancer l'image localement
3. Passer à l'étape "Rouler le script" — **pas besoin de RTMLauncher ni de redéployer ReportManagerApi**, l'image contient déjà tout

### Option 2 — Image Docker quelconque + overlay ReportManagerApi local + RTM local

Si l'image de la PR n'est pas encore prête (CI en cours, ou on veut itérer sans attendre un rebuild), on peut partir de n'importe quelle image Docker fonctionnelle (ex: dernière image de `develop`, image d'une autre PR récente) et y greffer les modifs localement :

1. **Build local du ReportManagerApi** avec les modifs de la branche (`dotnet build` de la solution)
2. **Récupérer une image Docker de base** — peu importe laquelle, tant qu'elle démarre correctement (ex: dernière image `develop` ou image d'une PR voisine)
3. **Configurer Monolith Dev Helper** pour overlay le ReportManagerApi local par-dessus l'image :
   - Onglet .Net → Path ReportManagerApi : `{Path du repo}/src/ReportManagerAPI/bin/debug/net{XXX}`
   - Cocher **Deploy** pour ReportManagerApi (le binaire local écrase celui de l'image au démarrage)
4. **Ouvrir le port nécessaire** : Port 8999 (FrameworkServer) uniquement
5. **Lancer le container** — le framework + la base viennent de l'image, le ReportManagerApi vient du build local
6. **Rouler RTMLauncher localement** pour appliquer les modifs RTM du nouveau rapport dans la base de l'image (sans ça, `B_REPORT_META_DATA` contient l'état de l'image de base, pas les nouveaux paramètres)
7. Demander à l'utilisateur de confirmer que le container tourne et que RTM est terminé, puis passer à l'étape "Rouler le script"

**Quand choisir Option 2 plutôt qu'Option 1 :** image de la PR pas encore prête, ou besoin d'itérer rapidement sans pusher + attendre un rebuild CI à chaque ajustement.

**Référence Confluence** : [Débuggage avec Docker — Report Manager API](https://croesus-support.atlassian.net/wiki/spaces/DEV/pages/556400661/D+buggage+avec+Docker#Report-Manager-API)

## Prérequis Python

- Python 3.12+ installé
- Installer les dépendances (la première fois) :
```bash
cd C:/Git projects/monolith/monolith/CFF/E2ETests
pip install -r requirements.txt
```

## Rouler le script

### Sur Windows (⚠️ encoding)

Le script utilise des caractères Unicode (✓/✗) qui crashent avec `UnicodeEncodeError` sur Windows par défaut. Forcer UTF-8 :

```bash
cd C:/Git projects/monolith/monolith/CFF/E2ETests
PYTHONIOENCODING=utf-8 PYTHONPATH=. python e2e/Report/v1/Helpers/update_baselines.py
```

### Sur Linux/Mac

```bash
cd /path/to/monolith/CFF/E2ETests
PYTHONPATH=. python e2e/Report/v1/Helpers/update_baselines.py
```

Le script met à jour :
- `e2e/Report/v1/Baselines/Reports/AccountTemplates.json`
- `e2e/Report/v1/Baselines/Reports/ClientTemplates.json`
- `e2e/Report/v1/Baselines/Reports/RelationTemplates.json`
- `e2e/Report/v1/Baselines/Reports/SecurityTemplates.json`
- Plus les fixtures de paramètres dans `Client/Parameters/`

## Vérifier les changements

```bash
cd C:/Git projects/monolith/monolith
git diff --stat CFF/E2ETests/
```

**Vérifier visuellement** que :
- Le nouveau rapport apparaît avec le bon `ReportTemplateId` et `InternalReportName`
- Si rapport exclusif (`header.ValidationFunction = "SingleSelect"`), `ValidationRules.SelectionAttribute` doit être présent
- Les autres rapports ne sont pas impactés involontairement

## Rouler pytest pour valider

Avant de commiter, vérifier que les tests qui échouaient passent maintenant :

```bash
cd C:/Git projects/monolith/monolith/CFF/E2ETests
PYTHONIOENCODING=utf-8 PYTHONPATH=. python -m pytest e2e/Report/v1/Reports/test_get_reports.py -v
```

**Distinguer les échecs liés à nos changements vs environnement local** :
- Si `test_get_report_templates_*` échouent → c'est ce qu'on corrige avec `update_baselines.py`
- Si d'autres tests échouent (ex: `test_post_report_for_client` avec HTTP 500) → probablement un problème d'environnement local (stockage, services gRPC non démarrés). Comparer avec le CI — s'ils passent en CI, ignorer localement.

## Commit et push

Respecter Conventional Commits (voir skill `git-conventions-monolith`) :

```bash
git add CFF/E2ETests/e2e/Report/v1/Baselines/Reports/*.json
git commit -m "test: update E2E baselines for XXX_REPORT_NAME"
git push
```

Exemple concret : `test: update E2E baselines with ValidationRules for IAVM_ASSET_MIX`

## Si le développeur ne peut pas rouler le script

Si ni l'image CI ni le déploiement local ne sont disponibles, demander au développeur de :
1. Rouler `python e2e/Report/v1/Helpers/update_baselines.py` sur son environnement
2. Fournir les JSONs mis à jour
3. Ou attendre que la CI de la PR échoue et récupérer les valeurs attendues des logs d'erreur

## Référence

- Documentation complète : [CFF/E2ETests/README.md](https://github.com/croesusfin/monolith/blob/develop/CFF/E2ETests/README.md#mise-a-jour-des-baselines-de-tests-dapis)
- Confluence Docker setup : [Débuggage avec Docker](https://croesus-support.atlassian.net/wiki/spaces/DEV/pages/556400661/)
