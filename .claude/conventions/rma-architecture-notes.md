# Notes d'architecture — ReportManagerApi et alentours

Faits établis en lisant le code pendant des tâches réelles, qu'on ne retrouve pas dans les références
du monolithe (`monolith-references.md` §B). À consulter **avant de planifier ou d'investiguer** dans
ces zones. Chaque note porte sa date ou son ticket : le code évolue, **revérifier un numéro de ligne
ou un nom de classe avant de s'y fier**.

## Pipeline de génération

- **La génération est en mémoire, sans saut SQS.** `BaseReportGenerationController` →
  `ReportGenerationService` → `BaseBatchServiceAsynchronous`. `IQueueMessaging` est enregistré dans le
  DI mais rien ne le consomme. Les frontières inter-processus sont le gRPC vers le ReportSpooler puis
  le Frameworkserver (`:8999`), le stockage S3 et la base (Dapper). *(vérifié 2026-11)*
- **Quels rapports générer pour une source : un scénario Flex, pas le helper `DefaultReport`.** Le
  chemin de génération passe par `GetDefaultReportSetupConfig` via
  `IReportSetupRepository.BuildScenarioData(...)`, dont les classes vivent dans **ReportFoundations**
  (`ReportBusinessLogic/.../FlexScenarios/ReportSetupConfig`). `DefaultReport.GetDefaultReportAsSetup`
  ne sert que le côté requête. Une feature qui lit la config par défaut entraîne donc ReportFoundations
  dans le périmètre. *(RPT-20114)*

## Session Croesus, concurrence et caches

- **La session/factory Croesus est thread-affine : ne pas paralléliser une boucle qui l'utilise.**
  L'`IFactory` Scoped est mono-thread par construction (`NotifyOfCrossThreadDependency()`, état indexé
  par `ManagedThreadId`, connexion TCP unique sérialisée sous `lock`). Paralléliser
  `ReportSetupService.GetReportSetup` n'apporte aucun gain réseau et risque une fuite inter-firmes si
  on clone des sessions sans ré-impersonation. S'y ajoute `CurrentReportId`, relu à l'exécution par des
  closures stockées dans l'executer PRE : le passer en argument ne suffit pas. Verdict : NO-GO sans un
  spike dédié (pool de `Factory.CloneScoped`). Le gain de latence s'obtient par préchauffage batch et
  cache. *(RPT-20590)*
- **Le cache de messages du `MessageManager` est par requête.** `Factory.Dispose` vide `MessageCache`
  en fin de requête : chaque requête recharge `B_MSG`. Pour un cache inter-requêtes, ajouter un
  `IMemoryCache` Singleton applicatif consulté par `MessageRepository.GetLocalizedMessage` avant le
  `MessageManager`, sans modifier ce dernier (framework). Sûr entre utilisateurs : le contenu d'un
  `messageId` est global. *(RPT-20590)*
- **Métadonnées RTM en lot, 100 % C#.** `factory.Entities.GetBrowser<ReportMetadata>()` +
  `AddCondition(Name, FilterOperation.In, names)` + `GetAllObjects()` ; aucune modification C++
  nécessaire. Préférer cette variante à N `InvokeMethod("GetMetadataForReport", name)` en boucle.
  **Piège `TEXTSIZE`** : ce chemin ne fait pas le `SET TEXTSIZE 2000000` du chemin mono-rapport et peut
  tronquer `META_DATA` à 32768 → garder un repli par rapport pour toute métadonnée qui atteint la
  limite. *(RPT-20590, `IReportMetadataRepository.GetMetadataForReports`)*
- **Patron de cache `IMemoryCache` en lot, anti-rafale** (modèle : `ReportMetadataCache.GetOrLoadMany`) :
  dédoublonner les clés (`HashSet`, ordre premier-vu) ; un verrou par clé, acquis dans un ordre stable
  `StringComparer.Ordinal` ; `Monitor.Enter(gate, ref taken)` et n'enregistrer le verrou que si
  `taken` ; revérifier le cache sous le verrou ; `finally` qui ne libère que les verrous réellement
  pris ; ne jamais cacher `null` ; cacher la donnée brute immuable. Les métadonnées se cachent entre
  requêtes ; **jamais les prefs**, qui dépendent de l'utilisateur. *(RPT-20590)*

## Observabilité

- **Base existante, ne pas repartir de zéro** : Serilog (avec TraceId/SpanId et `GenerationId` en
  contexte), `prometheus-net` sur `/metrics` (métriques ASP.NET seulement, aucune métrique métier), et
  le paquet interne `Croesus.OpenTelemetry.Tracing` câblé par `ConfigureCommonCroesusApi`.
- **Un span manuel doit venir d'une `ActivitySource` nommée exactement comme l'`AppName`**
  (`"ReportManagerApi"`), sinon il est écarté en silence. Utiliser la source partagée
  `Telemetry.Source` (`ReportManagerAPI.Domain/Observability/Telemetry.cs`). Le traçage n'est actif
  qu'avec `CROESUS_TELEMETRY=1` : `StartActivity` renvoie `null` sinon, toujours écrire `activity?.`.
  Poser les spans dans la couche service (le span serveur HTTP existe déjà), avec des tags de
  comptage à faible cardinalité, pas des identifiants. *(RPT-19587)*
- **Export OTLP/gRPC** vers `CF_OPENTELEMETRY_ENDPOINT` (défaut `http://localhost:4317`). ReportManagerApi
  tourne **dans le conteneur `croesus`** : depuis celui-ci, viser `http://host.docker.internal:4317`
  pour atteindre le Tempo de l'hôte, sinon rien n'arrive et rien ne le signale. *(2026-08-03)*
- **gRPC natif (`Grpc.Core`) : aucune auto-instrumentation.** Pour relier une trace à travers le
  spooler ou le FrameworkServer, il faut un intercepteur client qui injecte le contexte W3C dans les
  `Metadata` et un intercepteur serveur qui l'extrait (référence :
  `FrameworkServer…TraceContextServerInterceptor`). *(RPT-19587)*
- **Sybase (`AdoNetCore.AseClient`) : aucune auto-instrumentation SQL.** `AddSqlClientInstrumentation()`
  ne se déclenche pas sur ce pilote ; les spans SQL viennent d'un décorateur `DbCommand` manuel
  (`Technologies/Observability/TracingDbCommand`). *(RPT-19587)*

## Faits de domaine

- **`ORDER_ENTRY` : paramètres issus du contexte, pas de la saisie.** Le rapport est déclenché par
  ThinGUI/JIM ; `S_REPORT_CONTEXT` (`PM/Foundations/BusinessLogic/Api/report_data_const.h`) porte
  `nRebalanceId`, `sSpecialSourceType` (MODEL / UMA / MANUAL_REBALANCE / INVEST_OBJECTIVE /
  PROJECTED_PORTFOLIO) et `sSpecialSourceValue` (id du modèle, MODEL seulement). Les VPF C++
  correspondantes sont dans `validation_hided.c` (`GetRebalanceId`, `GetPad`,
  `OrderEntryGetHidedReportSrc`, `OrderEntryConditionSelector`). Côté Xpert, ces valeurs doivent être
  reçues dans la requête de génération ou produites par des VPF dédiées. Faux amis qui ne viennent
  **pas** du contexte : `PARAM_IsOrderEntry`, `PARAM_MOD_Id`. *(RPT-20548)*
- **`PREF_USE_EXTERNAL_DOC_PATH`** choisit le chemin d'un document externe, pour les `SPECIAL_REPORT`
  uniquement : pref active **et** `RPM_V_Internal_File` non vide → `RPM_V_Internal_File`, sinon
  `RPM_V_File`. Trois sites de lecture, tous C++ (`validation_file.c`, deux dans
  `PM/Tools/ReportCommander/Src/task_manager.cpp`) ; rien dans `ReportServer` ni `CroesusClient`.
  *(spike pref-use-external-doc-path)*
- **`RPM_V_File` : Conseiller lit des triplets, Xpert écrit des paires.** Format Conseiller par locale :
  `LANG,cheminClient,cheminServeur`. Sur une valeur Xpert bilingue (`en-CA,a.pdf,fr-CA,b.pdf`), le
  parseur C++ perd le document français sans erreur ni log. Ne pas « corriger le format » à la légère :
  un 3e champ vide bascule `ParseFileInfo` en mode « package prédéfini », qui exige `CroesusWeb` dans
  le chemin. `RPM_V_Content` porte `{ContentId}|{nom}` ; on stocke le `ContentId`, jamais la clé S3.
  *(RPT-21649)*
