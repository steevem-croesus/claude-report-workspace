# Comment corriger un bug

Objectif : corriger un défaut via le workflow `bug`, qui impose une règle stricte :

> **Aucune correction n'est shippée sans une reproduction et un test de régression** qui échoue *avant* la correction et passe
> *après*. Le diagnostic est obligatoire et distinct de la correction — on ne rustine pas les symptômes.

**Prérequis :** un rapport de bug ou une clé Jira décrivant un comportement erroné/cassé.

## Étapes

1. **Invoquez-le.** `/bug <symptôme ou clé Jira>` — p. ex. `/bug RPT-12345` ou `/bug the year-to-date
   parameter returns last year's start date for January reports`.

2. **Contexte.** `context-gatherer` capture le rapport, les étapes de repro et toute PR liée → `context.md`.

3. **Reproduire — cela vient avant le diagnostic.** Claude établit une reproduction, en préférant un
   **test qui échoue** qui capture le défaut ; sinon des étapes de repro documentées. Le statut est consigné dans
   `bug-diagnosis.md` comme reliable / intermittent / not-yet-reproduced.
   - S'il **ne peut pas** reproduire, il s'arrête et vous demande (via une invite) plus de détails ou la permission de
     poursuivre sur la meilleure preuve disponible — il ne rustine pas aveuglément.

4. **Diagnostiquer.** `investigator` travaille les preuves (code, `git log`/`git blame`, tickets, logs), forme
   des hypothèses, les réfute de façon adversariale, et ajoute la **cause racine + confiance** à
   `bug-diagnosis.md`. Il distingue le *déclencheur* de la *cause* sous-jacente.

5. **Planifier la correction.** `planner` écrit un `plan.md` minimal, cadré sur la correction, dont la section Tests **inclut
   le test de régression**. La même [barre de build](pass-the-plan-gate.md) s'applique au gate de plan — les petites
   corrections passent vite la revue du plan, mais la barre tient toujours à moins que vous ne la surchargiez explicitement.

6. **Construire la correction.** `implementer` (ou [`cpp-to-csharp-porter`](port-cpp-to-csharp.md) si la correction est
   dans un port) écrit la correction **et** le test de régression, puis construit et exécute les tests.

7. **Vérifier + review.** Claude ré-exécute le test/repro qui échouait pour confirmer qu'il a disparu, puis `reviewer`
   vérifie le diff — et spécifiquement que le test de régression couvre la **cause racine, pas seulement le
   symptôme**. Gate de code : **approve / request changes / cancel** (changes reboucle, plafond 3).

8. **Ship (optionnel)** et **rétrospective.** `retro.md` **doit** consigner la *classe* de cause racine pour que
   des bugs similaires soient attrapés plus tôt la prochaine fois. Approuvez les apprentissages proposés que vous voulez garder.

## Pièges courants

- **Sauter la reproduction parce que « la cause est évidente ».** Le workflow ne vous le permettra pas — et les causes
  « évidentes » sont souvent le déclencheur, pas la cause racine.
- **Un test de régression qui passe même sans la correction.** Le reviewer le signale ; le test doit échouer
  avant la correction.
- **Confondre ceci avec [`investigate`](../reference/workflows.md#6-investigate).** Si vous voulez seulement
  *comprendre* pourquoi quelque chose est arrivé sans le corriger, utilisez `investigate`.

## Référence

- Table des phases : [Référence : workflows §2](../reference/workflows.md#2-bug)
- La spécification complète du skill : [`.claude/skills/bug/SKILL.md`](../../.claude/skills/bug/SKILL.md)
