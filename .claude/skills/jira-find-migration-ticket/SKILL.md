---
name: jira-find-migration-ticket
description: Recherche dans Jira un ticket existant pour la migration Xpert d'un rapport, dans le projet RPT. Filtre les projets archivés. Retourne 0 ou plusieurs candidats avec leur statut. Utiliser au début de chaque commande /migrate-to-xpert-* pour savoir si un ticket existe avant de modifier ou créer.
allowed-tools: ToolSearch, mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources, mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql
---

# Skill: Jira — Find Migration Ticket

Recherche un ticket Jira existant pour la migration Xpert d'un rapport.

## Mission

Détecter si un ticket de migration actif existe déjà dans le projet `RPT` avant qu'une commande ne propose à l'utilisateur de modifier ou créer un ticket.

## Input

- **`{REPORT_NAME}`** — Nom interne du rapport (ex: `FBNFISC_BEG_EVAL`, `SUMMARY_PORT`)
- **`{NomEN}`** (optionnel) — Nom anglais (ex: `Initial Portfolio Analysis`)
- **`{NomFR}`** (optionnel) — Nom français (ex: `Analyse initiale du portefeuille`)

## Prérequis

Le serveur **MCP Atlassian** doit être connecté. Si les outils `mcp__plugin_atlassian_atlassian__*` ne sont pas disponibles via `ToolSearch`, retourner immédiatement :

```json
{
  "status": "mcp-unavailable",
  "message": "MCP Atlassian non connecté — recherche Jira ignorée."
}
```

## Étapes

### 1. Charger les outils MCP nécessaires

```
ToolSearch(query="select:mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources,mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql", max_results=2)
```

### 2. Récupérer le cloudId

```
mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources()
```

Identifier la ressource dont l'URL est `https://croesus-support.atlassian.net` et retenir son `id` (cloudId).

⚠️ Si plusieurs ressources sont retournées, prendre celle avec scope `read:jira-work`.

### 3. Construire la requête JQL

```jql
project = RPT AND (
  summary ~ "{REPORT_NAME}"
  {OR summary ~ "{NomFR}" si fourni}
  {OR summary ~ "{NomEN}" si fourni}
)
ORDER BY created DESC
```

**Toujours scoper sur `project = RPT`** pour exclure les projets archivés (REFACTREP, etc.) qui contiennent d'anciens refactorings non liés à la migration Xpert.

**Pourquoi titre-only** : la convention Xpert place le nom du rapport (interne ou EN/FR) dans le titre du ticket de migration (`Migrer vers Xpert : ...` ou `Générer le rapport ...`). Étendre la recherche à la description gonfle le payload (>50k caractères pour 20 issues) sans gain de précision pour les tickets de migration légitimes.

### 4. Exécuter la recherche

```
mcp__plugin_atlassian_atlassian__searchJiraIssuesUsingJql(
  cloudId={cloudId},
  jql={JQL construit},
  fields=["summary", "status", "issuetype"],
  maxResults=20
)
```

### 5. Filtrer et trier les résultats

Pour chaque ticket retourné :

- **Garder** : tickets dont le titre contient une référence claire à la migration Xpert / Web du rapport
- **Écarter** : tickets non pertinents (ex: bug sur l'ancien rapport Conseiller, ancien refactoring sans lien)

**Heuristiques de pertinence** (priorité décroissante) :
1. Titre contient `Migrer vers Xpert` ou `Convertir` + nom du rapport → priorité haute
2. Titre contient le nom interne du rapport et type = `Story` → priorité haute
3. Titre contient le nom EN/FR du rapport → priorité moyenne

## Output

Format JSON structuré :

```json
{
  "status": "found" | "not-found" | "mcp-unavailable",
  "cloudId": "c4424a63-8165-4fc5-b086-361ffdd81666",
  "candidates": [
    {
      "key": "RPT-20058",
      "summary": "Migrer vers Xpert : Analyse initiale du portefeuille (FBNFISC_BEG_EVAL)",
      "status": "Backlog",
      "issueType": "Story",
      "url": "https://croesus-support.atlassian.net/browse/RPT-20058",
      "relevance": "high"
    }
  ]
}
```

## Cas d'erreur

| Erreur | Action |
|--------|--------|
| MCP indisponible | Retourner `status: "mcp-unavailable"`, ne pas bloquer l'appelant |
| Aucun cloudId pour `croesus-support.atlassian.net` | Retourner `status: "mcp-unavailable"` avec message explicite |
| JQL syntax error | Logger l'erreur, retourner `status: "not-found"` |
| Permission refusée | Retourner `status: "not-found"` avec message d'erreur |

## Convention

- **Toujours** scoper sur `project = RPT` (jamais étendre à d'autres projets sans demande explicite)
- **Toujours** filtrer les projets archivés (REFACTREP, X-archives, etc.)
- **Ne jamais** modifier ou créer de ticket — c'est purement de la lecture (utiliser `jira-create-migration-ticket` / `jira-append-to-migration-ticket` pour les écritures)

## Références

- Skill complémentaire : `jira-create-migration-ticket` (création), `jira-append-to-migration-ticket` (mise à jour)
- Instance Atlassian : `https://croesus-support.atlassian.net`
- Convention CLAUDE.md : projet RPT, type Story pour la migration
