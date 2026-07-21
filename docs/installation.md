# Installer Kongo Market sur son ordinateur (test en local)

Compte 20 à 30 minutes la première fois. Les commandes se tapent dans le
terminal (**PowerShell** sur Windows : menu Démarrer → taper « PowerShell »).

## 1. Installer Python

Télécharge Python 3.12 sur https://www.python.org/downloads/ et lance
l'installeur. **Important (Windows)** : coche « *Add python.exe to PATH* »
sur le premier écran avant de cliquer Install.

## 2. Installer Git

Télécharge Git sur https://git-scm.com/downloads et installe-le en
laissant les options par défaut.

## 3. Récupérer le code

```powershell
git clone https://github.com/josuemufalme-coder/-projetsmarketplace-annonces.git kongomarket
cd kongomarket
git checkout claude/confident-volta-8vhp95
```

La dernière ligne est importante : tout le code du MVP est sur cette
branche. Git ouvrira le navigateur pour la connexion GitHub la première fois.

## 4. Installer les dépendances

```powershell
pip install -r requirements.txt
```

Si Windows répond « pip n'est pas reconnu », utiliser
`py -m pip install -r requirements.txt` (et `py manage.py …` ensuite).

## 5. Préparer la base et les données de démonstration

```powershell
python manage.py migrate          # crée la base (communes + catégories incluses)
python manage.py charger_demo     # 12 annonces et 4 comptes de test
python manage.py createsuperuser  # TON compte administrateur
```

## 6. Lancer le site

```powershell
python manage.py runserver
```

- Site : http://127.0.0.1:8000
- Administration : http://127.0.0.1:8000/admin/
- Arrêter : `Ctrl + C` dans le terminal.

## 7. Dérouler la recette

Suivre `docs/recette.md` (31 vérifications pas à pas). Noter le numéro de
toute étape dont le résultat diffère de l'attendu.

## Bon à savoir

- **E-mails** : en local, les e-mails du site (messages, mot de passe
  oublié) s'affichent dans le terminal — aucun vrai e-mail ne part.
- **Traductions** : déjà compilées et incluses ; `compilemessages` n'est
  nécessaire que si l'on modifie les textes (et demande l'outil gettext).
- **Tester depuis un téléphone** (même wifi) :
  `python manage.py runserver 0.0.0.0:8000` puis ouvrir
  `http://ADRESSE-IP-DU-PC:8000` (ajouter cette adresse à
  `DJANGO_ALLOWED_HOSTS` si le site répond « Bad Request »).
- **Comptes de démonstration** (mot de passe `demo2026!`) :
  chantal@demo.cd, didier@demo.cd, patrick@demo.cd, grace@demo.cd.
