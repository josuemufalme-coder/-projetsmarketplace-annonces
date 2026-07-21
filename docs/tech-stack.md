# Pile technique et hébergement — Kongo Market (MVP)

**Version :** 1.0 — 21 juillet 2026
**Statut :** Validé par le fondateur le 21 juillet 2026 — document de référence
**Référence :** `docs/srs.md` v0.3

---

## 1. Les critères de décision

Tout choix de ce document est évalué contre les six critères fixés par le
fondateur, plus un septième propre à la méthode de travail du projet :

1. **Coût** : budget mensuel minimal au lancement, croissance des coûts
   proportionnelle à la croissance de l'usage (jamais de palier brutal).
2. **Simplicité de maintenance** : un fondateur solo, non-développeur,
   doit pouvoir exploiter la plateforme (déployer, sauvegarder,
   diagnostiquer) sans administrateur système.
3. **Évolutivité** : supporter la croissance de Kinshasa vers la RDC
   entière sans réécriture.
4. **Sécurité** : protections standard par défaut, surface d'attaque
   minimale, peu de composants à tenir à jour.
5. **Performance sur connexions lentes** : pages légères, rapides sur 3G
   instable, images optimisées.
6. **Capacité à accompagner la croissance** : chaque composant doit avoir
   un chemin de montée en charge connu et documenté.
7. **Compatibilité avec le développement assisté par IA** : le projet est
   construit avec Claude Code, prompt par prompt. La pile doit être celle
   où les IA sont les plus fiables : technologies très répandues,
   conventions fortes, documentation abondante, peu de « magie » cachée.

---

## 2. La recommandation en bref

| Couche | Choix recommandé | Rôle |
|---|---|---|
| Langage & framework | **Python + Django** | Application monolithique : site public, messagerie, comptes, modération |
| Interface | **Templates Django (HTML rendu serveur) + HTMX + Tailwind CSS** | Pages légères, interactivité ciblée sans framework JavaScript lourd |
| Base de données | **PostgreSQL** | Données, champs par catégorie (JSONB), recherche plein texte du MVP |
| Interface d'administration | **Django Admin** (personnalisé) | File de modération, référentiels villes/communes/catégories |
| Images | **Cloudflare R2** (stockage objet compatible S3) | Photos d'annonces + variantes redimensionnées |
| CDN, protection, DNS | **Cloudflare** (offre gratuite) | Cache au plus près des utilisateurs, anti-bots/DDoS, TLS |
| E-mails transactionnels | **Brevo** (ou Resend) | Notifications de messages, récupération de mot de passe |
| Hébergement | **Railway** (PaaS, région Europe) — Postgres managé inclus | Déploiement automatique depuis GitHub, sauvegardes, tâches planifiées |
| Code & déploiement | **GitHub → déploiement automatique** | `git push` sur la branche principale = mise en production |

**Coût total estimé au lancement : 15 à 30 USD par mois** (hors nom de
domaine, ~12 USD/an). Détail en §5.

---

## 3. Argumentaire choix par choix

### 3.1 Python + Django (framework « batteries incluses »)

**Le choix structurant du projet.** Django est un framework web mature
(2005, fait tourner Instagram à ses débuts, toujours l'un des frameworks
les plus utilisés au monde) dont la philosophie — *tout inclus, une seule
bonne façon de faire* — est exactement ce qu'il faut ici :

- **L'interface d'administration est fournie.** Le module administration
  du SRS (§3.8 : file de modération, gestion des villes, communes,
  catégories et leurs champs, recherche d'utilisateurs, suspension de
  comptes) correspond presque trait pour trait à ce que Django Admin
  offre nativement, moyennant de la personnalisation légère. Pour un
  fondateur solo, c'est des semaines de développement économisées sur une
  partie invisible du public mais vitale pour toi.
- **Comptes, sessions, mots de passe hachés, protections CSRF/XSS/
  injections SQL : intégrés et actifs par défaut.** La sécurité ne
  dépend pas de l'assemblage correct de briques tierces.
- **L'internationalisation est native.** Le système de traduction de
  Django (fichiers de langue par locale) couvre directement l'exigence
  français / lingala / anglais du SRS, sélecteur de langue compris.
  Ajouter le swahili plus tard = un fichier de plus.
- **Migrations de base de données automatiques** : le schéma évolue par
  petites étapes versionnées — parfaitement adapté au développement
  incrémental « une étape testée à la fois » choisi pour ce projet.
- **Critère IA (n° 7).** Python est le langage sur lequel les modèles
  d'IA sont les plus performants, et Django impose des conventions
  fortes : structure de projet standard, patrons connus, vingt ans de
  documentation et de questions-réponses. Concrètement : Claude Code
  produit du Django plus juste du premier coup, et toi, tu peux relire et
  comprendre ce code plus facilement que celui d'une pile JavaScript
  éclatée en multiples couches.
- **Un monolithe = une seule chose à exploiter.** Un déploiement, une
  base de données, un journal d'erreurs. Quand quelque chose casse à
  2 h du matin, il n'y a qu'un endroit où regarder.

### 3.2 HTML rendu serveur + HTMX + Tailwind (plutôt qu'une SPA React/Next.js)

C'est le choix le plus important pour le **critère performance en RDC** :

- Une page rendue côté serveur envoie du HTML directement affichable :
  pas de mégaoctets de JavaScript à télécharger et exécuter avant de voir
  la première annonce. Sur un téléphone d'entrée de gamme en 3G
  instable, la différence est décisive.
- **SEO natif** : un site d'annonces vit du référencement Google
  (« appartement à louer Lemba »). Le HTML serveur est indexable sans
  effort, métadonnées Open Graph comprises pour le partage WhatsApp —
  canal n° 1 à Kinshasa.
- **HTMX** ajoute l'interactivité là où il en faut (bouton « Afficher le
  numéro », messagerie, filtres sans rechargement) en quelques attributs
  HTML, sans construire ni maintenir une API séparée + une application
  JavaScript. Deux codebases de moins.
- **Tailwind CSS** pour une interface propre, cohérente et responsive
  mobile-first, avec le meilleur support IA des outils CSS actuels.

### 3.3 PostgreSQL

Le standard des bases relationnelles open source, sans vrai concurrent
pour ce cas :

- **JSONB** stocke proprement les champs spécifiques par catégorie
  (surface, kilométrage…) définis dynamiquement dans le SRS, sans
  migration à chaque nouveau champ.
- **Recherche plein texte intégrée** : suffisante pour la recherche par
  mots-clés du MVP. Un moteur dédié (Meilisearch) ne deviendra pertinent
  qu'avec un volume important — chemin d'évolution connu, aucune impasse.
- Sauvegardes, réplication, montée en charge : territoire archi-connu.
  Postgres tiendra sans effort très au-delà du million d'annonces.

### 3.4 Cloudflare (CDN + protection) — la pièce maîtresse pour la RDC

- Cloudflare dispose de points de présence en Afrique, **y compris à
  Kinshasa** : les pages mises en cache et les images sont servies depuis
  le réseau local congolais au lieu de traverser les câbles sous-marins à
  chaque visite. C'est le levier de performance n° 1 pour ton public,
  et il est **gratuit**.
- Protection anti-bots et anti-DDoS devant le site — précieuse pour
  contrer l'aspiration de numéros et le spam (SRS §5.3), sans rien
  développer.
- TLS (HTTPS), DNS et compression gérés au même endroit.

### 3.5 Cloudflare R2 pour les photos

- Compatible S3 (standard universel, bien maîtrisé par les IA et par
  Django), avec un avantage décisif : **zéro frais de sortie** (pas de
  facturation au trafic sortant). Pour un site d'annonces où les images
  représentent l'écrasante majorité du volume servi, c'est l'écart de
  coût le plus important de toute la pile à mesure que l'audience croît.
- Les variantes redimensionnées (vignette, liste, plein écran) sont
  générées côté serveur à l'envoi, puis servies par le CDN — conformément
  au SRS §5.2.

### 3.6 Railway pour l'hébergement (PaaS)

Le critère décisif : **zéro administration système**. Un PaaS (Platform
as a Service) transforme l'hébergement en un service : tu pousses le code
sur GitHub, la plateforme construit, déploie, redémarre en cas de panne,
et gère la base Postgres avec sauvegardes automatiques.

- **Railway** : déploiement automatique depuis GitHub, Postgres managé,
  tâches planifiées (cron) pour l'expiration des annonces et les e-mails
  groupés, journaux lisibles, facturation à l'usage (~10–25 USD/mois pour
  démarrer). Région **Europe (Amsterdam)** : c'est le meilleur compromis
  de latence depuis Kinshasa (le trafic congolais transite par les câbles
  sous-marins de la côte ouest vers l'Europe), et Cloudflare absorbe
  l'essentiel des requêtes en cache local de toute façon.
- Alternative équivalente : **Render** (Francfort) — même philosophie,
  prix similaires. Le choix entre les deux n'est pas structurant.
- **Ce qu'on écarte : un VPS auto-géré** (Hetzner, OVH…). Deux à trois
  fois moins cher sur le papier, mais c'est toi l'administrateur système :
  mises à jour de sécurité, pare-feu, sauvegardes, pannes. Mauvais
  échange pour un fondateur solo non-développeur. Ce sera une
  optimisation de coûts pertinente **plus tard**, quand la facture PaaS
  dépassera ~100 USD/mois — la migration est simple car rien dans la pile
  n'est propriétaire.

### 3.7 Brevo pour les e-mails transactionnels

Notifications de messagerie (décision Q5) et récupération de mot de
passe : un fournisseur spécialisé est indispensable pour la
**délivrabilité** (éviter le dossier spam) — jamais d'envoi direct depuis
le serveur.

- **Brevo** : offre gratuite (300 e-mails/jour) largement suffisante au
  lancement, bonne réputation de délivrabilité, interface simple.
- Alternative : **Resend** (3 000 e-mails/mois gratuits), plus orientée
  développeurs. Choix non structurant, interchangeable en une heure.

### 3.8 GitHub + déploiement continu

- Le code vit sur GitHub (déjà le cas). La branche principale se déploie
  automatiquement : **publier une évolution = valider un commit**, ce qui
  colle à la méthode « une étape testée à la fois » du projet.
- Deux environnements : **production** et, dès que le site est public,
  une **pré-production** (staging) pour tester les évolutions sans
  risquer le site réel.

---

## 4. Les alternatives écartées, et pourquoi

| Alternative | Pourquoi pas |
|---|---|
| **Next.js / Node.js (full-stack JavaScript)** | Excellente pile, mais tout ce que Django fournit (admin, auth, i18n, ORM mûr) serait à assembler à partir de briques tierces — plus de code, plus de choix à faire, plus de surface d'erreur pour un solo. Les pages riches en JavaScript pèsent aussi plus lourd sur 3G. |
| **Laravel (PHP)** | Le concurrent le plus sérieux de Django, philosophie identique. Django l'emporte sur le critère IA (Python) et sur la maturité de son admin natif. Choix défendable, mais pas supérieur ici. |
| **WordPress + thème « petites annonces »** | Démarrage rapide, plafond très vite atteint : champs par catégorie, messagerie, avis conditionnés au contact tracé, multilingue performant — tout devient un combat contre l'outil. Dette technique et surface d'attaque (plugins) importantes. |
| **No-code (Bubble, etc.)** | Séduisant pour un non-développeur, mais : performances faibles sur connexions lentes, coûts qui grimpent avec l'audience, verrouillage propriétaire — en devenant « la référence nationale », il faudrait tout réécrire. Et le no-code neutralise ton principal atout : Claude Code écrit du vrai code, pas des configurations Bubble. |
| **Microservices / serverless** | Surdimensionné : complexité d'exploitation sans bénéfice à cette échelle. Le monolithe Django bien structuré est la norme pour ce type de plateforme jusqu'à des millions de visites. |

---

## 5. Estimation des coûts mensuels

| Poste | Lancement | À ~50 000 visites/mois |
|---|---|---|
| Railway (application + Postgres) | 10–25 USD | 25–50 USD |
| Cloudflare (CDN, protection, DNS) | 0 | 0 |
| Cloudflare R2 (photos) | ~0–1 USD | 1–5 USD |
| Brevo (e-mails) | 0 | 0–15 USD |
| Nom de domaine | ~1 USD (12 USD/an) | ~1 USD |
| **Total** | **≈ 15–30 USD/mois** | **≈ 30–70 USD/mois** |

Aucun palier brutal : chaque poste croît progressivement avec l'usage, et
chaque composant a une alternative moins chère documentée (VPS + Coolify
pour l'hébergement, notamment) si la facture devenait un sujet.

---

## 6. Chemins de croissance (critère évolutivité)

Ce que devient chaque composant quand la plateforme grandit — sans
réécriture :

| Besoin futur | Évolution prévue |
|---|---|
| Plus de trafic | Augmenter les ressources Railway (un curseur), puis réplique de lecture Postgres |
| Recherche plus riche | Ajouter Meilisearch à côté de Postgres |
| Applications mobiles | Le monolithe Django expose une API (Django REST Framework) consommée par les apps — le cœur métier ne change pas |
| Vérification SMS (décision Q3) | Brancher un fournisseur SMS sur l'étape d'inscription déjà isolée |
| Paiements (Premium, mise en avant) | Intégration mobile money / carte dans le monolithe ; les emplacements sont réservés dans le schéma |
| Nouvelles villes / provinces | Déjà couvert par les référentiels en base (SRS §3.2) |
| Équipe qui s'agrandit | Django est l'un des frameworks où il est le plus facile de recruter, y compris parmi les développeurs de la région |

---

## 7. Risques et points de vigilance

- **Dépendance à des services étrangers** (Railway, Cloudflare, Brevo) :
  inévitable au lancement — il n'existe pas d'offre managée équivalente
  hébergée en RDC. Atténuation : aucun composant propriétaire dans la
  pile (Django, Postgres et S3 sont portables partout), sauvegardes de la
  base exportées régulièrement hors de Railway.
- **Coût du PaaS à forte échelle** : assumé — le confort d'exploitation
  vaut largement l'écart de prix tant que la facture reste sous
  ~100 USD/mois ; au-delà, migration planifiable vers un VPS géré par
  un prestataire.
- **Délivrabilité e-mail vers les boîtes congolaises** (Gmail domine
  largement) : à tester tôt avec de vrais comptes ; configuration
  SPF/DKIM dès la mise en place de Brevo.
- **Latence résiduelle** des actions non cachables (publication, envoi de
  message) vers l'Europe : ~150–200 ms, imperceptible pour ces usages ;
  le contenu consulté (pages, images) est servi depuis le cache local
  Cloudflare.

---

## 8. Prochaines étapes proposées

1. **Validation de ce document** par le fondateur.
2. Création des comptes de service : Cloudflare, Railway, Brevo ; achat
   du nom de domaine (kongomarket.cd et/ou .com — à décider).
3. Initialisation du projet Django dans ce dépôt : squelette, base de
   données, premier déploiement d'une page « bientôt disponible » en
   production — pour valider toute la chaîne (GitHub → Railway →
   Cloudflare → navigateur à Kinshasa) avant d'écrire la moindre
   fonctionnalité.
4. Puis développement par étapes testables, dans l'ordre du SRS :
   référentiels (communes, catégories) → comptes → publication d'annonce
   → recherche → contact → avis → modération.
