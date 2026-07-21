# Cahier des charges — Kongo Market (MVP)

**Version :** 0.2 — 21 juillet 2026
**Statut :** Décisions fonctionnelles arbitrées par le fondateur (voir §7) — document de référence
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

- **Ville de lancement :** Kinshasa, avec la **commune** comme principal
  niveau de localisation et de recherche (Gombe, Lemba, Masina,
  Ngaliema…).
- **Principe fondateur :** la localisation (ville, commune) est une donnée
  structurée de la plateforme dès le premier jour. Kinshasa n'est jamais
  codée en dur ; l'ajout de Lubumbashi, Goma, Matadi ou de toute autre
  ville ou province se fait par simple ajout d'entrées en base de données,
  sans redéveloppement.
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
| **Visiteur** | Toute personne naviguant sans compte | Chercher, filtrer, consulter des annonces sans aucune barrière |
| **Acheteur inscrit** | Visiteur ayant créé un compte | Afficher le numéro d'un vendeur, contacter par messagerie interne, laisser des avis |
| **Vendeur** | Utilisateur inscrit | Publier, gérer, renouveler ses annonces ; être joignable selon le mode de contact qu'il a choisi |
| **Administrateur** | Le fondateur (et plus tard une équipe de modération) | Traiter les signalements et les annonces marquées par l'anti-spam, retirer les annonces problématiques, gérer les référentiels (villes, communes, catégories) |

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
- **Inscription :** requise pour publier une annonce, afficher le numéro
  d'un vendeur, utiliser la messagerie interne et laisser un avis.
- **Pas de vérification par SMS dans le MVP** (décision Q3) : la création
  de compte est immédiate, sans validation du numéro de téléphone.
  L'architecture réserve néanmoins un statut de vérification sur le compte
  (`non_verifie` par défaut) et isole l'étape d'inscription, afin que la
  vérification SMS puisse être ajoutée dans une version future sans
  modification majeure du système.
- **Identifiant de connexion :** adresse e-mail + mot de passe.
  L'e-mail est de toute façon requis pour les notifications de messagerie
  (décision Q5). Le numéro de téléphone n'est demandé qu'au moment où le
  vendeur publie une annonce en mode « numéro affiché ». *(Hypothèse de
  conception découlant des décisions Q3 et Q5 — à confirmer, voir §7bis.)*
- **Profil utilisateur :** nom d'affichage, commune/ville, photo
  facultative, date d'inscription, note moyenne et avis reçus (voir §3.6).
- **Rôles :** `utilisateur` et `administrateur` dans le MVP. Le champ rôle
  est extensible (futurs badge « vendeur professionnel », comptes Premium,
  modérateurs).
- **Protection anti-abus :** limitation de débit sur l'inscription et la
  publication (voir §5.3) — indispensable en l'absence de vérification
  SMS.

### 3.2 Localisation : villes et communes

- Référentiel géographique à deux niveaux en base de données,
  administrable sans déploiement : **Ville** (rattachable plus tard à une
  province) et **Commune** (subdivision d'une ville).
- Chaque ville a un statut `active` / `inactive` : seules les villes
  actives apparaissent dans les formulaires et filtres. Au lancement, une
  seule ville active : Kinshasa, avec son référentiel de communes.
- Chaque annonce est rattachée à une **commune** obligatoire (donc à une
  ville). Le profil utilisateur porte aussi une commune.
- **La commune est le principal critère de localisation dans la recherche
  au lancement** (décision Q6) : filtre par commune, affichage de la
  commune sur chaque annonce. Le filtre par ville existe dès le MVP et
  prendra son sens à l'activation d'une deuxième ville.
- L'ajout futur des provinces ne doit demander qu'une extension du
  référentiel (niveau au-dessus de la ville), pas une refonte.

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

- Titre, description, catégorie, commune (et donc ville)
- **Prix facultatif** (décision Q8) : soit un montant + devise (**USD ou
  CDF**, au choix du vendeur, sans conversion automatique dans le MVP),
  soit l'option « **Prix à discuter** » quand le vendeur ne souhaite pas
  afficher de montant fixe (offres d'emploi, services, prestations…)
- **Photos : jusqu'à 6 par annonce** (décision Q7). Les photos sont
  **obligatoires** (au moins une) pour les catégories où elles sont
  pertinentes — Immobilier, Véhicules, Électronique & Téléphones,
  Habits & Mode, Maison & Jardin — et facultatives pour Emploi, Services
  et Autres. Ce caractère obligatoire est un paramètre de la catégorie,
  pas une règle codée en dur. L'ajout de vidéos est prévu pour une version
  ultérieure.
- Mode de contact choisi par le vendeur (voir §3.5)
- Dates de publication et d'expiration, statut

**Champs spécifiques par catégorie** (exemples, liste exacte à valider) :

| Catégorie | Photos | Champs spécifiques envisagés |
|---|---|---|
| Immobilier | Obligatoires | Type de bien (maison, appartement, parcelle, bureau), transaction (vente / location), surface (m²), nombre de pièces |
| Véhicules | Obligatoires | Type (voiture, moto, camion), marque, modèle, année, kilométrage, carburant, boîte de vitesses |
| Électronique & Téléphones | Obligatoires | Type d'appareil, marque, état (neuf / occasion) |
| Habits & Mode | Obligatoires | Type d'article, taille, état, genre |
| Emploi | Facultatives | Type de contrat, secteur, niveau d'expérience — offre ou demande d'emploi ; salaire facultatif |
| Services | Facultatives | Type de service, zone d'intervention |
| Maison & Jardin | Obligatoires | Type d'article, état |
| Autres | Facultatives | Aucun champ spécifique |

Ces champs sont **structurés** (pas du texte libre dans la description) afin
d'alimenter les filtres de recherche par catégorie. Le modèle de données
doit permettre d'ajouter un champ à une catégorie sans migration lourde
(voir §4).

**Cycle de vie d'une annonce :**

```
brouillon (facultatif) → publiée immédiatement → expirée (30 jours)
                            │                        │
                            │                        └─ renouvelée en 1 clic → publiée (30 jours de plus)
                            ├─ marquée par l'anti-spam → file de revue admin
                            ├─ retirée par le vendeur (vendu / plus disponible)
                            └─ suspendue ou supprimée par un administrateur
```

- **Publication immédiate** (décision Q2) : aucune validation préalable.
  Les annonces sont analysées automatiquement par des règles anti-spam à
  la publication (voir §3.7).
- **Expiration automatique :** 30 jours après publication ou dernier
  renouvellement. L'annonce expirée n'apparaît plus dans la recherche mais
  reste visible dans l'espace du vendeur.
- **Renouvellement** (décision Q10) : bouton « renouveler » en un clic
  depuis l'espace vendeur. L'annonce renouvelée **remonte en tête des
  résultats** comme une nouvelle publication et repart pour 30 jours.
  Pour éviter les abus, le renouvellement des annonces gratuites est
  **limité à une fois tous les 7 jours** (paramètre configurable). Les
  futurs comptes Premium bénéficieront de davantage de remontées (§8).
- Le vendeur peut modifier ou retirer son annonce à tout moment.

### 3.4 Recherche et navigation

- Page d'accueil : annonces récentes, accès par catégorie, barre de
  recherche.
- Recherche par mots-clés sur titre et description.
- Filtres : catégorie, **commune** (critère principal au lancement),
  ville, fourchette de prix **par devise** (décision Q4 : « Prix en USD
  entre … et … » — pas de conversion, les annonces « à discuter » restant
  visibles hors filtre de prix), champs spécifiques de la catégorie
  sélectionnée (ex. : nombre de pièces en immobilier, marque en
  véhicules).
- Tri : plus récentes d'abord (par défaut — la date de dernier
  renouvellement compte comme date de publication), prix croissant /
  décroissant au sein d'une devise.
- Pages d'annonce accessibles par URL publique partageable (WhatsApp étant
  un canal de diffusion majeur à Kinshasa).

### 3.5 Mise en relation acheteur / vendeur

Au moment de la publication, le vendeur choisit **un** des deux modes :

1. **Numéro affiché :** le numéro est disponible sur l'annonce, mais
   **masqué derrière un bouton « Afficher le numéro »** (décision Q9) afin
   de limiter la récupération automatique par des robots. Le clic exige
   d'être connecté ; chaque clic est **journalisé** (statistiques pour le
   vendeur + preuve de contact pour le système d'avis, décision Q1). Les
   numéros ne doivent pas être indexables par les moteurs de recherche.
2. **Messagerie interne uniquement :** le numéro est masqué partout ; le
   contact passe par la messagerie de Kongo Market, qui nécessite un
   compte côté acheteur.

**Messagerie interne (MVP) :**

- Conversations rattachées à une annonce (un fil par couple
  acheteur / annonce).
- Boîte de réception avec compteur de messages non lus.
- Pas de pièces jointes dans le MVP ; texte uniquement.
- **Notification par e-mail** (décision Q5) : le destinataire d'un nouveau
  message est prévenu par e-mail (avec regroupement pour éviter un e-mail
  par message). Les notifications push arriveront avec les applications
  mobiles.

### 3.6 Profils vendeurs, avis et notation

- Chaque utilisateur a un profil public listant ses annonces actives.
- **Avis** (décision Q1) : peut laisser un avis tout utilisateur connecté
  ayant effectué une **action de contact traçable sur la plateforme**
  envers ce vendeur : clic sur « Afficher le numéro » ou envoi d'un
  message interne. Aucune preuve de transaction n'est exigée — seule
  l'initiation du contact depuis la plateforme conditionne le droit
  de noter.
- Un avis = note en étoiles (1 à 5) + commentaire textuel.
- **Note moyenne** affichée sur le profil et rappelée sur chaque annonce
  du vendeur.
- Un même acheteur ne peut laisser qu'un avis par vendeur (modifiable),
  pour limiter le spam de notation.

### 3.7 Signalement et modération

La modération combine trois sources, toutes traitées par un humain :

1. **Signalements des utilisateurs :** bouton « Signaler » sur chaque
   annonce, accessible à tous (y compris visiteurs sans compte), avec un
   motif à choisir (arnaque présumée, contenu illicite, doublon, mauvaise
   catégorie, autre) et un commentaire libre facultatif.
2. **Règles anti-spam automatiques** (décision Q2) : à la publication,
   chaque annonce passe par des règles simples (ex. : publication en
   rafale, doublons quasi identiques, motifs frauduleux connus). Une
   annonce suspecte est **marquée et versée dans la file de revue** —
   les règles automatiques **ne suppriment jamais rien elles-mêmes**.
   La liste des règles v1 est à définir en conception détaillée.
3. **Initiative de l'administrateur**, qui peut agir sur toute annonce.

**Traitement :** signalements et annonces marquées alimentent une **file
de revue** unique dans l'interface d'administration. L'administrateur
examine chaque cas et décide : rejeter le signalement / la marque,
**modifier**, **suspendre** ou **supprimer** l'annonce, ou (cas graves)
suspendre le compte du vendeur.

- Toute action de modération est journalisée (qui, quoi, quand, motif).

### 3.8 Administration

Interface réservée aux administrateurs :

- File de revue unifiée (signalements + annonces marquées par
  l'anti-spam) avec actions : rejeter, modifier, suspendre ou supprimer
  l'annonce, suspendre le compte.
- Gestion des référentiels : villes et communes (ajout / activation),
  catégories, leurs champs spécifiques et leur paramètre « photos
  obligatoires ».
- Recherche d'utilisateurs et d'annonces ; suspension / réactivation de
  comptes.
- Tableau de bord minimal : nombre d'annonces publiées, d'inscriptions,
  de signalements et de marques anti-spam en attente.

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
Ville ──< Commune ──< Utilisateur ──< Annonce >── Catégorie
                          │             │               │
                          │             ├──< Photo      └──< DéfinitionDeChamp
                          │             ├──< ValeurDeChamp (par annonce)
                          │             ├──< Signalement
                          │             ├──< MarqueAntiSpam
                          │             ├──< ClicAffichageNuméro
                          │             └──< Conversation ──< Message
                          └──< Avis (émis et reçus)
```

| Entité | Attributs clés | Notes |
|---|---|---|
| **Ville** | nom, statut actif/inactif | Extensible plus tard vers un niveau Province au-dessus ; jamais de ville en dur dans le code |
| **Commune** | ville, nom, statut | Niveau principal de localisation au lancement (Kinshasa) |
| **Utilisateur** | e-mail (identifiant de connexion), mot de passe, nom d'affichage, téléphone (facultatif), commune, rôle, statut de vérification (`non_verifie` par défaut — réservé pour la future vérification SMS), statut du compte (actif / suspendu) | Rôle extensible (Premium, badge pro, modérateur) |
| **Catégorie** | nom (traduisible), ordre d'affichage, **photos obligatoires (oui/non)** | Les 8 catégories du lancement |
| **DéfinitionDeChamp** | catégorie, nom, type (texte, nombre, liste de valeurs), obligatoire ou non | Permet d'ajouter un champ à une catégorie sans migration lourde (modèle attributs dynamiques ou colonne JSON) |
| **Annonce** | titre, description, catégorie, commune, **prix (nullable)**, devise (USD/CDF, nullable), **indicateur « prix à discuter »**, mode de contact, statut, date de publication, **date de dernier renouvellement** (sert au tri et à la limite de 7 jours), date d'expiration | Expiration = dernier renouvellement + 30 jours |
| **ValeurDeChamp** | annonce, définition de champ, valeur | Valeurs des champs spécifiques |
| **Photo** | annonce, fichier, ordre (max 6) | Stockage objet + variantes redimensionnées ; le type vidéo est une extension future |
| **ClicAffichageNuméro** | annonce, utilisateur, date | Journal des clics « Afficher le numéro » : statistiques vendeur + condition d'accès aux avis (Q1/Q9) |
| **Conversation / Message** | annonce, participants ; expéditeur, texte, lu/non-lu, notification e-mail envoyée | Un fil par couple acheteur-annonce |
| **Avis** | auteur, vendeur visé, note 1–5, commentaire, date | Un avis par couple acheteur-vendeur ; création autorisée seulement si un ClicAffichageNuméro ou un Message de l'auteur vers ce vendeur existe |
| **Signalement** | annonce, auteur (nullable si visiteur), motif, statut de traitement, administrateur, décision | Alimente la file de modération |
| **MarqueAntiSpam** | annonce, règle déclenchée, date, statut de traitement | Alimente la même file de revue que les signalements |
| **JournalModération** | administrateur, action, cible, motif, date | Traçabilité des actions admin |

**Prévu dans le schéma mais inactif dans le MVP** (voir §8) : champs de
mise en avant sur l'annonce (`premium_jusqu_au`, nullable), rôle / statut
« Premium » et « vendeur professionnel », table d'emplacements
publicitaires, statut de vérification SMS. Ces éléments sont *réservés*
dans la conception, **pas développés**.

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

- **Envoi d'e-mails transactionnels** (notifications de messages,
  récupération de mot de passe) via un fournisseur à choisir — la
  délivrabilité (éviter le dossier spam) est un point d'attention.
- **Limitation de débit (rate limiting)** sur : inscription, création
  d'annonces, envoi de messages, clics « Afficher le numéro », dépôt de
  signalements et d'avis. C'est la première ligne de défense contre les
  faux comptes, d'autant plus importante que le MVP n'a pas de
  vérification SMS.
- Les numéros de téléphone ne sont jamais présents dans le HTML initial
  d'une page publique (chargés seulement au clic « Afficher le numéro »,
  utilisateur connecté) et ne sont pas indexables.
- Mots de passe stockés hachés (algorithme moderne), sessions sécurisées.
- Sauvegardes régulières de la base de données.

### 5.4 Extensibilité (contraintes d'architecture, sans développement MVP)

- Aucune valeur métier codée en dur : villes, communes, catégories,
  champs par catégorie, motifs de signalement, règles anti-spam, durée de
  vie des annonces (30 jours) et délai minimal entre renouvellements
  (7 jours) sont des données ou de la configuration.
- L'étape d'inscription est conçue pour accueillir plus tard une
  vérification SMS sans refonte (statut de vérification déjà présent sur
  le compte).
- Le modèle utilisateur et le modèle annonce réservent les emplacements
  nécessaires aux évolutions payantes (§8) sans les implémenter.

### 5.5 Choix de pile technique

Volontairement **non figés dans ce document** : le choix du langage, du
framework, de la base de données et de l'hébergement fera l'objet d'une
décision dédiée à l'étape suivante, une fois ce cahier des charges validé.

---

## 6. Hors périmètre du MVP

Explicitement exclus de la première version :

- **Vérification du numéro de téléphone par SMS** (décision Q3 — reportée
  à une version future, architecture prête).
- Application mobile native (iOS / Android) et notifications push.
- Tout paiement intégré : mise en avant payante, comptes Premium,
  abonnements, mobile money.
- Conversion automatique USD ↔ CDF et affichage multi-devises d'un même
  prix.
- Suppression ou modification **automatique** d'annonces : les règles
  anti-spam marquent pour revue humaine, elles n'agissent jamais seules.
- Vidéos dans les annonces.
- Traduction automatique du contenu des annonces.
- Badge « vendeur professionnel » et comptes boutique.
- Espaces publicitaires.
- Géolocalisation fine (carte, rayon de recherche) — la localisation du
  MVP est la commune et la ville.
- Enchères, panier, commande en ligne, livraison.
- Villes autres que Kinshasa *activées* (le support multi-villes existe,
  seule Kinshasa est active).

---

## 7. Journal des décisions (arbitrages du fondateur)

Décisions fonctionnelles officielles rendues le 21 juillet 2026 sur les
dix questions ouvertes de la version 0.1. Elles font référence pour la
conception, le développement et les évolutions futures.

| # | Question | Décision |
|---|---|---|
| **Q1** | Droit de laisser un avis | Réservé aux utilisateurs connectés ayant une action de contact **traçable sur la plateforme** (clic « Afficher le numéro » ou message interne). Pas de preuve de transaction exigée. |
| **Q2** | Publication des annonces | **Immédiate**, sans validation préalable. Analyse automatique par des règles anti-spam qui **marquent** les annonces suspectes pour revue humaine. L'administrateur peut modifier, suspendre ou supprimer toute annonce. |
| **Q3** | Vérification SMS | **Retirée du MVP** (coûts, simplicité, indépendance vis-à-vis des fournisseurs SMS). Création de compte sans validation SMS. Architecture prête pour l'ajouter plus tard sans modification majeure. |
| **Q4** | Devises | USD ou CDF au choix du vendeur ; filtres de prix **par devise**, aucune conversion automatique dans le MVP. |
| **Q5** | Notification des messages | **E-mail** à la réception d'un message interne dans le MVP ; notifications push reportées aux applications mobiles. |
| **Q6** | Localisation | Lancement centré sur Kinshasa avec la **commune** comme principal niveau de localisation et de recherche. Architecture prête pour l'ajout des autres villes et provinces. |
| **Q7** | Photos | Jusqu'à **6 photos** par annonce. Obligatoires pour les catégories où elles sont pertinentes (véhicules, immobilier, électronique, vêtements, mobilier), facultatives ailleurs. Vidéos prévues pour une version ultérieure. |
| **Q8** | Prix | **Facultatif**, avec option « **Prix à discuter** » (emplois, services, prestations…). |
| **Q9** | Affichage du numéro | Numéro masqué derrière un bouton « **Afficher le numéro** » ; chaque clic est journalisé (statistiques + preuve de contact pour les avis). |
| **Q10** | Renouvellement | Le renouvellement **remonte l'annonce en tête** des résultats. Limité pour les annonces gratuites (**une fois tous les 7 jours**) ; les comptes Premium auront davantage de remontées. |

## 7bis. Questions ouvertes restantes

Points secondaires découlant des arbitrages, à confirmer au fil de la
conception (aucun ne bloque le démarrage) :

- **R1 — Identifiant de connexion.** Ce document retient **e-mail + mot
  de passe** (l'e-mail étant déjà requis pour les notifications Q5, et le
  SMS étant retiré). Alternative possible : numéro de téléphone + mot de
  passe sans vérification. À confirmer avant le développement du module
  comptes.
- **R2 — Règles anti-spam v1.** La décision Q2 introduit une analyse
  automatique ; la liste concrète des premières règles (seuils de
  publication en rafale, détection de doublons, motifs connus) est à
  définir en conception détaillée, en cohérence avec le principe « jamais
  de suppression automatique ».
- **R3 — Liste officielle des communes de Kinshasa** à charger comme
  référentiel de départ (les 24 communes officielles, ou une liste
  enrichie de quartiers usuels).

---

## 8. Évolutions prévues (architecture prête, développement ultérieur)

Rappel des pistes décidées, dont l'architecture tient compte sans les
développer :

1. **Vérification du numéro par SMS** — statut de vérification déjà
   présent sur le compte, étape d'inscription isolée.
2. **Mise en avant payante d'annonces et comptes Premium** — champs
   réservés sur l'annonce, renouvellements supplémentaires pour les
   comptes Premium (décision Q10), emplacement visuel prévu dans les
   listes.
3. **Badge vendeur professionnel** — extension du système de rôles.
4. **Espaces publicitaires** — zones prévues dans la maquette des pages.
5. **Vidéos dans les annonces** — extension du modèle Photo en modèle
   Média.

S'y ajoutent naturellement, sans engagement : activation de nouvelles
villes et provinces, applications mobiles avec notifications push,
paiement mobile money, modération assistée.

---

## 9. Suites de ce document

1. ~~Validation du document v0.1 et arbitrage des questions Q1 à Q10.~~
   **Fait — arbitrages intégrés dans cette version 0.2 (§7).**
2. Choix de la pile technique et de l'hébergement (décision dédiée).
3. Maquettes des écrans clés (accueil, recherche, annonce, publication).
4. Découpage du développement en étapes testables une par une.
