# Mise à jour directe du ticket Jira

Procédure de l'étape 8. **Aucune écriture sans confirmation explicite de l'utilisateur**, après lui avoir
montré ce qui sera écrit.

---

## Ce qui est modifiable, et ce qui ne l'est pas

Vérifié sur le projet `RPT`, type de ticket **Test** (Xray, `issuetype.id = 10017`) via
`getJiraIssueTypeMetaWithFields` : les seuls champs exposés sont les champs système standard —
`summary`, `description`, `environment`, `labels`, `components`, `priority`, `assignee`, `issuelinks`,
`attachment`, `parent`, `reporter`.

| Contenu du cas de test | Où il vit | Modifiable par le MCP ? |
|---|---|---|
| Objectif, préconditions, données | champ **`description`** | **oui** |
| Pas de test (Action / Données / Résultat attendu) | **store Xray**, pas un champ Jira | **non** |
| Pièces jointes (CSV) | `attachment` | non — pas d'outil d'upload dans le MCP |

**Conséquence** : la revue met à jour la description et dépose le scénario révisé pour ré-importation.
Ne pas chercher un `customfield_*` de pas de test : il n'existe pas sur ce projet. Si un autre projet en
expose un, le vérifier avec `getJiraIssueTypeMetaWithFields` avant d'écrire.

Pour les pas de test, deux voies, à proposer à l'utilisateur :

1. **Ré-importation Xray** — lui remettre `<ticket>-xray-import.csv`, produit au format Test Case
   Importer (voir [`format-xray-csv.md`](format-xray-csv.md)) ; l'import se fait depuis l'interface
   Xray. C'est la voie propre : les pas restent structurés et exécutables.
2. **Report dans la description** — ajouter le scénario révisé en tableau dans la description, sous un
   titre explicite, en précisant que les pas Xray restent à synchroniser. Voie de dépannage, à ne pas
   utiliser seule si les pas Xray existent déjà : on créerait deux versions divergentes.

---

## Modes de sortie

Demander le mode au début si l'utilisateur ne l'a pas précisé :

| Mode | Effet |
|---|---|
| `fichiers` | document de revue + CSV révisé seulement. Le ticket n'est pas touché. |
| `jira` | met à jour la description du ticket ; les fichiers restent produits localement (ils sont la source du contenu écrit). |
| `les deux` | défaut recommandé : fichiers, puis mise à jour du ticket après confirmation. |

---

## Procédure

### 1. Outils et cloudId

```
ToolSearch(query="select:<préfixe>getJiraIssue,<préfixe>editJiraIssue,<préfixe>addCommentToJiraIssue", max_results=3)
```

Le préfixe du serveur MCP Atlassian varie selon la configuration (`mcp__atlassian__`,
`mcp__claude_ai_Atlassian__`, `mcp__plugin_atlassian_atlassian__`, …). Le résoudre par `ToolSearch`
plutôt que de le coder en dur.

**Plusieurs connecteurs Atlassian peuvent coexister, avec des droits différents.** Observé le
2026-10-16 : le connecteur `mcp__claude_ai_Atlassian__` lit sans problème mais refuse l'écriture avec
`403 — The app is not installed on this instance`, tandis que `mcp__plugin_atlassian_atlassian__` écrit
correctement sur la même instance. En cas de 403 à l'écriture, **ne pas conclure à un manque de droits
de l'utilisateur** : rejouer le même appel sur l'autre connecteur avant de renoncer.

`cloudId` : passer directement le hostname **`croesus-support.atlassian.net`** — il est accepté. Recourir
à `getAccessibleAtlassianResources` seulement en cas d'échec.

### 2. Relire la description courante

```
getJiraIssue(cloudId=…, issueIdOrKey=<ticket>, fields=["summary","description","issuetype"],
             responseContentFormat="markdown")
```

Confirmer le type de ticket, et conserver la description existante : elle sert de base, on ne la
reconstruit pas de zéro.

### 3. Composer la nouvelle description

Structure visée :

```markdown
**Objectif :**
<objectif révisé — reformulé seulement si la revue a montré qu'il décrit un comportement impossible>

**Préconditions :**
**Environnement :** …
**Utilisateurs :** …
**Données :** …
**Précautions d'exécution :** …

**Écarts à valider (revue du <date>) :**
1. …
2. …

_Revue générée par /review-test-scenario — <branche>@<sha> — <date>_
```

Règles de composition :

- **Préserver le contenu humain** : commentaires, liens, historique, sections ajoutées par l'équipe. On
  remplace l'objectif, les préconditions et les données ; on ne supprime rien d'autre.
- **Idempotence** : si la description porte déjà le footer `Revue générée par /review-test-scenario`,
  remplacer le bloc généré précédent au lieu d'empiler une seconde revue.
- **Ne jamais retirer un écart** de la section « Écarts à valider » sans que l'utilisateur ait dit qu'il
  est tranché.
- Le texte doit rester lisible par un testeur qui n'a pas lu le code : pas de `fichier:ligne` dans le
  ticket — ces références restent dans `<ticket>-revue.md`, qui est mentionné dans le ticket.

### 4. Écrire

```
editJiraIssue(cloudId=…, issueIdOrKey=<ticket>,
              fields={"description": "<markdown>"},
              contentFormat="markdown", responseContentFormat="markdown")
```

### 5. Vérifier le rendu

Relire la description (`getJiraIssue`). La conversion markdown → ADF peut aplatir un tableau. Si un
tableau est illisible, le remplacer par une liste numérotée `Action / Données / Résultat attendu` et
réécrire.

### 6. Commenter plutôt qu'écraser, quand c'est plus sûr

Si la description contient beaucoup de contenu humain structuré, ou si l'utilisateur hésite, poser la
revue en commentaire :

```
addCommentToJiraIssue(cloudId=…, issueIdOrKey=<ticket>, body="<markdown>", contentFormat="markdown")
```

Le commentaire est non destructif et réversible. Le proposer d'office quand le ticket n'est pas au
statut `Backlog` / `A faire`.

---

## Après écriture

Restituer à l'utilisateur :

- l'URL du ticket (`https://croesus-support.atlassian.net/browse/<ticket>`) ;
- ce qui a été écrit (description remplacée ou commentaire ajouté) ;
- **ce qui reste à faire à la main** : importer `<ticket>-xray-import.csv` dans Xray pour les pas de
  test — avec les trois mises en garde de [`format-xray-csv.md`](format-xray-csv.md) (mapping,
  encodage, risque de doublon) — et joindre le document de revue si l'équipe veut la trace du
  raisonnement.
