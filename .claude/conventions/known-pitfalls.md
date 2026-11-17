# Pièges connus (leçons des tâches livrées)

Chaque entrée est un défaut **déjà payé** sur un ticket réel. Ce fichier est la mémoire d'équipe du
workspace : les agents qui planifient, implémentent ou relisent le consultent, et la `retrospective`
y propose ses ajouts (voir « Ajouter une entrée » en bas). Les règles de migration de base restent
dans `backend-conventions.md` / `frontend-conventions.md` — ici ne figurent que les pièges non
évidents. Format : la règle, quoi faire, le ticket d'origine.

## A. Fidélité du portage C++ → C#

- **Lecture d'une pref booléenne : `GetBoolean` (tolérant) vs `!= "YES"` (strict).** Le C++ lit
  `GetCresusConfig()->GetBoolean("PREF_X")` ; le C# porté compare souvent la chaîne à `"YES"`. Sur une
  base où la pref vaut autre chose (`1`, `true`…), les deux divergent sans erreur. → Comparer la
  sémantique de **lecture**, pas seulement la branche métier ; tester « pref absente » et « pref à une
  valeur non-`YES` non vide ». *(spike pref-use-external-doc-path ; écart non tranché sur
  `ReportSetupService.cs`, vérifier `GetBoolean` avant d'affirmer un bug.)*
- **Port partiel masqué par un défaut qui coïncide.** Une VPF qui ne porte que la branche *fallback*
  du C++ ne montre aucun écart tant que la config par défaut donne le même résultat. → Porter
  **toutes** les branches ; après un fix de fidélité, auditer tous les appelants du helper C++ partagé
  (procédure : `backend-conventions.md` § « fonction C++ à appelants multiples »). Un `TODO` qui cite
  un symbole C++ est un défaut ouvert, pas une note. *(RPT-20533 → RPT-20575)*
- **Sous-type de rapport : ne pas l'encoder dans une VPF basée sur `SourceType`.** Le contrôleur pose
  un seul `SourceType` pour toute une famille (ex. `OrderEntry`), la VPF ne peut donc pas distinguer
  MODEL de UMA. → Quand le C++ branche sur `GetSpecialSourceType()` ou un sous-type, garder la VPF au
  défaut générique (niveau pad) et forcer la valeur propre au sous-type par un `InitialValue` dans le
  `Parameters.cs` du rapport concerné. *(RPT-20548, `GetHiddenReportSourceParameter`)*
- **Self-read d'une VPF non garanti.** Une VPF qui lit dans `ParametersSoFar` le `PARAM_` sur lequel
  elle est elle-même câblée n'est pas assurée d'y trouver la valeur du client. → Prévoir un repli sur
  `IncomingReportGenerationRequest.Reports[].Parameters` (par nom) et un test d'intégration.
  Précédents : `GetHiddenReportSourceParameter`, `GetRebalanceIdParameter`. *(RPT-18883)*
- **`PARAM_IgnoreIdMasking` : le défaut est « non masqué ».** `GetDisplayUnmaskedIdParameter` renvoie
  `"1"` sauf pour les rapports de `ReportsWithInitialValueZero`. → Ne pas supposer « ne rien ajouter » :
  lire la valeur dans le XML Conseiller ; si `0`, enregistrer le rapport (skill
  `register-ignore-id-masking`). *(RPT-18883)*
- **La décision d'une pref vit en amont de `ReportServer`.** Le moteur ne lit pas les prefs : il reçoit
  des paramètres déjà résolus. → Chercher d'abord dans `CroesusServer` (`Src/ReportApi/`, `Src/View/`)
  et `PM/Tools/ReportCommander`. Pour un portage Xpert, l'analogue du flux API est le chemin **batch**
  de `ReportCommander`, pas le GUI serveur. *(spike pref-use-external-doc-path)*
- **Une pref a deux « défauts ».** Le `@DEFAULT_VALUE` du `spB_DEF` dans `MigrationScripts/` vaut pour
  les installs existantes ; `PM/SupportFiles/DBConfig/croesus.sql` peut le surcharger pour les
  nouvelles. → Grepper la clé aux **deux** endroits avant de conclure sur le comportement par défaut.
  Attention aux scripts de noms quasi identiques (casse différente) qui définissent des prefs
  différentes. *(spike pref-use-external-doc-path : déclarée `NO`, baseline `YES`)*

Déjà couverts ailleurs, à ne pas redoubler : `ValidationFunction` ≠ `ValueProviderFunction` et clé
VPF non enregistrée = ignorée en silence à la génération (`backend-conventions.md` ; contrôle :
`bash .claude/scripts/check-vpf-registration.sh --changed`) ; rapport frère sur
le même `TPL_` comme oracle des clés radio/combo (`CLAUDE.md`, `backend-conventions.md`).

## B. Validation Xpert (JSON) vs Conseiller (XML)

Un paramètre **présent dans le XML mais absent du JSON** a trois causes possibles. Les vérifier dans
cet ordre avant de toucher au câblage :

1. **`PrefValidation` fausse → paramètre retiré.** `ReportMetaDataService.GetExcludedParametersBasedOnPref`
   **supprime** le paramètre de la tâche Xpert, alors que le C++ l'envoie quand même (à `0`). Câbler une
   VPF n'y change rien : elle ne s'exécute pas sur un paramètre filtré. → Lire la `PrefValidation` dans
   `{CheckBox,Combo,Radio,Hidden}ParametersImplementation.cs`, et comparer les prefs de la firme des
   **deux** captures (un écart de prefs invalide la comparaison). Deux sous-pièges dans
   `ConditionStringUtilities.EvaluateCondition` : une pref non retournée fait tomber la condition à
   `false` (simple `Warning`), et `in (…)` compare en **sensible à la casse** là où le C++ est
   insensible. *(PROJECTED_PORTFOLIO)*
2. **Pas d'`InitialValue` explicite → paramètre non sérialisé.** RTM n'émet qu'un paramètre résolu à une
   valeur concrète. Une VPF qui produit `"1"` est émise ; une VPF qui produit `"0"`, faux ou vide ne
   l'est **pas**. `initialValueFromParam` pointant sur un PRE non envoyé en batch ne produit rien non
   plus. → Pour tout drapeau ou constante attendu en sortie, poser un `InitialValue` explicite dans le
   `Parameters.cs` du rapport (`InitialValue="0"` pour forcer un `0`), en gardant la VPF pour la
   surcharge contextuelle. *(RPT-18883)*
3. **Clé VPF non enregistrée** dans l'executer Pre/Post : la VPF ne s'exécute pas et le paramètre garde
   sa valeur initiale. → `bash .claude/scripts/check-vpf-registration.sh --where <Clé>`.

Une comparaison verte n'élimine pas la divergence : elle peut réapparaître sur une firme aux prefs
différentes. Le dire dans le rapport de validation.

## C. Tests et preuves

- **AutoFixture peuple toute propriété publique settable.** Asserter sur une propriété sans l'avoir
  posée en Arrange ne prouve rien. → Poser la valeur **opposée** à l'attendu en Arrange, puis asserter.
  *(RPT-20575 ; détail dans `backend-conventions.md` § IsReadOnly)*
- **Un test ajouté « pour couvrir X » doit pouvoir échouer.** Quand une revue signale un invariant tenu
  par le code mais verrouillé par aucun test, exiger une **preuve par mutation** : casser
  temporairement l'invariant, montrer que le nouveau test échoue (sortie brute du runner dans
  `build-summary.md`), restaurer le fichier et prouver qu'il est identique (hash avant/après). La
  mutation n'est jamais commitée. L'inscrire comme critère de sortie dans
  `_signals/revision-request.md`. *(RPT-20575 : 6 cas existants sur 7 étaient aveugles à la garde)*
- **Un compte d'avertissements `dotnet build` n'est pas comparable.** Le même code donne 2
  avertissements en incrémental et 1163 avec `-t:Rebuild`. → Pour prouver « aucun nouvel
  avertissement », faire un `-t:Rebuild` du projet et comparer le compte **par fichier touché**, `HEAD`
  contre la version livrée. *(RPT-20575)*
- **Chiffre de build ou de test : mesuré sur l'index, par soi-même.** Voir `protocol.md` § Traçabilité.
  *(RPT-21649)*
- **Jamais deux agents implémenteurs sur la même tranche dans le même checkout**, ni scratchpad
  partagé : l'un lit comme des échecs réels les mutations en cours de l'autre. *(RPT-21507)*

## D. Conception et revue

- **Copier un patron avec sa garde.** Reprendre un bloc existant sans les lignes qui le précèdent
  réintroduit le bug que ces lignes corrigeaient. → En revue d'un diff qui réutilise un patron maison,
  ouvrir la source et comparer les **bornes** du bloc copié ; une garde commentée signale un bug déjà
  payé. Un changement de code de statut HTTP observable se déclare dans la PR comme un changement de
  contrat. *(RPT-21649 : `catch (JsonException)` repris sans `if (Request.HasJsonContentType())`,
  415 → 500)*
- **Garantie « par construction » : énumérer les canaux.** Une faille fermée sur le chemin nominal
  reste ouverte par les autres portes. → Devant une contrainte de sécurité ou d'intégrité, grepper le
  symbole dans tout le repo et demander pour chaque point d'entrée : qui peut l'écrire, qu'est-ce qui
  l'en empêche ? Poser la garde au **point de passage unique** quand il existe (ex.
  `BaseReportGenerationController.CreateReportGeneration`). Une protection derrière un feature flag
  désactivé ne protège rien. *(RPT-21649)*
- **Un décorateur C# ne voit pas les appels via `this`.** Si la classe interne appelle ses propres
  méthodes directement, le décorateur est court-circuité sur ce chemin. → Vérifier avant de supposer
  l'interception ; sinon injecter l'interface dans l'inner, ou documenter la portée réelle.
  *(RPT-20590, `CoalescingConditionStringUtilities`)*
- **Un test qui rejette un format documente parfois une limitation, pas une règle métier.** Ne pas
  déduire le format attendu par Conseiller d'un test Xpert : lire le parseur C++. *(RPT-21649,
  triplets `RPM_V_File` — voir `rma-architecture-notes.md`)*
- **Flux ajouté à côté d'un flux existant** → classe de base + interface générique, pas une branche
  inline ; en faire un point de décision du plan et dimensionner l'estimation en conséquence.
  *(RPT-20114 ; déjà demandé par `planner.md` / `explorer.md`)*

## E. Git et build

- **Fins de ligne du monolithe : mesurer le blob, en comptant les octets.** Le dépôt n'est pas
  homogène (constaté : `CFF/Products/ReportManagerApi` en LF, `CFF/ReportFoundations` en CRLF, parfois
  avec BOM — remesurer à chaque fois).

  ```bash
  git cat-file -p :<fichier> | tr -dc '\r' | wc -c    # 0 = LF, >0 = CRLF
  ```

  Ne **jamais** utiliser `grep -c $'\r'` : il renvoie le nombre de lignes même sur un blob LF. Blob LF →
  `git add` ordinaire. Blob CRLF → conserver CRLF et `git -c core.autocrlf=false add`. Contrôler
  ensuite avec `git diff --cached --numstat` (ajouts ≈ suppressions ≈ taille du fichier = réécriture) ;
  réparer avec `git add --renormalize <fichier>`. *(RPT-21649 : trois fichiers réécrits en entier)*
- **Ajout de colonne en base : `exec spAddColumn`, jamais `ALTER TABLE`.** Script numéroté sous
  `PM/SupportFiles/MigrationScripts/<major>/<minor>/000/<NNN>/<TICKET>_<desc>.sql`, commentaires sans
  accents. L'emplacement `<NNN>` dépend du train de release : le faire confirmer. *(RPT-19587)*
- **Builder ReportManagerApi depuis le chemin réel du monolithe** et **piège `--skip-nx-cache` de
  pf-web** : voir le skill `workspace-commands`.

## Ajouter une entrée

Une entrée entre ici si elle est (1) non évidente à la lecture du code, (2) réutilisable au-delà du
ticket, (3) vérifiée — pas une hypothèse. Trois à six lignes : la règle, quoi faire, le ticket. Si elle
contredit une entrée existante, corriger l'ancienne plutôt qu'en empiler une nouvelle. Les faits sur
le fonctionnement interne de ReportManagerApi vont dans `rma-architecture-notes.md`.
