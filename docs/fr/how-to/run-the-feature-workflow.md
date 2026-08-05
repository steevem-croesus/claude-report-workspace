# Comment exécuter le workflow feature

Objectif : mener une nouvelle capacité (champ de rapport, endpoint, UI, changement d'API) d'un ticket à du code
fonctionnel et testé — et optionnellement jusqu'à une PR — via le playbook `feature` gaté.

**Prérequis :** une description de tâche ou une clé Jira ; Claude Code ouvert dans le workspace. Pas pour les défauts
(utilisez [`bug`](fix-a-bug.md)) ni la pure restructuration (utilisez `refactor`).

## Étapes

1. **Invoquez-le.** `/feature <ce que vous voulez construire>` — incluez la clé Jira s'il y en a une ; elle devient
   le slug de la tâche et tire automatiquement le contexte du ticket.

2. **Laissez le contexte + l'exploration s'exécuter.** `context-gatherer` écrit `context.md` ; `explorer` écrit
   `exploration.md`. Si Claude pose une question de clarification ici, répondez-y — il ne demande que quand une
   mauvaise supposition ferait dérailler le plan.

3. **Au gate de plan, lisez d'abord l'en-tête.** `plan.md` s'ouvre par `**Status:** … · **Grade:** …`.
   Vous ne pouvez approuver-pour-construire qu'un plan `ready` + **A/S** (la *barre de build*). S'il est sous la barre, voir
   [Comment faire passer un plan au gate](pass-the-plan-gate.md). Sinon choisissez **approve / request
   changes / cancel**.

4. **Laissez le build s'exécuter.** Pour une feature cross-repo, les builders s'exécutent en **ordre de pipeline** —
   analyse C++ → C#/API → UI Angular — un par tranche de repo nommée sous les
   sous-sections `#### <repo>` du plan. Chacun construit et exécute ses tests et écrit/met à jour `build-summary.md`.

5. **Au gate de code**, revoyez le verdict de `review-code.md`. Les constats must-fix → **request changes**
   (reboucle vers le build, plafonné à 3 tours). Propre → **approve**.

6. **Ship (optionnel).** Si vous dites oui, Claude crée une branche **par repo touché** (`--no-track` depuis une
   ref protégée), commit, `git push -u`, et ouvre une PR — en suivant les
   [règles git de l'organisation](../reference/gates-and-protocol.md#règles-de-branch-commit--ship). Dites non et rien
   n'est commité.

7. **Rétrospective.** `retro.md` propose des apprentissages durables et des mises à jour de docs sous forme de checklist. Approuvez
   ceux qui valent la peine d'être gardés — Claude n'écrira pas en mémoire ni n'éditera de docs sans qu'on le lui demande.

## Astuces

- **Le travail multi-repo reste sur des branches/PR séparées** — il n'y a pas de repo racine partagé. Chaque repo sous
  `repos/` est son propre repo git sur sa propre branche.
- **Déléguer à `code-fleet`.** Les phases build+review peuvent à la place être confiées à `/code-fleet:work`
  si vous préférez ses language packs ; les agents du workspace ajoutent la conscience de la topologie multi-repo et le
  `cpp-to-csharp-porter`. Voir [`workflows.md` → Relationship to code-fleet](../../../.claude/conventions/workflows.md).
- **Les ports de value-provider** à l'intérieur d'une feature sont gérés par
  [`cpp-to-csharp-porter`](port-cpp-to-csharp.md), pas par l'implementer générique.

## Référence

- Table des phases : [Référence : workflows §1](../reference/workflows.md#1-feature)
- Mécanique des gates : [Référence : gates & protocole](../reference/gates-and-protocol.md)
- La spécification complète du skill : [`.claude/skills/feature/SKILL.md`](../../../.claude/skills/feature/SKILL.md)
