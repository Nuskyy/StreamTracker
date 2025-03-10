# Discord Twitch Bot

## Description
Ce bot Discord surveille l'activité de streamers Twitch et envoie une notification sur un salon Discord lorsque l'un d'eux commence un live.

## Fonctionnalités
- Suivi des streamers Twitch enregistrés
- Notification automatique sur Discord lors du démarrage d'un live
- Ajout, suppression et modification de streamers via commandes slash
- Stockage des streamers surveillés dans une base de données MySQL

## Prérequis
Avant d'exécuter le bot, assurez-vous d'avoir :

- Un serveur Discord avec les permissions nécessaires
- Un bot Discord enregistré et son token
- Une base de données MySQL configurée
- Un compte développeur Twitch avec une client ID et un client secret
- Python 3.8+

## Installation
1. Clonez le dépôt :
   ```sh
   git clone https://github.com/Nuskyy/StreamTracker.git
   cd votre-repo
   ```
2. Installez les dépendances :
   ```sh
   pip install -r requirements.txt
   ```
3. Configurez les variables d'environnement ou remplacez les valeurs dans le code :
   - `DISCORD_TOKEN`
   - `TWITCH_CLIENT_ID`
   - `TWITCH_CLIENT_SECRET`
   - `DISCORD_CHANNEL_ID`
   - `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
4. Lancez le bot :
   ```sh
   python bot.py
   ```

## Commandes
| Commande           | Description |
|--------------------|-------------|
| `/addstreamer`     | Ajoute un streamer à la liste de surveillance |
| `/liststreamers`   | Liste les streamers surveillés |
| `/removestreamer`  | Supprime un streamer de la liste |
| `/editstreamer`    | Modifie la description d'un streamer |

## Sécurité
**Ne partagez jamais votre token Discord ou vos clés API en ligne !**
Utilisez des variables d'environnement ou un fichier `.env` pour stocker ces informations sensibles.

## Licence
Ce projet est sous licence MIT. Vous êtes libre de l'utiliser et de le modifier.

## Auteurs
- [Votre Nom](https://github.com/Nuskyy)

