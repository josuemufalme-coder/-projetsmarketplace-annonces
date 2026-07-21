# Recette manuelle du MVP — Kongo Market

Scénario de test pas à pas pour vérifier tout le parcours utilisateur.
À dérouler en local avant la mise en ligne, puis à nouveau sur le site
public après le déploiement.

## 0. Préparer l'environnement

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py compilemessages     # traductions (nécessite gettext)
python manage.py charger_demo        # 4 comptes + 12 annonces de démonstration
python manage.py createsuperuser     # TON compte administrateur (e-mail + mot de passe)
python manage.py runserver
```

Le site est sur http://127.0.0.1:8000/ — l'administration sur
http://127.0.0.1:8000/admin/.

**Comptes de démonstration** (mot de passe : `demo2026!`) :

| E-mail | Rôle dans le scénario |
|---|---|
| chantal@demo.cd | Vendeuse d'électronique (Gombe) |
| didier@demo.cd | Immobilier et véhicules (Lemba) |
| patrick@demo.cd | Mécanicien, mode « numéro affiché » (Masina) |
| grace@demo.cd | Mode & maison, mode « messagerie » (Limete) |

Les e-mails envoyés par le site (notifications, mot de passe oublié)
s'affichent **dans le terminal** où tourne `runserver` — c'est normal en
local.

## 1. Navigation sans compte (5 min)

1. Ouvre l'accueil : tu dois voir la barre de recherche, les 8 catégories
   et 8 annonces récentes avec photos. ✅ attendu : aucune demande de connexion.
2. Cherche « toyota » : la RAV4 apparaît.
3. Filtre par catégorie « Véhicules » puis commune « Masina » : seule la
   moto TVS reste.
4. Filtre par prix : devise USD, max 300 → l'iPhone (380 $) disparaît,
   l'ordinateur HP (260 $) reste.
5. Ouvre une annonce : photos, champs spécifiques (marque, année…),
   commune, description.
6. Change la langue (LN puis EN) en bas de page : l'interface change,
   le contenu des annonces reste dans sa langue d'origine.
7. Sur une annonce de Patrick : clique « Afficher le numéro » →
   tu es renvoyé vers la connexion (pas de numéro sans compte). ✅

## 2. Inscription et publication (10 min)

8. Crée TON compte (menu « Créer un compte ») : e-mail, nom, commune.
   ✅ attendu : connexion immédiate, sans SMS.
9. Clique « Publier une annonce » → choisis « Véhicules ».
10. Essaie de publier **sans photo** : refus avec message clair (photos
    obligatoires pour cette catégorie). ✅
11. Essaie **sans prix** ni « à discuter » : refus. Coche « Prix à
    discuter » ou mets un prix + devise. ✅
12. Complète (type, marque, année…), ajoute 1 à 6 photos, mode de
    contact « Numéro affiché », publie. ✅ attendu : l'annonce apparaît
    immédiatement sur l'accueil, en tête.
13. Va dans « Mes annonces » : ton annonce est là, avec sa date
    d'expiration (30 jours) et le bouton « Retirer ». Le bouton
    « Renouveler » n'apparaît pas (moins de 7 jours). ✅

## 3. Contact entre acheteur et vendeur (10 min)

14. Déconnecte-toi, connecte-toi avec `chantal@demo.cd`.
15. Ouvre ton annonce → « Afficher le numéro » : ton numéro apparaît.
    ✅ (ce clic est journalisé : il ouvrira le droit de laisser un avis).
16. Ouvre le « Téléviseur Samsung » de Chantal… tu es Chantal : pas de
    formulaire de contact sur sa propre annonce. ✅
17. Déconnecte-toi, connecte-toi avec `didier@demo.cd`, ouvre le
    téléviseur (mode messagerie) : envoie un message. ✅ attendu :
    fil de conversation créé + e-mail de notification dans le terminal.
18. Reconnecte-toi en `chantal@demo.cd` : badge « Messages (1) » dans
    l'en-tête → ouvre, réponds. ✅ le compteur disparaît après lecture.

## 4. Avis (5 min)

19. Toujours en `chantal@demo.cd` : ouvre le profil du vendeur de ton
    annonce (clique son nom sur l'annonce). Le formulaire d'avis est là
    (grâce au clic « Afficher le numéro » de l'étape 15). Note 5 étoiles
    + commentaire. ✅ la note moyenne s'affiche sur le profil.
20. Connecte-toi en `grace@demo.cd` (aucun contact avec toi) : sur ton
    profil, PAS de formulaire d'avis — message expliquant qu'il faut
    d'abord un contact. ✅

## 5. Signalement et modération (10 min)

21. Déconnecte-toi. Sans compte, ouvre une annonce → « Signaler cette
    annonce » → motif « Arnaque présumée » + commentaire. ✅
22. Connecte-toi sur /admin/ avec TON superutilisateur.
23. « Signalements » : ton signalement est « En attente ». Sélectionne-le
    → action « Suspendre l'annonce et marquer traité ». ✅
24. Retourne sur le site : l'annonce n'apparaît plus ; son vendeur la
    voit marquée « Suspendue par la modération » dans Mes annonces. ✅
25. Dans l'admin, republie-la (action « Republier l'annonce »). ✅
26. Toujours dans l'admin, regarde « Marques anti-spam » : publie depuis
    le site une annonce Véhicules à 10 $ → une marque AS7 (prix
    aberrant) apparaît, l'annonce reste en ligne. ✅
27. Essaie de republier deux fois la même annonce (même titre + même
    description) : refus à la deuxième. ✅

## 6. Robustesse (5 min)

28. « Mot de passe oublié ? » sur la connexion : saisis ton e-mail →
    le lien arrive dans le terminal → ouvre-le, change le mot de passe,
    reconnecte-toi. ✅
29. Ouvre une URL au hasard (ex. /xyz/) : page 404 propre. ✅
30. Vérifie /robots.txt et /sitemap.xml. ✅
31. Sur téléphone (même wifi : `python manage.py runserver 0.0.0.0:8000`
    puis http://IP-DU-PC:8000 — ajoute cette IP à DJANGO_ALLOWED_HOSTS
    si besoin) : refais les étapes 1 à 6. ✅

## En cas d'écart

Note le numéro de l'étape, ce que tu attendais et ce que tu as vu, et
transmets-le tel quel — chaque écart devient une correction à faire
avant la mise en ligne.
