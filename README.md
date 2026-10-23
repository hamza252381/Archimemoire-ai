# ArchiMémoire AI — version initiale

Application personnelle de recherche architecturale, avec recherche Internet via l'API OpenAI et bibliothèque SQLite.

## Démarrer sur un ordinateur

1. Installer Python 3.10 ou plus récent.
2. Ouvrir un terminal dans ce dossier.
3. Installer les dépendances : `pip install -r requirements.txt`
4. Définir la clé API **sur le serveur**, jamais dans le navigateur :
   - macOS/Linux : `export OPENAI_API_KEY="votre_cle"`
   - Windows PowerShell : `$env:OPENAI_API_KEY="votre_cle"`
5. Exécuter `python app.py`.
6. Ouvrir `http://127.0.0.1:5000` sur cet ordinateur.

## Sur iPhone

Pour accéder à l'application hors de l'ordinateur, il faut déployer le serveur Flask chez un hébergeur compatible Python, en configurant `OPENAI_API_KEY` comme variable d'environnement secrète. Prévoir une base SQLite persistante (volume) ou remplacer SQLite par une base hébergée, car certains hébergeurs effacent les fichiers au redémarrage. Configurer HTTPS. Dans Safari sur iPhone, ouvrir l'adresse HTTPS puis utiliser Partager > Sur l'écran d'accueil.

**Important :** cette première version n'a pas encore de connexion utilisateur. Ne pas la publier telle quelle en accès public : quiconque connaît l'URL peut déclencher des recherches facturées et consulter les fiches. Avant déploiement, ajouter une authentification, des limites d'utilisation et des sauvegardes. Pour une installation PWA complète hors ligne, ajouter des icônes et un service worker. La version actuelle est une application web mobile installable selon le navigateur et le contexte d'hébergement, mais n'offre pas le mode hors ligne.

L'API OpenAI facture l'utilisation selon ses tarifs. Le modèle par défaut est `gpt-4.1-mini` avec l'outil `web_search` de la Responses API ; on peut changer le modèle avec `OPENAI_MODEL`. La disponibilité de l'outil dépend du modèle et du compte API. Les fiches doivent être vérifiées avant publication.
