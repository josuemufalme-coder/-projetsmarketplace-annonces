# Cahier des charges — Kongo Market (MVP)

**Version :** 0.1 — 21 juillet 2026
**Statut :** Brouillon à valider par le fondateur
**Document :** Spécification des exigences logicielles (SRS) du produit minimum viable

---

## 1. Contexte et vision

### 1.1 Le produit

Kongo Market est une plateforme web de petites annonces entre particuliers
(et, à terme, professionnels) en République Démocratique du Congo. Elle met
en relation vendeurs et acheteurs autour de biens et services du quotidien :
immobilier, véhicules, électronique, mode, emploi, services, maison.

### 1.2 La vision

Devenir la référence nationale des petites annonces en RDC, sur le modèle
d'Avito (Russie) ou d'OLX (marchés émergents) : un lieu unique, gratuit à
l'entrée, où toute la population peut acheter, vendre et proposer des
services en confiance.

### 1.3 Le point de départ

- **Ville de lancement :** Kinshasa.
- **Principe fondateur :** la ville est une donnée structurée de la
  plateforme dès le premier jour. Kinshasa n'est jamais codée en dur ;
  l'ajout de Lubumbashi, Goma, Matadi ou toute autre ville se fait par
  simple ajout d'une entrée en base de données, sans redéveloppement.
- **Modèle économique au lancement :** 100 % gratuit pour tous les
  utilisateurs. Aucun paiement intégré dans le MVP. L'architecture doit
  néanmoins laisser la porte ouverte aux futures sources de revenus
  (voir §8).

### 1.4 Contexte d'usage

- La majorité des visites se fera depuis un téléphone mobile, souvent sur
  des connexions lentes ou intermittentes et des forfaits data limités.
- Le paiement mobile (M-Pesa, Orange Money, Airtel Money) est répandu mais
  volontairement exclu du MVP.
- Le public est multilingue : français (langue administrative et par
  défaut), lingala (langue véhiculaire de Kinshasa), anglais.

---

## 2. Utilisateurs cibles

| Profil | Description | Besoin principal |
|---|---|---|
| **Visiteur** | Toute personne naviguant sans compte | Chercher, filtrer, consulter des annonces et contacter un vendeur (si numéro affiché) sans aucune barrière |
| **Acheteur inscrit** | Visiteur ayant créé un compte | Contacter les vendeurs par messagerie interne, laisser des avis |
| **Vendeur** | Utilisateur inscrit et vérifié par SMS | Publier, gérer, renouveler ses annonces ; être joignable selon le mode de contact qu'il a choisi |
| **Administrateur** | Le fondateur (et plus tard une équipe de modération) | Traiter les signalements, retirer les annonces problématiques, gérer les référentiels (villes, catégories) |

Personas indicatifs à Kinshasa : une commerçante de Gombe qui vend des
téléphones reconditionnés ; un particulier de Lemba qui cherche un
appartement à louer ; un mécanicien de Masina qui propose ses services ;
un étudiant qui revend son ordinateur portable.

---

## 3. Fonctionnalités par module

### 3.1 Comptes et authentification

- **Navigation libre :** la consultation, la recherche et le filtrage des
  annonces sont accessibles sans compte, sans inscription, sans mur de
  connexion.
- **Inscription :** requise pour publier une annonce, utiliser la
  messagerie interne et laisser un avis.
- **Vérification par SMS :** obligatoire avant la première publication
  d'annonce. Un code à usage unique est envoyé au numéro de téléphone
  déclaré ; le compte passe alors au statut « vérifié ».
- **Profil utilisateur :** nom d'affichage, ville, photo facultative,
  date d'inscription, note moyenne et avis reçus (voir §3.6).
- **Rôles :** `utilisateur` et `administrateur` dans le MVP. Le champ rôle
  est extensible (futur badge « vendeur professionnel », modérateurs).

### 3.2 Villes et localisation

- Référentiel de villes en base de données, administrable sans
  déploiement. Chaque ville a un statut `active` / `inactive` : seules les
  villes actives apparaissent dans les formulaires et filtres.
- Au lancement, une seule ville active : Kinshasa.
- Chaque annonce est rattachée à une ville obligatoire. Le profil
  utilisateur porte aussi une ville.
- Le filtre par ville est présent dans la recherche dès le MVP (même s'il
  n'a qu'une valeur au départ), pour que l'expérience multi-villes soit
  déjà en place le jour où une deuxième ville est activée.

### 3.3 Catégories et annonces

**Catégories au lancement** (toutes disponibles dès le premier jour) :

1. Immobilier
2. Véhicules
3. Électronique & Téléphones
4. Habits & Mode
5. Emploi
6. Services
7. Maison & Jardin
8. Autres

**Champs communs à toute annonce :**

- Titre, description, catégorie, ville
- Prix : montant + devise (**USD ou CDF**, au choix du vendeur ; pas de
  conversion automatique dans le MVP)
- Photos (voir question ouverte Q7 sur le nombre et les limites)
- Mode de contact choisi par le vendeur (voir §3.5)
- Dates de publication et d'expiration, statut

**Champs spécifiques par catégorie** (exemples, liste exacte à valider) :

| Catégorie | Champs spécifiques envisagés |
|---|---|
| Immobilier | Type de bien (maison, appartement, parcelle, bureau), transaction (vente / location), surface (m²), nombre de pièces |
| Véhicules | Type (voiture, moto, camion), marque, modèle, année, kilométrage, carburant, boîte de vitesses |
| Électronique & Téléphones | Type d'appareil, marque, état (neuf / occasion) |
| Habits & Mode | Type d'article, taille, état, genre |
| Emploi | Type de contrat, secteur, niveau d'expérience — offre ou demande d'emploi |
| Services | Type de service, zone d'intervention |
| Maison & Jardin | Type d'article, état |
| Autres | Aucun champ spécifique |

Ces champs sont **structurés** (pas du texte libre dans la description) afin
d'alimenter les filtres de recherche par catégorie. Le modèle de données
doit permettre d'ajouter un champ à une catégorie sans migration lourde
(voir §4).

**Cycle de vie d'une annonce :**

```
brouillon (facultatif) → publiée → expirée (30 jours)
                            │            │
                            │            └─ renouvelée en 1 clic → publiée (30 jours de plus)
                            ├─ retirée par le vendeur (vendu / plus disponible)
                            └─ retirée par un administrateur (suite à modération)
```

- **Expiration automatique :** 30 jours après publication. L'annonce
  expirée n'apparaît plus dans la recherche mais reste visible dans
  l'espace du vendeur.
- **Renouvellement :** bouton « renouveler » en un clic depuis l'espace
  vendeur, qui republie l'annonce pour 30 jours.
- Le vendeur peut modifier ou retirer son annonce à tout moment.

### 3.4 Recherche et navigation

- Page d'accueil : annonces récentes, accès par catégorie, barre de
  recherche.
- Recherche par mots-clés sur titre et description.
- Filtres : catégorie, ville, fourchette de prix **par devise**, champs
  spécifiques de la catégorie sélectionnée (ex. : nombre de pièces en
  immobilier, marque en véhicules).
- Tri : plus récentes d'abord (par défaut), prix croissant / décroissant
  au sein d'une devise (voir question ouverte Q4).
- Pages d'annonce accessibles par URL publique partageable (WhatsApp étant
  un canal de diffusion majeur à Kinshasa).

### 3.5 Mise en relation acheteur / vendeur

Au moment de la publication, le vendeur choisit **un** des deux modes :

1. **Numéro affiché :** son numéro de téléphone apparaît sur l'annonce ;
   tout visiteur (même sans compte) peut l'appeler ou le contacter hors
   plateforme.
2. **Messagerie interne uniquement :** le numéro est masqué ; le contact
   passe par la messagerie de Kongo Market, qui nécessite un compte côté
   acheteur.

**Messagerie interne (MVP) :**

- Conversations rattachées à une annonce (un fil par couple
  acheteur / annonce).
- Boîte de réception avec compteur de messages non lus.
- Pas de pièces jointes dans le MVP ; texte uniquement.
- Notification des nouveaux messages : voir question ouverte Q5.

### 3.6 Profils vendeurs, avis et notation

- Chaque utilisateur a un profil public listant ses annonces actives.
- **Avis :** un acheteur peut laisser sur le profil d'un vendeur une note
  en étoiles (1 à 5) accompagnée d'un commentaire textuel, après un
  contact.
- **Note moyenne** affichée sur le profil et rappelée sur chaque annonce
  du vendeur.
- Un même acheteur ne peut laisser qu'un avis par vendeur (modifiable),
  pour limiter le spam de notation.
- Les conditions exactes ouvrant le droit de laisser un avis (comment
  vérifier qu'il y a eu « contact » ?) sont à trancher : voir question
  ouverte **Q1**, la plus structurante du document.

### 3.7 Signalement et modération

- **Bouton « Signaler »** sur chaque annonce, accessible à tous (y compris
  visiteurs sans compte), avec un motif à choisir (arnaque présumée,
  contenu illicite, doublon, mauvaise catégorie, autre) et un commentaire
  libre facultatif.
- Les signalements alimentent une **file de revue** dans l'interface
  d'administration. Un administrateur examine chaque signalement et
  décide : rejeter le signalement, retirer l'annonce, ou (cas graves)
  suspendre le compte du vendeur.
- **Pas de modération automatique** (filtrage par mots-clés, IA) dans le
  MVP — décision assumée, à réévaluer avec le volume.
- Les annonces sont publiées **immédiatement**, sans validation préalable
  (modération a posteriori uniquement) — à confirmer, voir question
  ouverte Q2.
- Toute action de modération est journalisée (qui, quoi, quand, motif).

### 3.8 Administration

Interface réservée aux administrateurs :

- File des signalements avec actions (rejeter, retirer l'annonce,
  suspendre le compte).
- Gestion des référentiels : villes (ajout / activation), catégories et
  leurs champs spécifiques.
- Recherche d'utilisateurs et d'annonces ; suspension / réactivation de
  comptes.
- Tableau de bord minimal : nombre d'annonces publiées, d'inscriptions,
  de signalements en attente.

### 3.9 Internationalisation (i18n)

- Interface disponible en **français (défaut), lingala et anglais** dès le
  lancement, avec un sélecteur de langue persistant.
- Tous les textes d'interface passent par un système de traduction
  (fichiers de ressources par langue) ; **aucune chaîne en dur** dans le
  code. Les référentiels administrables (noms de catégories, motifs de
  signalement) sont également traduisibles.
- Le **contenu des annonces n'est pas traduit** : il s'affiche dans la
  langue où le vendeur l'a rédigé.
- L'ajout d'une quatrième langue (swahili, tshiluba, kikongo — pertinent
  pour l'expansion nationale) ne doit demander que l'ajout d'un fichier de
  traduction.

---

## 4. Modèle de données à haut niveau

Entités principales et relations (niveau conceptuel, pas un schéma SQL
définitif) :

```
Ville ──< Utilisateur ──< Annonce >── Catégorie
                │            │              │
                │            ├──< Photo     └──< DéfinitionDeChamp
                │            ├──< ValeurDeChamp (par annonce)
                │            ├──< Signalement
                │            └──< Conversation ──< Message
                └──< Avis (émis et reçus)
```

| Entité | Attributs clés | Notes |
|---|---|---|
| **Ville** | nom, statut actif/inactif | Référentiel administrable ; jamais de ville en dur dans le code |
| **Utilisateur** | téléphone (identifiant de connexion), nom d'affichage, ville, rôle, statut de vérification SMS, statut du compte (actif / suspendu) | Le rôle est extensible (futur badge pro) |
| **Catégorie** | nom (traduisible), ordre d'affichage | Les 8 catégories du lancement |
| **DéfinitionDeChamp** | catégorie, nom, type (texte, nombre, liste de valeurs), obligatoire ou non | Permet d'ajouter un champ à une catégorie sans migration lourde (modèle attributs dynamiques ou colonne JSON) |
| **Annonce** | titre, description, catégorie, ville, prix, **devise (USD/CDF)**, mode de contact, statut, date de publication, date d'expiration | L'expiration = publication + 30 jours ; le renouvellement repousse la date |
| **ValeurDeChamp** | annonce, définition de champ, valeur | Valeurs des champs spécifiques |
| **Photo** | annonce, fichier, ordre | Stockage objet + variantes redimensionnées |
| **Conversation / Message** | annonce, participants ; expéditeur, texte, lu/non-lu | Un fil par couple acheteur-annonce |
| **Avis** | auteur, vendeur visé, note 1–5, commentaire, date | Un avis par couple acheteur-vendeur |
| **Signalement** | annonce, auteur (nullable si visiteur), motif, statut de traitement, administrateur, décision | Alimente la file de modération |
| **JournalModération** | administrateur, action, cible, motif, date | Traçabilité des actions admin |

**Prévu dans le schéma mais inactif dans le MVP** (voir §8) : champs de
mise en avant sur l'annonce (`premium_jusqu_au`, nullable), rôle
« vendeur professionnel », table d'emplacements publicitaires. Ces éléments
sont *réservés* dans la conception, **pas développés**.

---

## 5. Contraintes techniques

### 5.1 Plateforme

- **Site web responsive uniquement** : utilisable confortablement du
  téléphone bas de gamme à l'ordinateur de bureau. Pas d'application
  mobile native dans le MVP.
- Conception **mobile-first** : la majorité du trafic attendu est mobile.

### 5.2 Performance et réseau (contexte RDC)

- Pages légères : images compressées et redimensionnées côté serveur,
  chargement différé (lazy loading), poids de page minimal.
- La plateforme doit rester utilisable sur une connexion 3G instable.
- URLs publiques propres et partageables (WhatsApp, réseaux sociaux) avec
  aperçus (métadonnées Open Graph).

### 5.3 Sécurité et intégrité

- Envoi de SMS via un fournisseur couvrant les opérateurs congolais
  (Vodacom, Airtel, Orange, Africell) — choix du fournisseur : question
  ouverte Q3.
- Limitation de débit (rate limiting) sur : envoi de codes SMS, création
  d'annonces, envoi de messages, dépôt de signalements — protection de
  base contre le spam même sans modération automatique.
- Données personnelles : le numéro de téléphone n'est jamais exposé
  publiquement sauf choix explicite du vendeur sur une annonce donnée.
- Sauvegardes régulières de la base de données.

### 5.4 Extensibilité (contraintes d'architecture, sans développement MVP)

- Aucune valeur métier codée en dur : villes, catégories, champs par
  catégorie, motifs de signalement et durée de vie des annonces (30 jours)
  sont des données ou de la configuration.
- Le modèle utilisateur et le modèle annonce réservent les emplacements
  nécessaires aux évolutions payantes (§8) sans les implémenter.

### 5.5 Choix de pile technique

Volontairement **non figés dans ce document** : le choix du langage, du
framework, de la base de données et de l'hébergement fera l'objet d'une
décision dédiée à l'étape suivante, une fois ce cahier des charges validé.

---

## 6. Hors périmètre du MVP

Explicitement exclus de la première version :

- Application mobile native (iOS / Android) et notifications push.
- Tout paiement intégré : mise en avant payante, abonnements, mobile money.
- Conversion automatique USD ↔ CDF et affichage multi-devises d'un même
  prix.
- Modération automatique (mots-clés, détection d'images, IA).
- Traduction automatique du contenu des annonces.
- Badge « vendeur professionnel » et comptes boutique.
- Espaces publicitaires.
- Géolocalisation fine (carte, rayon de recherche) — la localisation du
  MVP est la ville (et éventuellement la commune, voir Q6).
- Enchères, panier, commande en ligne, livraison.
- Villes autres que Kinshasa *activées* (le support multi-villes existe,
  seule Kinshasa est active).

---

## 7. Incohérences et questions ouvertes

Points identifiés à la relecture des décisions — **à trancher avant ou
pendant la conception détaillée**, classés par importance.

### Q1 — Qui a le droit de laisser un avis ? *(structurant)*

La décision dit : avis « laissés par les acheteurs **après contact** ».
Or, quand le vendeur choisit d'afficher son numéro, le contact se fait
**hors plateforme** (appel, WhatsApp) : Kongo Market n'a aucun moyen de
savoir qu'il a eu lieu. Trois options :

- **(a)** Avis réservés aux acheteurs ayant échangé via la messagerie
  interne → avis fiables, mais les vendeurs « numéro affiché » (sans doute
  la majorité) ne recevraient presque jamais d'avis ;
- **(b)** Tout utilisateur connecté peut noter n'importe quel vendeur →
  couverture maximale, mais porte ouverte aux faux avis (positifs comme
  malveillants) ;
- **(c)** Intermédiaire : avis ouvert à tout utilisateur connecté **ayant
  déclenché une action de contact tracée sur la plateforme** (clic sur
  « afficher le numéro », qui est alors journalisé, ou message interne).

**Recommandation : (c)** — elle couvre les deux modes de contact tout en
exigeant une trace d'intention réelle. À valider.

### Q2 — Publication immédiate ou validation préalable ?

La décision de modération ne parle que des **signalements**. Ce document
suppose que les annonces sont **publiées immédiatement** et modérées a
posteriori (§3.7). Alternative : faire valider chaque annonce par
l'administrateur avant publication — qualité maximale, mais goulot
d'étranglement intenable pour une seule personne dès que le volume monte.
**Recommandation : publication immédiate.** À confirmer.

### Q3 — Vérification SMS : coût et fournisseur *(risque opérationnel)*

La plateforme est gratuite pour les utilisateurs, mais **chaque SMS de
vérification a un coût pour toi**, et c'est la seule barrière à l'entrée
des vendeurs. À instruire avant le développement : choix d'un fournisseur
fiable en RDC (Africa's Talking, Twilio, agrégateur local…), coût
unitaire, budget mensuel estimé, et comportement de secours si le SMS
n'arrive pas (renvoi limité, appel vocal ?). Risque à documenter : des
échecs de délivrance SMS bloqueraient toute nouvelle publication.

### Q4 — Deux devises sans conversion : tri et filtres de prix

Sans taux de conversion, il est impossible de trier ou filtrer par prix
une liste mêlant USD et CDF. Ce document retient l'approche : **fourchette
de prix et tri par prix ne s'appliquent qu'au sein d'une devise choisie**
(« Prix en USD entre … et … »). Conséquence assumée : un acheteur qui
filtre en USD ne voit pas les annonces équivalentes en CDF. À valider.

### Q5 — Notification des messages internes *(risque produit)*

Sans application mobile ni push, un vendeur « messagerie uniquement »
n'apprend l'existence d'un message qu'en revenant sur le site → risque
fort de messages sans réponse, décourageant pour les acheteurs. Options :
notification par e-mail (mais l'e-mail est peu utilisé par la cible),
notification par SMS (coût par message, cf. Q3), ou rien dans le MVP en
assumant le risque. **À trancher — aucune option par défaut retenue.**

### Q6 — Granularité de la localisation à Kinshasa

Avec une seule ville active, le filtre « ville » ne discrimine rien au
lancement. Kinshasa est immense : la **commune** (Gombe, Lemba, Masina,
Ngaliema…) est probablement le vrai critère de proximité pour les
utilisateurs. Faut-il un champ « commune / quartier » structuré sous la
ville dès le MVP ? Coût faible maintenant, coûteux à rattraper plus tard.
**Recommandation : oui, prévoir le niveau commune dès le départ.**

### Q7 — Les photos ne figurent pas dans les décisions

Aucune décision ne mentionne les photos, pourtant essentielles à une
plateforme d'annonces. Ce document les suppose incluses (§3.3). À
préciser : nombre maximal par annonce (proposition : 6), taille maximale,
photo obligatoire ou non selon la catégorie (une annonce immobilière sans
photo a peu de valeur ; une offre d'emploi n'en a pas besoin).

### Q8 — La catégorie Emploi cadre mal avec le modèle « prix »

Une offre d'emploi n'a pas de « prix » ; un salaire ne se déclare pas
comme le prix d'un téléphone. De même, beaucoup de services sont « à
négocier ». Proposition : rendre le prix **facultatif** avec une mention
« Prix à discuter », et pour l'Emploi, un champ salaire facultatif
distinct. À valider — sinon, le champ prix obligatoire produira des
valeurs absurdes (0, 1…).

### Q9 — Numéros affichés : exposition au démarchage

Les numéros affichés publiquement sur les annonces peuvent être aspirés
par des robots (spam, arnaques ciblées). Mesure simple envisagée : masquer
le numéro derrière un clic « Afficher le numéro » (ce qui sert aussi la
traçabilité de Q1-option c) et bloquer l'indexation des numéros par les
moteurs de recherche. À valider.

### Q10 — Renouvellement et position dans les résultats

Le tri par défaut étant « plus récentes d'abord », que fait le
renouvellement : il remonte l'annonce en tête (incitation à renouveler,
mais risque d'annonces zombies remontées indéfiniment) ou il conserve la
date d'origine (annonces renouvelées invisibles en pratique) ?
**Recommandation : le renouvellement remonte l'annonce**, avec une limite
(ex. 3 renouvellements consécutifs sans modification). À valider.

---

## 8. Évolutions prévues (architecture prête, développement ultérieur)

Rappel des pistes de monétisation décidées, dont l'architecture tient
compte sans les développer :

1. **Mise en avant payante d'annonces** — champs réservés sur l'annonce,
   emplacement visuel prévu dans les listes.
2. **Badge vendeur professionnel** — extension du système de rôles.
3. **Espaces publicitaires** — zones prévues dans la maquette des pages.

S'y ajoutent naturellement, sans engagement : activation de nouvelles
villes, application mobile, paiement mobile money, modération assistée.

---

## 9. Suites de ce document

1. Validation du présent document et arbitrage des questions Q1 à Q10.
2. Choix de la pile technique et de l'hébergement (décision dédiée).
3. Maquettes des écrans clés (accueil, recherche, annonce, publication).
4. Découpage du développement en étapes testables une par une.
