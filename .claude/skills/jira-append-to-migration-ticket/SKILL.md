---
name: jira-append-to-migration-ticket
description: Met à jour la description d'un ticket Jira de migration. Si la description est auto-générée (footer "Description générée par /migrate-to-xpert-*"), elle est REMPLACÉE entièrement par la nouvelle version. Sinon, ajoute une section à la suite SANS effacer le contenu humain existant. Utiliser pour empiler les artefacts produits par les commandes /migrate-to-xpert-* dans le même ticket.
allowed-tools: ToolSearch, mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources, mcp__plugin_atlassian_atlassian__getJiraIssue, mcp__plugin_atlassian_atlassian__editJiraIssue
---

# Skill: Jira — Append/Replace Migration Ticket

Met à jour la description d'un ticket Jira de migration en choisissant automatiquement entre **append** (ajout à la suite) et **replace** (remplacement complet) selon que la description existante a été auto-générée ou écrite par un humain.

## Logique de décision

1. **Lire la description actuelle**
2. **Détecter si auto-générée** : la description contient un footer du type `Description générée par /migrate-to-xpert-*` ou `Story créée à partir de l'analyse automatisée via /migrate-to-xpert-*` (sur la dernière ligne ou les 2 dernières lignes utiles)
3. **Si auto-générée** → **mode REPLACE** : remplacer la description entièrement par la nouvelle version (l'appelant fournit la version complète à jour)
4. **Si écrite par un humain** (pas de footer auto, ou footer non reconnu) → **mode APPEND** : ajouter la nouvelle section à la suite, séparée par `---` + titre daté

Ce comportement évite l'accumulation de contenu obsolète quand on relance plusieurs fois `/migrate-to-xpert-analysis` sur le même rapport.

## Mission

Empiler des artefacts dans un même ticket de migration (analyse → spec backend → spec frontend → résultats validation) en préservant l'historique humain, mais en remplaçant proprement les artefacts auto-générés pour éviter les doublons.

## Input

- **`{ticketKey}`** — Clé du ticket Jira (ex: `RPT-20058`)
- **`{sectionTitle}`** — Titre de la section à ajouter en mode APPEND (ex: `Analyse de migration`, `Spec backend`, `Spec frontend`, `Résultats validation`)
- **`{contentMarkdown}`** — Contenu de la **nouvelle section** (mode APPEND) ou de la **description complète à jour** (mode REPLACE — voir 4.5). L'appelant doit anticiper les deux cas.
- **`{fullReplacementMarkdown}`** *(optionnel)* — Si fourni, c'est la version complète qui sera utilisée en mode REPLACE. Si absent en mode REPLACE, le skill remonte une erreur pour éviter de tronquer du contenu.

## Prérequis

- Le serveur **MCP Atlassian** doit être connecté
- Le skill appelant **DOIT** avoir préalablement obtenu la confirmation explicite de l'utilisateur. Modifier un ticket Jira est une action visible.
- Le ticket doit exister (utiliser `jira-find-migration-ticket` au préalable pour le confirmer)

## Étapes

### 1. Charger les outils MCP nécessaires

```
ToolSearch(query="select:mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources,mcp__plugin_atlassian_atlassian__getJiraIssue,mcp__plugin_atlassian_atlassian__editJiraIssue", max_results=3)
```

### 2. Récupérer le cloudId

```
mcp__plugin_atlassian_atlassian__getAccessibleAtlassianResources()
```

Retenir l'`id` de la ressource `https://croesus-support.atlassian.net` (scope `write:jira-work` requis).

### 3. Lire la description actuelle

```
mcp__plugin_atlassian_atlassian__getJiraIssue(
  cloudId={cloudId},
  issueIdOrKey={ticketKey},
  fields=["description"],
  responseContentFormat="markdown"
)
```

Extraire le champ `fields.description` (chaîne markdown). Si la description est `null` ou vide, traiter comme chaîne vide `""`.

### 4. Détecter le mode (REPLACE vs APPEND)

La description est considérée **auto-générée** si elle satisfait l'**une** des conditions suivantes (testées sur les ~5 dernières lignes non vides) :

- Contient `Description générée par /migrate-to-xpert-` (pattern récent)
- Contient `Story créée à partir de l'analyse automatisée via /migrate-to-xpert-` (pattern historique)
- Contient `Analyse ajoutée via /migrate-to-xpert-` (pattern historique)

**Si auto-générée → mode REPLACE** :
- L'appelant DOIT fournir `{fullReplacementMarkdown}` (la version complète à jour de la description)
- Si `{fullReplacementMarkdown}` n'est pas fourni → retourner `status: "error"` avec message `Mode REPLACE détecté mais fullReplacementMarkdown manquant — refus pour éviter la perte de données.`
- La nouvelle description = `{fullReplacementMarkdown}` tel quel (l'appelant inclut son propre footer)

**Si écrite par un humain (description vide ou pas de footer auto reconnu) → mode APPEND** :
- Construire :
  ```markdown
  {Description existante telle quelle}

  ---

  ## {sectionTitle} (ajoutée le {YYYY-MM-DD})

  {contentMarkdown}
  ```
- Règles critiques :
  - ❌ NE JAMAIS modifier ou supprimer la description existante
  - ❌ NE JAMAIS réorganiser les sections existantes
  - ✅ Toujours ajouter à la fin, séparé par `---`
  - ✅ Toujours dater le titre `(ajoutée le YYYY-MM-DD)`

### 5. Mettre à jour le ticket

```
mcp__plugin_atlassian_atlassian__editJiraIssue(
  cloudId={cloudId},
  issueIdOrKey={ticketKey},
  fields={"description": {nouvelle description}},
  contentFormat="markdown"
)
```

### 6. Vérifier la mise à jour

Récupérer à nouveau le ticket pour confirmer que :
- **Mode REPLACE** : la nouvelle description correspond à `{fullReplacementMarkdown}` et contient bien un footer auto-généré à jour
- **Mode APPEND** : la description contient toujours l'ancien contenu (vérifier qu'une chaîne caractéristique du début est toujours présente) ET la nouvelle section avec le titre attendu est présente à la fin

## Output

```json
{
  "status": "updated" | "error",
  "mode": "replace" | "append",
  "ticket": {
    "key": "RPT-20058",
    "url": "https://croesus-support.atlassian.net/browse/RPT-20058",
    "sectionAdded": "Analyse de migration"
  },
  "error": null | "{message}"
}
```

Le champ `mode` indique au skill appelant comment l'opération a été interprétée :
- `"replace"` — le footer auto-généré a été détecté, la description a été entièrement remplacée par `{fullReplacementMarkdown}`
- `"append"` — la description existante a été préservée et la nouvelle section ajoutée à la suite

`sectionAdded` n'est pertinent qu'en mode `"append"` (en mode `"replace"` la description complète est nouvelle).

## Cas d'erreur

| Erreur | Action |
|--------|--------|
| MCP indisponible | Retourner `status: "error"` avec message `MCP Atlassian non disponible` |
| Ticket introuvable (404) | Retourner l'erreur, suggérer de vérifier la clé |
| Permission refusée (write:jira-work) | Retourner l'erreur, ne pas réessayer |
| Description existante non lisible | **Annuler la modification**. Ne jamais écraser une description qu'on n'a pas pu lire |
| Confirmation utilisateur absente | **Refuser**. Rappel : ce skill suppose que l'appelant a déjà obtenu confirmation |

## Exemples de sectionTitle par commande

| Commande | sectionTitle suggéré |
|----------|----------------------|
| `/migrate-to-xpert-analysis` | `Analyse de migration` |
| `/migrate-to-xpert-backend` | `Spec backend` (ou `Implémentation backend` après PR) |
| `/migrate-to-xpert-frontend` | `Spec frontend` (ou `Implémentation frontend` après PR) |
| `/migrate-to-xpert-validation` | `Résultats validation Conseiller vs Xpert` |

## Convention

- **Toujours** lire avant d'écrire (round-trip read → modify → write)
- **Toujours** préserver intégralement la description existante
- **Toujours** dater chaque section ajoutée
- **Ne jamais** écraser, fusionner ou réorganiser le contenu existant
- **Ne jamais** modifier d'autres champs que `description` (statut, assignee, labels, etc. sont hors scope de ce skill)

## Références

- Skill complémentaire : `jira-find-migration-ticket` (recherche), `jira-create-migration-ticket` (création)
- Instance Atlassian : `https://croesus-support.atlassian.net`
- Pour les transitions de statut, ajout d'assignee, labels : utiliser un skill dédié (à créer) ou les outils MCP directement
