---
name: jira-create-migration-ticket
description: 'Crée une nouvelle Story Jira dans le projet RPT pour suivre la migration Xpert d''un rapport. Titre standardisé "Migrer vers Xpert : {NomFR} ({REPORT_NAME})", format markdown, footer de traçabilité automatique. Demande TOUJOURS confirmation utilisateur avant création.'
allowed-tools: ToolSearch, mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources, mcp__plugin_atlassian_atlassian__createJiraIssue
---

# Skill: Jira — Create Migration Ticket

Crée une Story Jira standardisée pour la migration Xpert d'un rapport dans le projet `RPT`.

## Mission

Créer un ticket de suivi de migration avec une description structurée, après confirmation explicite de l'utilisateur.

## Input

- **`{REPORT_NAME}`** — Nom interne du rapport (ex: `FBNFISC_BEG_EVAL`)
- **`{NomFR}`** — Nom français (ex: `Analyse initiale du portefeuille`)
- **`{description_markdown}`** — Description complète au format markdown (synthèse de l'analyse — voir conventions ci-dessous)

## Prérequis

- Le serveur **MCP Atlassian** doit être connecté
- Le skill appelant **DOIT** avoir préalablement obtenu la confirmation explicite de l'utilisateur. Ne JAMAIS créer un ticket sans cette confirmation (créer un ticket Jira est une action visible et engageante).

## Étapes

### 1. Charger les outils MCP nécessaires

```
ToolSearch(query="select:mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources,mcp__plugin_atlassian_atlassian__createJiraIssue", max_results=2)
```

### 2. Récupérer le cloudId

```
mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources()
```

Retenir l'`id` de la ressource `https://croesus-support.atlassian.net` (scope `write:jira-work` requis).

### 3. Construire le titre

Format **strict** :
```
Migrer vers Xpert : {NomFR} ({REPORT_NAME})
```

Exemples :
- `Migrer vers Xpert : Analyse initiale du portefeuille (FBNFISC_BEG_EVAL)`
- `Migrer vers Xpert : Sommaire du portefeuille (SUMMARY_PORT)`

### 4. Compléter la description

Ajouter le footer de traçabilité **à la fin** de `{description_markdown}` :

```markdown
{description_markdown}

---

*Description générée par `/migrate-to-xpert-analysis {REPORT_NAME}` — dernière mise à jour : {YYYY-MM-DD}.*
```

Date au format ISO `YYYY-MM-DD` (jour de création).

⚠️ **Format strict** : utiliser exactement `Description générée par /migrate-to-xpert-...` — c'est ce pattern qui permet à `jira-append-to-migration-ticket` de détecter une description auto-générée et de basculer en mode REPLACE plutôt qu'APPEND.

### 5. Créer la Story

```
mcp__plugin_atlassian_atlassian__createJiraIssue(
  cloudId={cloudId},
  projectKey="RPT",
  issueTypeName="Story",
  summary={titre construit},
  description={description avec footer},
  contentFormat="markdown"
)
```

### 6. Vérifier la création

Confirmer que le ticket retourné a :
- Un `key` au format `RPT-XXXXX`
- `issuetype.name == "Story"`
- `project.key == "RPT"`
- `status` = `Backlog` (statut initial par défaut du projet RPT)

## Output

Format JSON :

```json
{
  "status": "created" | "error",
  "ticket": {
    "key": "RPT-20058",
    "summary": "Migrer vers Xpert : Analyse initiale du portefeuille (FBNFISC_BEG_EVAL)",
    "status": "Backlog",
    "url": "https://croesus-support.atlassian.net/browse/RPT-20058"
  },
  "error": null | "{message}"
}
```

## Conventions de description (à respecter par l'appelant)

La `{description_markdown}` doit contenir, dans cet ordre :

1. **## Description utilisateur (spec fonctionnelle)** *(OBLIGATOIRE EN TÊTE)* — vue produit du rapport (à quoi il sert, contexte d'utilisation, ce que l'utilisateur voit, options de configuration humanisées, comportements interactifs en langage naturel, prefs admin). Pas de `PARAM_*` techniques, pas de noms de classes C#.
2. `---` (séparateur visuel) avant la partie technique
3. **## Objectif** — 1-2 phrases sur ce que fait le rapport et son contexte
4. **## Identité du rapport** — tableau (Template ID, Nom interne, Nom EN/FR, Classe C#, Template, Sub-reports, Activation prefs)
5. **## Effort de migration backend** — compteurs VPF (Catégories A/B/C/D) avec descriptions courtes ; les noms des nouvelles classes Cat C apparaissent dans le compteur, sans pseudo-code
6. **## Estimation suggérée pour affinage (backend)** — pointage 5/8/13 + compteurs détectés + drapeaux levés + règle appliquée + scénarios d'escalade. Toujours afficher la formule d'audit
7. **## Comportements UI à migrer** — liste numérotée des patterns Observer actifs
8. **## Préférences impliquées** — Activation / Runtime / UI logic
9. **## Critères d'acceptation** — checklist
10. **## Limites connues** — éléments à investiguer
11. **## Documents de référence** — liens vers analyse markdown/PDF, page Confluence, sources C++/C#

⚠️ **Sections explicitement EXCLUES de la description Jira** (gardées dans le markdown complet `.work/{slug}/analysis.md` mais pas poussées ici) :
- `## Nouvelles classes à créer (Catégorie C)` — détails techniques pseudo-code/dépendances réservés au markdown
- `## Travail à faire` — checklist Backend/Frontend/Validation, redondante avec les critères d'acceptation

⚠️ **Conventions Jira markdown** :
- Les checkboxes `- [ ]` sont rendues comme bullets (pas cochables) — c'est attendu
- Pas de bloc HTML brut
- Le pipe `|` dans les valeurs `InitialValue` n'a pas besoin d'être échappé en Markdown (il l'est dans les tableaux uniquement)

## Cas d'erreur

| Erreur | Action |
|--------|--------|
| MCP indisponible | Retourner `status: "error"` avec message `MCP Atlassian non disponible` |
| Confirmation utilisateur absente | **Refuser de créer**. Rappel : ce skill suppose que l'appelant a déjà obtenu confirmation |
| Permission refusée (write:jira-work) | Retourner l'erreur, ne pas réessayer |
| projectKey RPT introuvable | Retourner l'erreur, suggérer de vérifier l'accès au projet |

## Convention

- **Toujours** projet `RPT`, type `Story`
- **Toujours** format markdown (pas ADF, pas HTML)
- **Toujours** ajouter le footer de traçabilité
- **Ne jamais** assigner automatiquement le ticket (laisser non assigné par défaut)
- **Ne jamais** ajouter de labels, story points, ou epic parent sans demande explicite

## Références

- Skill complémentaire : `jira-find-migration-ticket` (recherche), `jira-append-to-migration-ticket` (mise à jour)
- Instance Atlassian : `https://croesus-support.atlassian.net`
- Projet RPT : DevOps, REPORTS
