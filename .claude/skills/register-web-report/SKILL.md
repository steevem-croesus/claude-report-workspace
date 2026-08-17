---
name: register-web-report
description: Enregistre un rapport dans la liste des rapports Web supportés (WebRTMRunner.cs). Ajoute le ReportName dans ConstructSupportedWebReportList en ordre alphabétique. Utiliser lors de la migration d'un nouveau rapport.
allowed-tools: Read, Edit, Grep, Glob, Bash
---

# Skill: Register Web Report

Ajoute un rapport à la liste des rapports Web supportés dans `WebRTMRunner.cs`.

**Utilisé par:** report-developer (étape finale de migration d'un rapport)

---

## Quand utiliser ce skill

À utiliser lors de la migration d'un nouveau rapport, pour l'enregistrer dans la liste des rapports supportés par le Web.

---

## Input

L'utilisateur fournit:
- **Nom de la classe du rapport**: Ex: `RPT_AssetsUnderManagement`

Si non fourni, déduire du rapport en cours de migration.

---

## Étape 1: Localiser le fichier

```
repos/ReportFoundations/ReportServices/WebRTMRunner.cs
```

Vérifier que le fichier existe:
```bash
find -L ReportFoundations -name "WebRTMRunner.cs" 2>/dev/null
```

---

## Étape 2: Vérifier que le rapport n'est pas déjà enregistré

```bash
grep "RPT_NomRapport.ReportName" repos/ReportFoundations/ReportServices/WebRTMRunner.cs
```

Si déjà présent, informer l'utilisateur et ne rien faire.

---

## Étape 3: Trouver la position alphabétique

Lire la méthode `ConstructSupportedWebReportList()` et identifier la position correcte en ordre alphabétique parmi les entrées `RPT_*.ReportName` existantes.

**Exemple:** Pour `RPT_ForeignPropertyStandard`, insérer entre `RPT_ForeignPropertySimple` et `RPT_GainsAndLossesRealized`.

---

## Étape 4: Ajouter l'entrée

Insérer la ligne suivante à la position alphabétique correcte:

```csharp
                RPT_NomRapport.ReportName,
```

**Important:**
- Respecter l'indentation existante (16 espaces typiquement)
- Terminer par une virgule
- Format exact: `RPT_{NomRapport}.ReportName,`

---

## Étape 5: Vérifier le using

S'assurer que le `using` pour le namespace du rapport est présent en haut du fichier. Vérifier les usings existants pour déterminer si un ajout est nécessaire.

---

## Checklist finale

- [ ] Rapport pas déjà dans la liste
- [ ] Entrée ajoutée en ordre alphabétique
- [ ] Format et indentation cohérents avec les entrées existantes
- [ ] Using ajouté si nécessaire

---

## Étape suivante

Invoquer `activate-web-report-pref` pour activer la `PREF_REPORT_*=YES` du rapport dans la BD dev (sinon il ne sera pas visible dans Xpert), puis `update-e2e-baselines` pour les baselines E2E qui vont casser.

---

## Rapport de fin

Fournir:
1. **Rapport ajouté**: `RPT_NomRapport.ReportName`
2. **Position**: Entre quelles entrées il a été inséré
3. **Fichier modifié**: `repos/ReportFoundations/ReportServices/WebRTMRunner.cs`

---

## Référence

**Implémentation de référence:** `RPT_AssetsUnderManagement.ReportName` ajouté dans RPT-18494 (commit `58cd1e8860`)

**Fichier:** `repos/ReportFoundations/ReportServices/WebRTMRunner.cs` — méthode `ConstructSupportedWebReportList()`
