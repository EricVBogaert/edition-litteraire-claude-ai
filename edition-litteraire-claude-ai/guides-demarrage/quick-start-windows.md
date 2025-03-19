# Guide de démarrage rapide - Windows

Ce guide vous accompagne pas à pas dans la mise en place de l'environnement d'édition littéraire assistée par IA sur Windows, tel que décrit dans le Project Knowledge. Il est spécifiquement conçu pour les débutants qui découvrent Git et les systèmes de versionnement.

## 1. Installation des outils essentiels

### Claude.ai

1. Accédez à [claude.ai](https://claude.ai/)
2. Créez un compte ou connectez-vous
3. Aucune installation n'est requise, Claude.ai fonctionne dans votre navigateur

### Obsidian

1. Téléchargez Obsidian depuis [obsidian.md](https://obsidian.md/)
2. Lancez l'installateur et suivez les instructions
3. Ouvrez Obsidian après l'installation

### Git

L'installation de Git est une étape cruciale pour pouvoir versionner votre travail :

1. Téléchargez Git pour Windows sur [git-scm.com/download/win](https://git-scm.com/download/win)
2. Exécutez l'installateur
3. Configurations recommandées lors de l'installation :
    - Choisissez "Git from the command line and also from 3rd-party software"
    - Pour les fins de ligne, sélectionnez "Checkout Windows-style, commit Unix-style"
    - Pour le terminal, choisissez "Use Windows' default console window"
    - Acceptez les autres options par défaut

> **Important** : GitHub Desktop seul n'est pas suffisant. Vous devez installer Git complet pour qu'Obsidian Git fonctionne correctement.

### VS Code (optionnel pour commencer)

1. Téléchargez VS Code depuis [code.visualstudio.com](https://code.visualstudio.com/)
2. Installez en suivant les instructions

## 2. Configuration initiale d'Obsidian

### Création d'un vault (coffre)

Un "vault" est l'espace de travail d'Obsidian qui contient tous vos documents et configurations :

1. Lancez Obsidian
2. Sur l'écran d'accueil, cliquez sur "Créer un nouveau coffre"
3. Donnez un nom à votre vault (ex: "mon-projet-litteraire")
4. Choisissez l'emplacement sur votre disque où il sera stocké
5. Cliquez sur "Créer"

### Installation des plugins essentiels

1. Ouvrez les Paramètres d'Obsidian (icône d'engrenage en bas à gauche)
    
2. Activez les plugins principaux (Core plugins) suivants :
    
    - Templates
    - Tags (Volet des tags)
3. Pour les plugins communautaires :
    
    - Allez dans "Plugins communautaires"
    - Désactivez le mode sans échec si demandé
    - Cliquez sur "Parcourir" et recherchez les plugins suivants :
        - Obsidian Git
        - Outliner
        - Kanban
    - Installez et activez chaque plugin

## 3. Intégration avec Git et GitHub

### Comprendre les concepts de base de Git

Git peut sembler complexe au début, mais ses concepts fondamentaux sont accessibles :

- **Dépôt (repository)** : Un dossier suivi par Git qui contient votre projet
- **Commit** : Une "sauvegarde" de l'état de vos fichiers à un moment précis
- **Push** : L'envoi de vos commits locaux vers un dépôt distant (comme GitHub)
- **Pull** : La récupération des changements depuis le dépôt distant vers votre ordinateur

Imaginez Git comme un système de points de sauvegarde avancé pour vos documents, qui vous permet également de collaborer avec d'autres personnes.

### Méthode A : Créer un nouveau projet depuis zéro

1. **Créez un dépôt sur GitHub** :
    
    - Connectez-vous à [github.com](https://github.com/)
    - Cliquez sur le bouton "+" puis "New repository"
    - Nommez votre dépôt et cliquez sur "Create repository"
    - GitHub vous présentera des instructions pour initialiser votre dépôt
2. **Clonez le dépôt sur votre ordinateur** :
    
    - Copiez l'URL du dépôt (bouton vert "Code")
    - Ouvrez Git Bash (clic droit dans un dossier → Git Bash Here)
    - Tapez : `git clone [URL-copiée]`
    - Exemple : `git clone https://github.com/votre-nom/votre-projet.git`
3. **Utilisez ce dossier comme vault Obsidian** :
    
    - Dans Obsidian, retournez à l'écran d'accueil (icône de coffre en bas à gauche)
    - Choisissez "Ouvrir un dossier comme coffre"
    - Sélectionnez le dossier de votre dépôt Git

### Méthode B : Utiliser un vault Obsidian existant avec Git

1. **Initialisez Git dans votre vault** :
    
    - Ouvrez Git Bash dans le dossier de votre vault
    - Tapez : `git init`
2. **Connectez à un dépôt GitHub distant** :
    
    - Créez d'abord un dépôt vide sur GitHub (sans README ni .gitignore)
    - Copiez l'URL du dépôt
    - Dans Git Bash, tapez :
        
        ```bash
        git remote add origin [URL-du-dépôt]git branch -M maingit push -u origin main
        ```
        

## 4. Workflow quotidien : Commit et Push

Le cycle habituel de travail avec Git comprend ces étapes :

### Faire un commit (sauvegarder vos changements)

**Via Obsidian Git** :

1. Modifiez vos fichiers normalement dans Obsidian
2. Appuyez sur `Ctrl+P` pour ouvrir la palette de commandes
3. Tapez "git" et sélectionnez "Obsidian Git: Commit all changes"
4. Entrez un message décrivant vos modifications (ex: "Ajout du chapitre 2")

**Via Git Bash** :

1. Ouvrez Git Bash dans le dossier de votre projet
2. Vérifiez les fichiers modifiés : `git status`
3. Ajoutez les fichiers modifiés : `git add .`
4. Créez le commit : `git commit -m "Votre message de commit"`

> **Astuce** : Un bon message de commit décrit brièvement ce que vous avez changé et pourquoi.

### Envoyer vos changements vers GitHub (push)

**Via Obsidian Git** :

1. Appuyez sur `Ctrl+P` pour ouvrir la palette de commandes
2. Tapez "git" et sélectionnez "Obsidian Git: Push"

**Via Git Bash** :

1. Ouvrez Git Bash dans le dossier de votre projet
2. Tapez : `git push`

> **Note** : Lors de votre premier push, vous pourriez avoir à vous authentifier avec GitHub. Suivez les instructions à l'écran pour la vérification.

### Configuration recommandée d'Obsidian Git

Pour automatiser les sauvegardes :

1. Ouvrez les paramètres d'Obsidian
2. Allez dans les paramètres du plugin Obsidian Git
3. Configurez :
    - Backup interval : 10 (pour sauvegarder toutes les 10 minutes)
    - Activez "Commit message on auto backup" et personnalisez le message si souhaité

## 5. Structure recommandée pour votre projet

Suivez cette organisation pour bien structurer votre travail :

```
mon-projet-litteraire/
├── README.md                # Vue d'ensemble du projet
├── structure/               # Plans et structure
├── chapitres/               # Contenu principal
├── ressources/              # Recherches et références
└── media/                   # Images et autres médias
```

Créez ces dossiers manuellement ou utilisez Git Bash avec les commandes :

```bash
mkdir structure chapitres ressources media
```

## 6. Problèmes courants et solutions

### "Obsidian Git ne trouve pas Git"

- Vérifiez que Git est bien installé : ouvrez CMD et tapez `git --version`
- Redémarrez Obsidian après l'installation de Git
- Assurez-vous que Git est dans votre PATH système

### "Je n'arrive pas à push vers GitHub"

- Vérifiez votre connexion internet
- Assurez-vous d'avoir configuré vos identifiants :
    
    ```bash
    git config --global user.name "Votre Nom"git config --global user.email "votre.email@exemple.com"
    ```
    
- Si vous avez l'authentification à deux facteurs, utilisez un token d'accès personnel

### "Conflits lors du pull"

- Git vous avertira des fichiers en conflit
- Ouvrez les fichiers concernés et cherchez les marqueurs de conflit (`<<<<<<<`, `=======`, `>>>>>>>`)
- Modifiez manuellement pour résoudre les conflits, puis faites un nouveau commit

## Ressources supplémentaires

- [Guide Git simplifié](https://rogerdudler.github.io/git-guide/index.fr.html)
- [Tutoriel vidéo Obsidian en français](https://www.youtube.com/results?search_query=tutoriel+obsidian+fran%C3%A7ais)
- [Documentation officielle d'Obsidian](https://help.obsidian.md/)

---

Ce guide est évolutif. N'hésitez pas à y ajouter vos propres notes et astuces au fur et à mesure de votre apprentissage.