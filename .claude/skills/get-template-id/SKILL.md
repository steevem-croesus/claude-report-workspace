---
name: get-template-id
description: Lookup le template ID d'un rapport dans docs/template_ids.csv à partir du report internal name. Utiliser au début d'une migration (frontend ou backend) quand le template ID est requis.
---

# Skill: Get Template ID

Récupère le template ID d'un rapport par lookup dans le fichier CSV.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Objectif

Obtenir le template ID du rapport. Ce ID est nécessaire pour:
- Les fixtures e2e frontend (`Account.v1.json` et `params-{templateId}.Account.v1.json`)
- L'enregistrement backend dans `WebRTMRunner.cs`
- Toute référence au rapport dans les systèmes externes

## Processus

### Input requis

Le nom interne du rapport (ex: `FOREIGN_PROPERTY`, `SUMMARY_PORT_WO_REF`).

### 1. Lookup dans le CSV

Lire le fichier `docs/template_ids.csv` et chercher la ligne où `report_internal_name` correspond au nom interne du rapport.

Le fichier a le format:
```csv
"template_id","report_internal_name"
1,ALARMS
2,ANNIC
...
```

Si trouvé, afficher:
```
Template ID pour {NOM_INTERNE}: {ID}
```

### 2. Si non trouvé

Afficher un message d'erreur:
```
⚠ Template ID non trouvé pour {NOM_INTERNE} dans docs/template_ids.csv.
Vérifier que le nom interne est correct ou ajouter l'entrée manuellement dans le CSV.
```

**Ne pas continuer le workflow appelant sans cette information.**

### Output

Le template ID (un nombre, ex: `40`, `5000281`).
