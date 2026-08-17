---
name: rebuild-before-validation
description: Rebuild obligatoire de RTMTester et ReportManagerApi après toute implémentation backend, avant de demander le JSON Xpert et le XML Conseiller pour la validation. Détecte les erreurs de compilation tôt.
---

# Skill: Rebuild Before Validation

Après toute migration/implémentation backend (modifications dans ReportFoundations ou ReportManagerApi), **rebuild obligatoirement** RTMTester et ReportManagerApi et corriger toutes les erreurs avant de demander le JSON Xpert et le XML Conseiller à l'utilisateur.

**IMPORTANT: Répondre TOUJOURS en français à l'utilisateur.**

## Pourquoi

- Les changements dans `WebRTMRunner.cs`, `RadioParametersImplementation.cs`, `CheckBoxParametersImplementation.cs`, `Parameters.cs` d'un rapport, etc. ne sont pas toujours couverts par `dotnet build ReportManagerAPI.sln` seul (certains projets sont dans ReportFoundations et compilent via MSBuild classique, pas via `dotnet build`).
- RTMTester est l'exécutable qui matérialise les templates RTM dans la base — il doit compiler pour que la migration puisse être testée.
- `dotnet build` sur les anciens projets .NET Framework échoue sur des erreurs `Serilog could not be found` non liées au code — utiliser **MSBuild** pour ces solutions.
- Le frontend pf-web doit aussi être prêt (npm i + dev server Xpert) pour que l'utilisateur puisse générer le JSON à comparer.
- Ne jamais demander à l'utilisateur le XML/JSON pour validation si le code n'est pas dans un état compilable **et** le frontend pas démarré — c'est une perte de temps pour l'utilisateur.

## Quand utiliser

**Proactif** — dès que l'implémentation backend est terminée (tous les fichiers modifiés, tests ajoutés), **avant** de demander l'XML Conseiller et le JSON Xpert.

## Procédure

### Étape 1 — Rebuild ReportManagerApi (solution moderne .NET 8)

```bash
cd "c:/Git projects/monolith/monolith/CFF/Products/ReportManagerApi"
dotnet build ReportManagerAPI.sln 2>&1 | grep -E "Build succeeded|Build FAILED|error"
```

**Résultat attendu :** `Build succeeded.` sans erreurs.

### Étape 2 — Rebuild RTMTester (solution legacy .NET Framework/Standard — MSBuild obligatoire)

**⚠️ NE PAS utiliser `dotnet build`** pour RTMTester — les anciens projets csproj (ReportFoundations, etc.) échouent sur les références Serilog/ILogger transitive qui ne sont pas résolues par `dotnet build`. Utiliser MSBuild VS2022 :

```bash
# Première fois (ou après changements NuGet) : restore
cd "c:/Git projects/monolith/monolith/CFF/Tools/Reports/RTMTester"
"/c/Program Files/Microsoft Visual Studio/2022/Professional/MSBuild/Current/Bin/MSBuild.exe" RTMTester.sln -t:Restore -p:Configuration=Debug -p:RuntimeIdentifier=win -nologo

# Build
"/c/Program Files/Microsoft Visual Studio/2022/Professional/MSBuild/Current/Bin/MSBuild.exe" RTMTester.sln -p:Configuration=Debug -m -v:minimal -nologo 2>&1 | tail -20
```

**Résultat attendu :** Les 5 dernières lignes doivent montrer la compilation réussie des projets clés :
- `ReportImplementations -> ...ReportImplementations.dll`
- `ReportServices -> ...ReportServices.dll`
- `RTMTester -> ...RTMTester.exe`

### Étape 3 — Exécuter les tests

```bash
cd "c:/Git projects/monolith/monolith/CFF/Products/ReportManagerApi"
dotnet test ReportManagerAPI.sln --no-build 2>&1 | tail -10
```

**Résultat attendu :** Tous les tests passent (`Failed: 0`).

### Étape 4 — Corriger les erreurs détectées

Si une erreur apparaît :
1. **Lire le message d'erreur complet** — ne pas supposer la cause
2. **Identifier le fichier source** (chemin + ligne) mentionné dans l'erreur
3. **Corriger** puis **relancer le rebuild** (étape concernée)
4. **Ne pas passer à l'étape suivante** tant que la précédente échoue
5. Répéter jusqu'à ce que ReportManagerApi ET RTMTester compilent tous les deux sans erreur

**Erreurs courantes :**

| Erreur | Cause fréquente | Fix |
|--------|----------------|-----|
| `CS7036: no argument given for parameter 'X'` dans un test d'executer | Signature du constructeur de l'executer a changé (ajout de dépendance injectée comme `IUserInfoFinder`) | Mettre à jour les appels dans les tests pour ajouter `null` pour la nouvelle dépendance |
| `CS0246: type 'Serilog' not found` avec `dotnet build` | Projet .NET Framework/Standard non supporté par `dotnet build` | Utiliser MSBuild comme montré à l'étape 2 |
| `CS0246: type 'Foo' not found` dans le code | Using manquant ou mauvais namespace | Ajouter le `using` approprié |
| `error : Your project file doesn't list 'win' as a RuntimeIdentifier` | Restore non fait avec le bon RID | Rerouler le restore avec `-p:RuntimeIdentifier=win` |
| Tests qui échouent sur un DateTime | Format `yyyy.MM.dd` vs `yyyy-MM-dd` mal géré | Vérifier `DateTimeFormat.REPORT_SERVER_STANDARD` (POST) vs `API_LONG_DATE_STANDARD` (PRE) |

### Étape 5 — Préparer et lancer le frontend pf-web (Xpert)

Après le succès des builds backend, préparer et démarrer le frontend Xpert local pour que l'utilisateur puisse générer le rapport et récupérer le JSON.

```bash
# 1. Installer les dépendances npm (peut être long la première fois)
cd "c:/Git projects/pfweb/pf-web"
npm i

# 2. Une fois npm i TERMINÉ, lancer le dev server Xpert pointant sur le backend local
nx hybrid xpert --backend=http://localhost
```

**⚠️ Ordre strict :** attendre que `npm i` soit **complètement terminé** avant de lancer `nx hybrid xpert`. Ne pas paralléliser — `nx` a besoin des node_modules.

**Lancer `nx hybrid xpert` en arrière-plan** (`run_in_background: true`) puisque c'est un serveur dev qui tourne indéfiniment. Ne pas attendre qu'il se termine.

**Attendre que le serveur soit prêt** en lisant la sortie du processus background : chercher un message de type `Application bundle generation complete`, `Local: http://localhost:4200` ou équivalent avant de passer à l'étape 6.

**Répertoire pf-web :** `c:/Git projects/pfweb/pf-web`

### Étape 6 — Demander l'XML/JSON seulement après succès

Seulement **après** que les deux builds backend réussissent, les tests passent, et le frontend Xpert est démarré, demander à l'utilisateur :

```
✅ Backend — ReportManagerApi et RTMTester compilent sans erreur
✅ Tests — {N}/{N} tests passent
✅ Frontend — npm i terminé, nx hybrid xpert lancé (http://localhost:4200)

Pour la validation des paramètres (Conseiller vs Xpert) :
1. Fournir le **XML Conseiller** du rapport {REPORT_NAME} (généré dans le legacy)
2. Fournir le **JSON Xpert** généré via Xpert local (http://localhost:4200)

Je lancerai ensuite le skill `compare-report-params` pour comparer.
```

## Anti-patterns à éviter

1. **Ne jamais skip le rebuild** — "le code semble correct, allons-y" : une erreur compile peut masquer une régression invisible au code review
2. **Ne jamais ignorer un `Build FAILED`** — corriger d'abord, demander les XML/JSON ensuite
3. **Ne pas confondre warnings et errors** — les warnings CS8618/CS1591 sont OK, seules les `error` bloquent
4. **Ne pas demander à l'utilisateur de rebuild à votre place** — c'est votre responsabilité d'agent
5. **Ne pas utiliser `dotnet build` sur RTMTester/RTMLauncher** — les projets legacy échouent faussement sur Serilog. MSBuild VS2022 est obligatoire

## Référence

- Build system Croesus : voir `CLAUDE.md` section "Build & Test Commands"
- Conventions git : skill `git-conventions-monolith`
- Validation paramètres : skill `compare-report-params`
