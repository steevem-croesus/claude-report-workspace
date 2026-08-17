---
name: git-conventions-pf-web
description: Conventions git du repo pf-web (Xpert Angular monorepo) — limite stricte sur la longueur des branches, conventional commits, titres de PR. Utiliser lors de la création de branches, commits et PR sur pf-web pour passer le CI (PR Validator + commitlint).
---

# Skill: Git Conventions pf-web

Conventions à respecter pour que les branches, commits et PR passent le CI du repo `pf-web` (Croesus Xpert).

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Noms de branches — limite stricte 38 caractères

**Règle critique** : le nom complet de la branche **doit faire moins de 38 caractères**, préfixe inclus.

Cette limite est imposée par l'action `croesusfin/pr-validator@v1` (workflow `.github/workflows/pr-validator.yaml`). Au-delà, la PR Validator échoue avec :

> Branch name is too long. It should be less than 38 characters. Otherwise the release label on the pr will fail.

**Format :** `<type>/<jira-id>-<short-desc>`

**Exemples valides :**
- `feature/rpt-20003-perf-fees` — 27 chars ✓
- `fix/rpt-19707-asset-mix` — 23 chars ✓
- `feature/rpt-19537-money-weighted` — 32 chars ✓
- `fix/sup-22361-fees-validation` — 29 chars ✓

**Exemples invalides :**
- ❌ `feature/rpt-20003-performance-fees-validation` — 44 chars (trop long)
- ❌ `feature/RPT-20003-money-weighted-net-of-fees-validation` — 56 chars

**Conseils pour rester court :**
- Préfixe : `feature/` (8 chars), `fix/` (4 chars), `hotfix/` (7 chars), `chore/` (6 chars)
- Jira ID : `rpt-20003` ou `RPT-20003` (le casse est libre, juste cohérent)
- Description : 2-4 mots max, abréger si nécessaire (`perf-fees` au lieu de `performance-fees-validation`)

**Si la branche est déjà créée et trop longue :**

```bash
# Renommer en local
git branch -m feature/rpt-20003-perf-fees

# Pousser la nouvelle branche
git push -u origin feature/rpt-20003-perf-fees

# GitHub n'autorise pas de changer le head ref d'une PR existante :
# il faut FERMER l'ancienne PR et en créer une nouvelle.

# Sauvegarder le body de l'ancienne PR :
gh pr view <old-pr-num> --json body --jq .body > /tmp/pr-body.md

# Fermer l'ancienne PR :
gh pr close <old-pr-num> --comment "Closed in favor of new PR from shorter branch name."

# Recréer la PR depuis la nouvelle branche :
gh pr create --title "<même titre>" --body-file /tmp/pr-body.md

# Supprimer l'ancienne branche distante :
git push origin --delete <old-branch-name>
```

## Messages de commit — Conventional Commits 1.0.0

Validés par commitlint via la PR Validator (`croesusfin/pr-validator@v1`) qui lit `.commitlintrc.js` du repo.

**Format :** `<type>[(<scope>)]: <description>`

**Types acceptés :**
| Type | Usage |
|------|-------|
| `feat` | Nouvelle fonctionnalité |
| `fix` | Correction de bug |
| `refactor` | Refactoring sans changement de comportement |
| `docs` | Documentation seulement |
| `test` | Ajout/modification de tests |
| `chore` | Maintenance (build, CI, dépendances) |
| `style` | Formatage, lint (pas de logique) |
| `perf` | Amélioration de performance |

**Scope** : généralement le domaine ou le rapport (`report`, `account`, `crm`).

**Exemples réels :**
```
fix(report): RPT-20003 - Disable Money-Weighted when no Time-Weighted is selected
feat(report): RPT-19707 - Migrate IAVM Asset Mix radio button
fix(rebalancing): Changer étape d'une validation d'un rééquilibrage déjà complété
docs: improve performance-base.spec setup
```

**Règles :**
- Lowercase pour le type (`fix:` pas `Fix:`)
- Pas de point final dans la description
- Description en anglais ou français (les deux sont acceptés)
- Body optionnel après une ligne vide pour plus de détails

## Titres de pull request

Le **titre de la PR** devient le commit final lors du `Squash and merge` (méthode standard du repo). Il DOIT donc respecter Conventional Commits.

**Format recommandé :** `<type>(<scope>): <description>`

GitHub ajoute automatiquement le numéro de PR (`(#1914)`) lors du squash merge.

**Exemples :**
```
fix(report): RPT-20003 - Disable Money-Weighted when no Time-Weighted is selected
feat(report): migrate Performance Asset Class to Xpert
refactor(report): consolidate fees validation logic
```

## Workflow de création de PR

1. **Créer la branche depuis main** (pf-web utilise `main` comme branche par défaut, pas `develop`) :
   ```bash
   git checkout main
   git pull
   git checkout -b feature/rpt-<id>-<short-desc>
   git push -u origin feature/rpt-<id>-<short-desc>
   ```

2. **Vérifier la longueur AVANT de pousser** :
   ```bash
   git branch --show-current | tr -d '\n' | wc -c
   # Doit retourner < 38
   ```

3. **Créer la PR** :
   ```bash
   gh pr create --base main --title "<conventional commit>" --body "..."
   ```

4. **Merge avec squash** (après review+approval) :
   ```bash
   gh pr merge -s -t "<conventional commit title>" -d
   ```

## Anti-patterns à éviter

**Noms de branches :**
- ❌ `feature/rpt-20003-performance-fees-validation` (44 chars > 38)
- ❌ `Feature/RPT-19707` (préfixe en majuscules)
- ❌ `my-fix` (pas de préfixe, pas de ticket)

**Commits :**
- ❌ `Fix the bug` (pas de type conventionnel)
- ❌ `FIX: bug` (majuscules dans le type)
- ❌ `feat: ` (description vide)

**Titres de PR :**
- ❌ `Update code` (pas de type)
- ❌ `WIP: ...` (utiliser draft mode à la place)

## Checklist avant de pousser

- [ ] Nom de branche : `<type>/<jira-id>-<short-desc>` **et < 38 chars**
- [ ] Préfixes en minuscules (`feature`, `fix`, `chore`, etc.)
- [ ] Chaque commit a un type conventionnel (`feat:`, `fix:`, etc.)
- [ ] Titre de la PR respecte Conventional Commits (deviendra le commit de merge)
- [ ] Co-authored footer si applicable

## Différences vs git-conventions-monolith

| Aspect | monolith | pf-web |
|---|---|---|
| Branche par défaut | `develop` (Gitflow) | `main` (trunk-based) |
| Validateur CI | commitlint workflow | `croesusfin/pr-validator@v1` |
| Limite longueur branche | aucune documentée | **< 38 chars** |
| Modèle de release | `release/X.Y.0` | release labels sur PR |

## Références

- Workflow PR Validator : `.github/workflows/pr-validator.yaml`
- Action externe : `croesusfin/pr-validator@v1`
- Config commitlint : `.commitlintrc.js`
- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
