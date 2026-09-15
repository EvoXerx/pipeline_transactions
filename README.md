# Pipeline de transactions financières

Un programme qui crée des transactions financières, les lit depuis des
fichiers CSV et les enregistre dans une base SQLite, sans pandas. Seules
dépendances : `pytest` et `mypy`.

## Installation

Depuis PowerShell, à la racine du projet :

"py -m venv .venv"
".venv\Scripts\Activate.ps1"
"py -m pip install -r requirements.txt"


## Tests et vérification des types

A faire sur powershell:
"py -m pytest -v"
"py -m mypy src tests"


## Organisation


`src/generator.py`   crée les fichiers CSV
`src/loader.py`      lit les fichiers
`src/processing.py`  calcule les totaux et repère les montants suspects
`src/database.py`    structure de la base et enregistrement des données
`tests/`             tests


## Création des CSV

A faire sur powershell:
"py -m src.generator"


Crée deux fichiers fixes de cinq transactions dans `data/input`.

## Lecture et calculs

`src/loader.py` lit un CSV et calcule un identifiant unique à partir de son
contenu, utilisé pour reconnaître un fichier déjà enregistré. `src/processing.py`
regroupe des fonctions qui ne font que des calculs, sans lire de fichier ni
rien afficher : total envoyé par IBAN origine, total envoyé par banque, total
reçu par IBAN, et repérage des montants au-dessus de 5000.

## Structure de la base

`processed_files` : identifiant du fichier, nom d'origine et date d'enregistrement.
`transactions` : transactions lues, avec l'indicateur `est_suspecte`.
`totals_sent_by_origin` : montants envoyés par IBAN origine, par fichier.
`totals_sent_by_bank` : montants envoyés par banque, par fichier.
`totals_received_by_iban` : montants reçus par IBAN destinataire, par fichier.

Chaque table de résultats est liée à `processed_files`.

## Enregistrement en base

`insert_batch` enregistre un lot de fichiers d'un coup : si quelque chose
échoue en cours de route, rien n'est enregistré, pas même une partie. Un
fichier déjà présent dans `processed_files` est ignoré, ce qui évite de
l'enregistrer deux fois même en le relançant.
