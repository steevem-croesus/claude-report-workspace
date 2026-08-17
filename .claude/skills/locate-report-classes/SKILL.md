---
name: locate-report-classes
description: Retrouve les classes C# d'un rapport (RPT_*, Parameters.cs, classe parent) à partir de son nom interne (ex FOREIGN_PROPERTY). Utiliser au début d'une migration pour identifier tous les fichiers sources C# du rapport.
allowed-tools: Read, Grep, Glob, Bash
---

# Skill: Locate Report Classes

Retrouve les fichiers C# d'un rapport à partir de son nom interne.

---

## Input

L'utilisateur fournit:
- **Nom interne du rapport**: Ex: `FOREIGN_PROPERTY`, `ASSETS_UNDER_MGT`

Si non fourni, demander à l'utilisateur.

---

## Exécution

### Étape 1: Trouver la classe principale (RPT_*)

Chercher le fichier `RPT_*.cs` qui déclare le `ReportName` correspondant au nom interne.

**Plan A — String littéral:**
```bash
grep -rl '"NOM_INTERNE"' repos/ReportFoundations/ReportImplementations/Implementations/Reports/ --include="RPT_*.cs"
```

**Plan B — Constante via ReportDefines:**
Si Plan A ne retourne rien, le `ReportName` peut être défini via une constante (ex: `ReportDefines.Names.AssetUnderManagement`). Chercher la constante d'abord:
```bash
grep -r '"NOM_INTERNE"' repos/ReportFoundations/ --include="ReportDefines.cs"
```
Cela retourne le nom de la constante (ex: `AssetUnderManagement`). Puis chercher quel `RPT_*.cs` l'utilise:
```bash
find -L ReportFoundations -name "RPT_*.cs" -exec grep -l "NomConstante" {} \;
```

**Plan C — Recherche large:**
Si Plans A et B échouent, chercher le nom interne dans tous les fichiers:
```bash
find -L ReportFoundations -name "RPT_*.cs" -exec grep -l "NOM_INTERNE" {} \;
```

Si toujours rien trouvé, afficher un message d'erreur et arrêter.

### Étape 2: Identifier la classe parent

Dans le fichier trouvé, lire la déclaration de classe pour identifier l'héritage:

```bash
grep "class RPT_" <fichier_trouvé>
```

Cela donne le pattern: `class RPT_X : RPT_Y` ou `class RPT_X : ReportImplementation`

- Si la classe parent est `ReportImplementation` → pas de classe Base, passer à l'étape 3
- Si la classe parent est un autre `RPT_*` (ex: `RPT_BaseForeignProperty`) → localiser le fichier parent:

```bash
find -L ReportFoundations -name "RPT_BaseForeignProperty.cs" 2>/dev/null
```

### Étape 3: Localiser tous les Parameters.cs

Trouver tous les fichiers `Parameters.cs` dans le même dossier que la classe principale ET dans le dossier de la classe parent (Base):

```bash
# Parameters.cs du rapport spécifique (même dossier que RPT_*.cs)
# Parameters.cs du parent (dossier Base)
find -L ReportFoundations -path "*NomDossierRapport*" -name "Parameters.cs" 2>/dev/null
```

**IMPORTANT:** Les paramètres peuvent être répartis entre le `Parameters.cs` du rapport spécifique (Standard/Simple) et celui de la classe Base. Il faut identifier les deux.

### Étape 4: Afficher le résultat

Présenter les fichiers trouvés:

```
## Rapport: NOM_INTERNE

### Classe principale
- Fichier: repos/ReportFoundations/.../RPT_ForeignProperty.cs
- Classe: RPT_ForeignProperty
- Hérite de: RPT_BaseForeignProperty

### Classe parent (Base)
- Fichier: repos/ReportFoundations/.../RPT_BaseForeignProperty.cs
- Classe: RPT_BaseForeignProperty

### Fichiers Parameters.cs
- repos/ReportFoundations/.../Standard/Parameters.cs (paramètres spécifiques)
- repos/ReportFoundations/.../Base/Parameters.cs (paramètres communs)
```

Si pas de classe parent (hérite directement de `ReportImplementation`), indiquer qu'il n'y a pas de Base.

---

## Référence

**Exemple:** `FOREIGN_PROPERTY`
- Classe principale: `RPT_ForeignProperty` → `repos/ReportFoundations/.../ForeignProperty/Standard/RPT_ForeignProperty.cs`
- Classe parent: `RPT_BaseForeignProperty` → `repos/ReportFoundations/.../ForeignProperty/Base/RPT_BaseForeignProperty.cs`
- Parameters: `Standard/Parameters.cs` + `Base/Parameters.cs`
