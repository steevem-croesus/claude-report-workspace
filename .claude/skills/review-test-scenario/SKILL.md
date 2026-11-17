---
name: review-test-scenario
description: Revoit un cas de test QA (scénario CSV/tableau + ticket Jira de test) en le confrontant au code source du monolith, puis produit un document de revue, un scénario corrigé et une mise à jour du ticket Jira. Utiliser quand l'utilisateur demande de « réviser / peaufiner / valider / corriger » des cas de test, des préconditions ou un scénario de test, quand il fournit un CSV de cas de test avec un ticket RPT-/CAR-/MROX-, ou quand il demande si une précondition de test est réalisable. Détecte les attendus impossibles, les préconditions non produisibles par l'application, les étapes qui cliquent un contrôle non affiché, et les noms de champs inexistants.
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, ToolSearch, mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources, mcp__plugin_atlassian_atlassian__getJiraIssue, mcp__plugin_atlassian_atlassian__editJiraIssue, mcp__plugin_atlassian_atlassian__addCommentToJiraIssue, mcp__claude_ai_Atlassian__getAccessibleAtlassianResources, mcp__claude_ai_Atlassian__getJiraIssue, mcp__claude_ai_Atlassian__editJiraIssue, mcp__claude_ai_Atlassian__addCommentToJiraIssue
---

# Skill: Revue d'un cas de test contre le code source

## Mission

Un cas de test QA est écrit à partir d'un énoncé fonctionnel, pas du code livré. Il contient donc
régulièrement des attendus que le code ne peut pas produire, des préconditions que l'application ne sait
pas créer, et des étapes qui manipulent un contrôle absent de l'écran. Ce skill confronte le scénario au
code du monolith, corrige ce qui est factuellement faux, et remonte à l'analyste ce qui relève d'une
décision fonctionnelle.

**Ce skill ne rend pas un verdict « le test passe / échoue ».** Il rend un scénario exécutable et
cohérent avec le code livré, plus la liste des écarts entre l'énoncé du ticket et le comportement
implémenté.

## Input

- **`{ticketKey}`** — ticket Jira du cas de test (ex. `RPT-21343`). Optionnel si un scénario est fourni.
- **`{scenarioPath}`** — chemin du scénario (CSV, Markdown, texte). Optionnel si le ticket le contient.
- **`{featureHint}`** *(optionnel)* — indice de domaine (« configuration des rapports », « blotter RQS »…)
  ou chemin d'un fichier source déjà identifié par l'utilisateur.
- **`{mode}`** *(optionnel)* — `fichiers` | `jira` | `les deux`. Détermine si le ticket Jira est mis à
  jour directement. Défaut : `les deux`. Demander si `{ticketKey}` est fourni sans mode.

Au moins un de `{ticketKey}` / `{scenarioPath}` est requis. Si les deux manquent, demander lequel fournir
plutôt que de deviner.

## Prérequis

- Le checkout **monolith** doit être accessible : `C:\Repos\monolith` ou via les symlinks `repos/` du
  workspace. La revue porte sur le code **de la branche courante** — relever le SHA et la branche au
  début et les inscrire dans le document produit, sinon la revue n'est pas reproductible.
- Serveur **MCP Atlassian** connecté si `{ticketKey}` est fourni.
- Langue de sortie : **français** (les cas de test et les tickets QA sont en français).

## Sorties

| Sortie | Contenu | Mode |
|---|---|---|
| `<ticket>-revue.md` | document de revue : règles implémentées, écarts relevés, préconditions révisées, scénario révisé, annexes | toujours |
| `<ticket>-revise.csv` | scénario corrigé pour lecture humaine, mêmes colonnes que l'entrée | toujours |
| `<ticket>-xray-import.csv` | même scénario au format **Test Case Importer** d'Xray, prêt à importer | ticket de type Test (Xray) |
| **Ticket Jira mis à jour** | description réécrite (objectif, préconditions, données, précautions) + section « Écarts à valider », **après confirmation explicite** | `jira`, `les deux` |

Déposer les fichiers **à côté du scénario d'entrée**. **Ne jamais écraser le scénario d'origine** : il
est la trace de ce qui a été demandé.

Limite connue sur les tickets de type **Test (Xray)** : les pas de test ne sont pas un champ Jira et ne
sont donc **pas** modifiables par le MCP. Seule la description l'est — d'où le CSV d'import, que
l'utilisateur charge lui-même. Format et pièges : [`format-xray-csv.md`](format-xray-csv.md) ;
procédure Jira : [`maj-jira.md`](maj-jira.md).

## Étapes

### 1. Cadrer

Relever la branche et le SHA du monolith (`git -C C:/Repos/monolith rev-parse --short HEAD` et
`--abbrev-ref HEAD`). Lire le scénario fourni et, s'il y a lieu, le ticket Jira (objectif, préconditions,
données, étapes). Si les étapes vivent dans un champ d'un plugin de gestion de tests (Xray, Zephyr) non
exposé par le MCP, le dire : la mise à jour se fera par la description ou un commentaire, et le CSV
servira à la ré-importation manuelle.

Ne pas traiter la formulation du ticket comme une autorité : c'est précisément l'objet de la revue.

### 2. S'orienter dans le code avant de chercher

Identifier le produit/sous-système concerné via la chaîne CLAUDE.md et `doc/references/*/README.md`, puis
**restreindre toutes les recherches à ce dossier et à ses dépendances directes** (discipline monorepo).
Ne pas lancer de recherche à la racine du dépôt.

Point d'entrée habituel : le contrôleur de l'écran → le service → le repository → le scénario flex /
la requête. Lire les commentaires : dans ce dépôt ils citent souvent la fonction C++ d'origine, ce qui
donne la règle métier de référence.

### 3. Extraire les règles réellement implémentées

Produire un tableau « règles implémentées », **une ligne par règle, chacune avec sa référence
`fichier:ligne`**. Une règle sans référence de code ne va pas dans le tableau.

Couvrir au minimum :

- la **barrière d'accès** à la fonctionnalité (préférences `PREF_*`, feature flags `FF_*`) ;
- ce qui **alimente la liste** (scénario flex / requête) : un élément absent de la liste ne peut pas être
  grisé, il est invisible — distinction cruciale pour les attendus ;
- les **filtres d'exclusion** (colonnes de visibilité, conditions de préférence, flags par rapport) ;
- les **drapeaux d'action** et leurs **dérivations** (`canDelete` dérivé de `canEdit`, etc.) ;
- l'**application côté serveur** des mêmes règles sur les mutations (un bouton grisé doit correspondre à
  un 403).

### 4. Construire la table de correspondance des noms

Pour chaque champ cité par le cas de test, établir le nom dans **chaque couche** : libellé d'interface,
colonne BD, champ logique PM, propriété ORM/implementer, champ d'API. Un cas de test qui cite un nom
d'une couche à laquelle le testeur n'a pas accès est inexploitable.

Les implementers (`CFF/Products/FinancialFramework/**/*Implementer.cs`, attribut `FIELDNAME`) sont la
source de vérité propriété ORM → colonne BD. Les champs logiques PM se trouvent par
`sp_create_field` dans `PM/SupportFiles/MigrationScripts/`.

### 5. Passer le scénario aux quatre tests de la checklist

Appliquer [`checklist-revue.md`](checklist-revue.md) — produisibilité, atteignabilité, exclusivité
mutuelle, hygiène d'exécution. C'est le cœur du skill ; ne pas l'abréger.

Consulter [`pieges-connus.md`](pieges-connus.md) : catalogue des pièges déjà rencontrés, avec les
références de code. Vérifier que le piège s'applique toujours dans la version courante avant de
l'invoquer — ces notes vieillissent.

### 6. Rédiger le document de revue

Suivre [`modele-revue.md`](modele-revue.md). Règle de rédaction : **chaque correction est justifiée par
une référence de code**, et chaque écart avec l'énoncé du ticket apparaît dans la section « à remonter à
l'analyste ».

### 7. Rédiger le scénario révisé

Mêmes colonnes que l'entrée, un fichier `<ticket>-revise.csv`. Chaque étape doit être exécutable par un
testeur qui n'a pas lu le code : données nommées par des références stables (`CFG-SUCC-A`…), attendus
observables à l'écran, restaurations incluses.

Si le ticket est de type **Test (Xray)**, produire en plus `<ticket>-xray-import.csv` et **valider sa
structure** avant livraison — format, contraintes d'encodage et vérification :
[`format-xray-csv.md`](format-xray-csv.md).

### 8. Mettre à jour le ticket Jira (modes `jira` et `les deux`)

Suivre [`maj-jira.md`](maj-jira.md) : champs réellement modifiables, composition de la description,
idempotence du bloc généré, vérification du rendu, repli en commentaire.

Trois règles non négociables :

- **confirmation explicite avant toute écriture**, en montrant le contenu exact ;
- **préserver le contenu humain** : on remplace l'objectif, les préconditions et les données, rien
  d'autre ;
- **signer le bloc généré** (`Revue générée par /review-test-scenario — <branche>@<sha> — <date>`) pour
  qu'une passe ultérieure le remplace au lieu de l'empiler.

En mode `fichiers`, sauter cette étape et le dire dans la restitution.

### 9. Restituer

Dans la réponse : les corrections majeures (une ligne chacune, avec la référence de code), les écarts à
remonter, les questions restées ouvertes, et — si le ticket a été mis à jour — son URL ainsi que **ce
qui reste à faire à la main** (ré-importation Xray du CSV). Pas de paraphrase du document.

## Garde-fous

- **Ne jamais écraser** le scénario d'origine ni la description Jira sans confirmation.
- **Ne jamais aligner silencieusement** un attendu sur le code : si le code contredit l'énoncé du ticket,
  corriger le scénario **et** inscrire l'écart dans « à remonter à l'analyste ». Le code peut être le
  défaut.
- **Ne pas inventer de donnée de test** : si l'état requis n'est pas produisible par l'application, le
  dire, fournir le SQL de forgeage **étiqueté comme artificiel**, et proposer de couvrir la règle
  autrement.
- **Ne pas supposer qu'un contrôle est affiché** parce que l'API retourne la donnée : vérifier le gate
  d'affichage (liste des groupes/onglets/menus), qui est souvent plus restrictif.
- **Ne pas conclure sur le frontend** depuis le seul code backend : si le comportement d'affichage n'est
  pas vérifiable dans le code disponible, poser la question plutôt que de trancher.
- Vérifier chaque référence `fichier:ligne` avant de l'écrire : les lignes bougent.
