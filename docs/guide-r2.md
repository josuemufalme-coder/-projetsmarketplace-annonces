# Guide — Brancher les photos sur Cloudflare R2

Le code est prêt : dès que les variables R2_* sont définies (sur Railway
ou en local), les photos partent sur R2 au lieu du disque. Sans ces
variables, le stockage local continue de fonctionner (idéal en
développement).

## 1. Créer le bucket (5 min, dans le tableau de bord Cloudflare)

1. Connecte-toi sur https://dash.cloudflare.com
2. Menu de gauche → **R2 Object Storage** → **Create bucket**
   (à la première visite, R2 demande d'activer la facturation : la
   tranche gratuite couvre 10 Go et largement le lancement).
3. Nom du bucket : `kongomarket-media` — région : laisser
   « Automatic ». **Create bucket**.

## 2. Rendre le bucket public en lecture

1. Ouvre le bucket → onglet **Settings**.
2. Section **Public access** → **R2.dev subdomain** → **Allow Access**.
3. Note l'adresse affichée, du type `pub-xxxxxxxx.r2.dev` — c'est le
   domaine public des photos (plus tard, on le remplacera par
   `media.<ton-domaine>` via « Custom Domains », même écran).

## 3. Créer les clés d'accès

1. Retour à l'accueil R2 → **Manage R2 API Tokens** → **Create API token**.
2. Nom : `kongomarket-app` — permissions : **Object Read & Write**,
   limité au bucket `kongomarket-media`. **Create**.
3. Note (une seule fois affichés !) : **Access Key ID**,
   **Secret Access Key**, et l'**endpoint S3** du type
   `https://<accountid>.r2.cloudflarestorage.com`.

## 4. Renseigner les variables (Railway → ton service → Variables)

| Variable | Valeur |
|---|---|
| `R2_BUCKET` | `kongomarket-media` |
| `R2_ENDPOINT` | `https://<accountid>.r2.cloudflarestorage.com` |
| `R2_ACCESS_KEY_ID` | la clé notée à l'étape 3 |
| `R2_SECRET_ACCESS_KEY` | le secret noté à l'étape 3 |
| `R2_PUBLIC_HOST` | `pub-xxxxxxxx.r2.dev` (sans `https://`) |

Redéploie : les nouvelles photos publiées arrivent dans le bucket
(dossier `media/annonces/...`) et s'affichent depuis le domaine public.

## Ce que fait le code automatiquement

- Chaque photo envoyée est convertie en JPEG et réduite à 1600 px
  maximum ; une **vignette** de 500 px maximum est générée pour les
  listes — c'est elle qui est chargée sur la page d'accueil et les
  résultats de recherche (léger pour la 3G).
- Les URLs publiques ne contiennent aucune signature : elles sont
  mises en cache par le CDN Cloudflare.

## Vérification après branchement

1. Publie une annonce avec une grande photo depuis le site déployé.
2. La photo s'affiche ; son URL commence par ton `R2_PUBLIC_HOST`.
3. Dans le bucket : deux fichiers (image + vignettes/…-min.jpg).
