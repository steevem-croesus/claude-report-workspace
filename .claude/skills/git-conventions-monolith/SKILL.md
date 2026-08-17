---
name: git-conventions-monolith
description: Conventions git du monolith Croesus — branches, commits conventionnels, titres de PR. Utiliser lors de la création de branches, commits et PR pour respecter le CI (commitlint) et les standards du repo.
---

# Skill: Git Conventions Monolith

Conventions à respecter pour que les commits, branches et PR passent le CI du monolith.

**Pour les conventions du repo `pf-web` (frontend Xpert), utiliser le skill `git-conventions-pf-web` à la place** — il a des règles différentes (notamment une limite stricte de 38 caractères sur les noms de branches).

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Noms de branches

Format : `feature/<jira-id-short-desc>` ou `fix/<jira-id-short-desc>`

Exemples :
- `feature/RPT-19707` — migration rapport RPT-19707
- `feature/RPT-19707-skills` — skills liés à RPT-19707
- `fix/RPT-18234` — bug fix pour ticket RPT-18234
- `fix/MROX-4358-comptes-sous-jacents` — fix avec description

**Règles :**
- Lowercase pour les préfixes (`feature`, `fix`, `hotfix`) — le CI (`.github/workflows/check-branch-naming.yml` du monolith) vérifie uniquement ce préfixe
- Tirets pour séparer les mots dans la description

## Messages de commit — Conventional Commits 1.0.0

Référence : https://www.conventionalcommits.org/en/v1.0.0/

**Format :** `<type>[(<scope>)]: <description>`

**Types utilisés dans le monolith :**
| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `refactor` | Refactoring sans changement de comportement |
| `docs` | Documentation seulement |
| `test` | Ajout/modification de tests |
| `chore` | Maintenance (build, CI, dépendances) |

**Scope optionnel** : généralement le Jira ID — `feat(RPT-18641): ...`

**Exemples réels du monolith :**
```
feat(RPT-18641): Configure Flex Object for Criteria BO and add GlobalParameters
feat: MROX-4358 Comptes sous-jacents pour les ordres en bloc
fix: Convertir le IA Code en upper case pour que l'utilisateur n'ait pas d'erreur
fix: corriger une régression en incluant accountId dans la sérialisation
refactor: address code review feedback from Loic
docs: improve comments on accepted gaps in Parameters.cs
test: update E2E baselines with ValidationRules for IAVM_ASSET_MIX
```

**CI valide les messages de commit via commitlint** (`.github/workflows/commitlint.yml`). Un commit non conforme fera échouer le CI.

**Règles :**
- Lowercase pour le type (`feat:` pas `Feat:`)
- Pas de point final dans la description
- Description en anglais ou français (les deux sont acceptés dans le repo)
- Body optionnel après une ligne vide, pour plus de détails

## Titres de pull request

Le **titre de la PR** devient le message de commit final quand on fait `Squash and merge` (méthode standard du monolith). Il DOIT donc respecter Conventional Commits.

**Format recommandé :** `<type>: <description> (#<PR_number>)`

Le numéro de PR est ajouté automatiquement par GitHub lors du merge squash.

**Exemples :**
```
feat: migrate IAVM_ASSET_MIX (Asset Allocation Summary) to Xpert backend
fix: correct PARAM_IsCliRootManagement and PARAM_AssetMixRepartType defaults
refactor: address code review feedback from Loic
```

## Workflow de création de PR

1. **Créer la branche** :
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/RPT-<ticket>
   git push -u origin feature/RPT-<ticket>
   ```

2. **Créer la PR en draft** :
   ```bash
   gh pr create -d --base develop --title "feat: <description>" --body "..."
   ```

3. **Quand prêt, marquer Ready for review** :
   ```bash
   gh pr ready <pr_number>
   ```
   Les validations CI s'enclenchent seulement en mode Ready (pas en draft).

4. **Merge avec squash** (après review+approval) :
   ```bash
   gh pr merge -s -t "<conventional commit title>" -d
   ```
   `-d` supprime la branche après le merge.

## Anti-patterns à éviter

**Noms de branches :**
- ❌ `Feature/RPT-19707` (préfixe en majuscules — le CI rejette)
- ❌ `my-fix` (pas de préfixe, pas de ticket)
- ❌ `rpt19707` (manque le tiret)

**Commits :**
- ❌ `Fix the bug` (pas de type conventionnel)
- ❌ `FEAT: new feature` (majuscules dans le type)
- ❌ `feat: ` (description vide)
- ❌ `feat: added new feature.` (passé + point final)

**Titres de PR :**
- ❌ `Update code` (pas de type)
- ❌ `WIP: ...` (utiliser draft mode à la place)

## Checklist avant de pousser

- [ ] Nom de branche respecte `<type>/<jira-id-desc>` (préfixe en minuscules ; casse du Jira ID au choix)
- [ ] Chaque commit a un type conventionnel (`feat:`, `fix:`, etc.)
- [ ] Titre de la PR respecte Conventional Commits (deviendra le commit de merge)
- [ ] Co-authored footer si applicable : `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`

## Références

- [CONTRIBUTING.md du monolith](https://github.com/croesusfin/monolith/blob/develop/CONTRIBUTING.md)
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
- Workflow commitlint : `.github/workflows/commitlint.yml`
