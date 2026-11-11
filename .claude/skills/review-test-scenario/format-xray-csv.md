# Livrable : CSV d'import Xray

Les pas de test d'un ticket de type **Test (Xray)** ne sont pas un champ Jira et ne sont donc pas
modifiables par le MCP (voir [`maj-jira.md`](maj-jira.md)). Le scénario révisé est livré en CSV, que
l'utilisateur importe lui-même depuis le **Test Case Importer** d'Xray.

Deux fichiers, deux usages — produire **les deux** :

| Fichier | Usage |
|---|---|
| `<ticket>-revise.csv` | lecture humaine, revue d'équipe, comparaison avec l'original. Mêmes colonnes que le scénario d'entrée. |
| `<ticket>-xray-import.csv` | import machine dans Xray. Format ci-dessous. |

---

## Format

Une ligne par pas de test.

| Colonne | Contenu |
|---|---|
| `Issue Key` | la clé du ticket, répétée sur **chaque** ligne — rattache les pas au test existant |
| `Test Case Identifier` | la clé du ticket, répétée — regroupe les lignes en un seul test |
| `Summary` | le résumé du ticket, sur la **première ligne seulement** (l'importeur retient la première valeur non vide) |
| `Action` | l'action du pas |
| `Data` | la colonne « Données » du scénario |
| `Result` | le résultat attendu |

```csv
Issue Key,Test Case Identifier,Summary,Action,Data,Result
RPT-00000,RPT-00000,Résumé du test,"Première action","Données","Résultat attendu"
RPT-00000,RPT-00000,,"Deuxième action","Données","Résultat attendu"
```

Les **préconditions ne vont pas dans ce fichier** : elles vivent dans la description du ticket, mise à
jour à l'étape 8. Proposer un second fichier au format *Precondition* seulement si l'utilisateur le
demande.

---

## Contraintes à respecter à l'écriture

- **UTF-8 sans BOM**, fins de ligne LF. Les accents sont partout dans ces scénarios.
- **Aplatir les cellules multi-lignes** : remplacer les sauts de ligne internes par ` / `. Un saut de
  ligne dans une cellule est légal en CSV mais passe mal dans certains importeurs.
- Guillemets doubles autour de toute cellule contenant une virgule, un guillemet, un `;` ou un `>`.
- Mêmes **références de jeux de données** (`CFG-SUCC-A`…) que dans le document de revue et le ticket.

## Vérification avant livraison

Valider la structure plutôt que de la supposer :

```bash
python -c "
import csv, io
rows=list(csv.reader(io.open('<fichier>',encoding='utf-8')))
print('pas de test:',len(rows)-1)
bad=[(i+1,len(r)) for i,r in enumerate(rows) if len(r)!=len(rows[0])]
print('lignes bancales:', bad if bad else 'aucune')
d=open('<fichier>','rb').read()
print('BOM:', d[:3]==b'\xef\xbb\xbf', '| CRLF:', d.count(b'\r\n'))
"
```

Attendu : aucune ligne bancale, pas de BOM, pas de CRLF, et un nombre de pas égal au nombre d'étapes du
scénario révisé.

## Ce qu'il faut dire à l'utilisateur en livrant

1. **Le mapping à l'écran fait foi** : l'importeur Xray fait associer chaque colonne à un champ. Si
   `Issue Key` n'est pas proposé, c'est que l'importeur **crée** des tests au lieu de mettre à jour
   l'existant — supprimer cette colonne et vérifier qu'on ne génère pas un doublon du ticket.
2. **Ne pas ouvrir/ré-enregistrer le fichier dans Excel** avant l'import : Excel le relit en ANSI et
   casse les accents. Pour le relire : « Données > À partir d'un fichier texte », encodage UTF-8.
3. Rappeler quelles cellules multi-lignes ont été aplaties, s'il y en a.
