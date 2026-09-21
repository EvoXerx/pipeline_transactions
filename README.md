Etudiant : LA Dan-Michel, Mastère data engineering & IA
# Pipeline de transaction

Ce programme fabrique des fichiers CSV de transactions bancaires, les lit,
calcule des totaux, puis range tout dans une petite base de données (SQLite).
Il n'utilise que Python, plus `pytest` (tests) et `mypy` (vérification des types).

## Installation (PowerShell, à la racine du projet)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
```

## Utilisation

```powershell
py -m src.pipeline      
py -m pytest -v         
py -m mypy src tests    
```

On peut aussi donner deux chemins : `py -m src.pipeline [dossier_csv] [fichier_db]`.
À la fin, le programme renvoie `0` si tout s'est bien passé, `1` si au moins
un fichier a posé problème.

## Les fichiers du projet

- `src/generator.py` : fabrique 3 fichiers CSV de 5 transactions. Les données sont écrites dans le code, donc identiques à chaque fois.
- `src/loader.py` : lit un CSV et vérifie que chaque ligne est correcte.
- `src/processing.py` : les calculs (total envoyé par IBAN, par banque, total reçu par IBAN, repérage des montants au-dessus de 5000). Ces fonctions ne lisent aucun fichier et n'affichent rien.
- `src/database.py` : la base de données, l'enregistrement d'un fichier et les nouvelles tentatives.
- `src/pipeline.py` : fait tout, dans l'ordre.

Les montants sont des `Decimal` et non des `float` : les `float` font de
petites erreurs d'arrondi quand on additionne de l'argent (0,1 + 0,2 ne donne
pas exactement 0,3). En base, les montants sont gardés sous forme de texte pour
la même raison.

## Contenu de la base de données

- `processed_files` : la liste des fichiers déjà traités (hash, nom, date).
- `transactions` : toutes les transactions, avec une colonne `est_suspecte` (montant > 5000).
- `totals_sent_by_origin`, `totals_sent_by_bank`, `totals_received_by_iban` : les totaux calculés, une ligne par IBAN ou par banque et par fichier.

Chaque ligne est rattachée au fichier d'où elle vient.

## Que fait-on d'une ligne invalide ?

Choix retenu : **un seul défaut et le fichier entier est refusé.**

Une ligne est invalide si le montant n'est pas un nombre, si la date est illisible, ou s'il manque une colonne. Le programme
affiche alors le numéro de la ligne, n'enregistre rien de ce fichier, passe au
fichier suivant et renvoie `1` à la fin.

Pourquoi : c'est simple et cohérent avec la règle « un fichier passe en entier
ou pas du tout ». On ne se retrouve jamais avec la moitié d'un fichier en base.
C'est vérifié dans `tests/test_loader.py` et `tests/test_pipeline.py`.

## Éviter de traiter deux fois le même fichier

Chaque fichier reçoit un **hash SHA-256** : une sorte d'empreinte calculée à
partir de son contenu (même contenu = même hash). Ce hash est enregistré en
base. S'il y est déjà, le fichier est sauté.

Le nom du fichier ne suffit pas : deux fichiers de même nom peuvent avoir un
contenu différent (le second sera traité), et deux fichiers de noms différents
peuvent avoir le même contenu (le second sera ignoré).

L'enregistrement d'un fichier se fait en un seul bloc : si tout va bien on
valide, sinon on annule tout, comme si rien ne s'était passé.

## Étape 6 : que se passe-t-il quand ça échoue ?

Voici la sortie du programme avec un CSV dont une ligne contient `abc` comme
montant (les 3 fichiers corrects étaient déjà en base) :

```
IGNORÉ (déjà traité) transactions_01.csv
IGNORÉ (déjà traité) transactions_02.csv
IGNORÉ (déjà traité) transactions_03.csv
ÉCHEC transactions_04_invalide.csv : ligne 3 : montant non numérique
```

Le code de retour est `1`. Même la première ligne de ce fichier, pourtant
correcte, n'a pas été enregistrée (test :
`test_failure_returns_nonzero_and_leaves_clean_db`).

**Une erreur que mypy voit et que les tests ne voient pas.**
Dans `src/pipeline.py`, on remplace le chemin par défaut par `Path(42)` (un
nombre à la place d'un chemin). mypy dit :

```
src\pipeline.py:26: error: Argument 1 to "Path" has incompatible type "int"; expected "str | PathLike[str]"  [arg-type]
```

Pourtant tous les tests passent : ils lancent toujours le programme en lui
donnant les chemins, donc ils ne passent jamais par ce cas. Si on lance
`py -m src.pipeline` sans rien ajouter, le programme plante (`TypeError`).

Ce qu'on en retient :
- Les **tests** exécutent le code et vérifient les résultats, mais seulement pour les cas qu'on a pensé à tester.
- **mypy** lit tout le code sans l'exécuter et repère les incohérences de types, même dans un coin jamais testé. En revanche, il ne comprend pas la logique : un `>` écrit à la place d'un `>=` lui échappe.
- Les deux se complètent.

(Cette modification était juste un essai)

## Étape 7 : quand faut-il réessayer ?

Quand l'enregistrement en base échoue, il y a deux cas :

- **Cela vaut la peine de réessayer** : `sqlite3.OperationalError`, par exemple « database is locked ». La base est temporairement utilisée par quelqu'un d'autre. Dans un instant elle sera libre, et la même opération réussira.
- **Cela ne sert à rien de réessayer** : `sqlite3.IntegrityError` (une règle de la base n'est pas respectée : doublon, référence vers une ligne qui n'existe pas…) ou une donnée invalide. Le problème vient des données elles-mêmes : on aura la même erreur à chaque essai.

La différence : une erreur **passagère** (elle dépend du moment) contre une
erreur **permanente** (elle dépend de ce qu'on essaie d'enregistrer).

`insert_with_retry` (dans `src/database.py`) réessaie jusqu'à 3 fois, avec 0,5
seconde d'attente, quand la base est occupée (`OperationalError`). Les autres
erreurs ne sont pas réessayées. Comme un essai raté est entièrement annulé,
réessayer ne risque pas de créer de doublons.

Tests (`tests/test_database.py`) : une erreur « base verrouillée » simulée,
suivie d'un succès à la deuxième tentative, et une `IntegrityError` qui n'est
pas réessayée.
