# Guide de démarrage rapide - Windows

Ce guide vous accompagne pas à pas dans la mise en place de l'environnement d'édition littéraire assistée par IA sur Windows, tel que décrit dans le [Project Knowledge](docs/guide-complet.md) #Référence. Il est spécifiquement conçu pour les débutants qui découvrent Git et les systèmes de versionnement.

> **Note importante** : Ce guide est une introduction simplifiée. Pour une documentation plus complète, consultez le [guide complet](docs/guide-complet.md) et la [directive d'utilisation de Claude](docs/directive-utilisation-claude.md).

## 1. Installation des outils essentiels [Installation](workflow/prep01-installation.md) #Workflow

### Claude

1. Accédez à [claude.ai](https://claude.ai/)
2. Créez un compte ou connectez-vous
3. Aucune installation n'est requise, Claude fonctionne dans votre navigateur

### Obsidian [Obsidian](outil/ed01-obsidian.md) #Outil

1. Téléchargez Obsidian depuis [obsidian.md](https://obsidian.md/)
2. Lancez l'installateur et suivez les instructions
3. Ouvrez Obsidian après l'installation

### Git [GitSetup](workflow/prep02-gitsetup.md) #Workflow

L'installation de Git est une étape cruciale pour pouvoir versionner votre travail :

1. Téléchargez Git pour Windows sur [git-scm.com/download/win](https://git-scm.com/download/win)
2. Exécutez l'installateur
3. Configurations recommandées lors de l'installation :
    - Choisissez "Git from the command line and also from 3rd-party software"
    - Pour les fins de ligne, sélectionnez "Checkout Windows-style, commit Unix-style"
    - Pour le terminal, choisissez "Use Windows' default console window"
    - Acceptez les autres options par défaut

> **Important** : GitHub Desktop seul n'est pas suffisant. Vous devez installer Git complet pour qu'Obsidian Git fonctionne correctement.

### VS Code (optionnel pour commencer) [VSCode](outil/ed02-vscode.md) #Outil

1. Téléchargez VS Code depuis [code.visualstudio.com](https://code.visualstudio.com/)
2. Installez en suivant les instructions

## 2. Configuration initiale d'Obsidian [StructureCreation](workflow/obs01-structure-creation.md) #Workflow

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
    
    - Templates (Modèles)
    - Tags (Volet des tags)
    
3. Pour les plugins communautaires :
    
    - Allez dans "Plugins communautaires"
    - Désactivez le mode sans échec si demandé
    - Cliquez sur "Parcourir" et recherchez les plugins suivants :
        - Obsidian Git
        - Outliner
        - Kanban
    - Installez et activez chaque plugin

## 3. Intégration avec Git et GitHub [Versionnement](pratique/git01-versionnement.md) #Pratique

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
        git remote add origin [URL-du-dépôt]
        git branch -M main
        git push -u origin main
        ```

### Authentification GitHub moderne

Pour l'authentification avec GitHub, les méthodes recommandées sont :

1. **Utilisation d'un token d'accès personnel (PAT)** :
    - Allez dans Paramètres GitHub → Developer settings → Personal access tokens
    - Générez un nouveau token avec les permissions appropriées (au minimum `repo`)
    - Utilisez ce token comme mot de passe lors des opérations Git

2. **Authentification SSH** (pour utilisateurs avancés) :
    - Générez une paire de clés SSH avec `ssh-keygen -t ed25519 -C "votre.email@exemple.com"`
    - Ajoutez la clé publique à votre compte GitHub
    - Configurez Git pour utiliser SSH

## 4. Workflow quotidien : Commit et Push [SessionsLog](ia/claude06-sessions-log.md) #IA

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

### Configuration recommandée d'Obsidian Git

Pour automatiser les sauvegardes :

1. Ouvrez les paramètres d'Obsidian
2. Allez dans les paramètres du plugin Obsidian Git
3. Configurez :
    - Backup interval : 10 (pour sauvegarder toutes les 10 minutes)
    - Activez "Commit message on auto backup" et personnalisez le message si souhaité

## 5. Structure recommandée pour votre projet [Structure](structure/org01-structure.md) #Structure

Suivez cette organisation pour bien structurer votre travail, conforme aux recommandations du guide complet :

```
mon-projet-litteraire/
├── README.md                # Pour GitHub (description, liens, installation)
├── index.md                 # Document principal pour Obsidian
├── structure/               # Plans et structure 
├── chapitres/               # Contenu principal
├── ressources/              # Recherches et références
├── media/                   # Images et autres médias
├── templates/               # Modèles de documents (optionnel pour débutants)
└── export/                  # Fichiers générés (optionnel pour débutants)
```

> **Note** : Les dossiers `templates/` et `export/` sont recommandés dans le guide complet mais peuvent être ajoutés ultérieurement si vous débutez.

**Distinction README.md et index.md** :
- `README.md` est recommandé pour GitHub car il s'affiche automatiquement sur la page d'accueil de votre dépôt
- `index.md` est le document principal de navigation pour votre projet dans Obsidian, contenant les liens et métadonnées essentielles

Créez ces dossiers manuellement ou utilisez Git Bash avec les commandes :

```bash
mkdir structure chapitres ressources media templates export
```

## 6. Intégration avec Claude [ProjetsClaude](ia/claude00-projets-claude.md) #IA

Claude est un assistant IA puissant qui peut vous aider dans votre processus d'écriture et d'édition. Cette section vous explique comment intégrer efficacement Claude dans votre workflow d'édition littéraire.

### Organisation basique avec Claude

1. **Créez des projets distincts dans Claude** :
   - Un projet pour le développement narratif
   - Un projet pour le travail sur les personnages
   - Un projet pour la révision stylistique

2. **Importation du guide complet dans Claude** :
   - Accédez à l'interface de conversation de Claude sur [claude.ai](https://claude.ai)
   - Créez un nouveau projet nommé "[Votre projet] - Méthodologie"
   - Dans la zone de saisie de message, cliquez sur l'icône du trombone (📎) en bas à gauche
   - Naviguez jusqu'au fichier `guide-complet.md` dans votre dépôt local
   - Sélectionnez le fichier et cliquez sur "Ouvrir"
   - Ajoutez un message d'accompagnement comme : "Voici le guide complet de méthodologie d'édition littéraire que je souhaite utiliser pour mon projet. Peux-tu m'aider à l'appliquer pour [description de votre projet] ?"
   - Envoyez le message

   > **Note** : Si le fichier `guide-complet.md` est trop volumineux pour être importé directement, vous pouvez :
   > - Le diviser en sections plus petites et les importer séparément
   > - Partager un lien vers le fichier brut (raw) sur GitHub
   > - Copier-coller des sections spécifiques selon vos besoins du moment

3. **Importation d'autres documents** :
   - Utilisez la même méthode pour importer vos chapitres, notes de recherche ou plans
   - Partagez des extraits spécifiques pour obtenir des retours

3. **Sessions de brainstorming** :
   - Décrivez un élément spécifique (personnage, scène, concept)
   - Demandez des variations ou développements
   - Enregistrez les idées pertinentes dans Obsidian

4. **Référence au guide dans vos conversations** :
   - Une fois le guide importé, vous pouvez y faire référence dans vos conversations ultérieures
   - Utilisez les noms des concepts spécifiques : "En suivant la méthode [Brainstorming](ia/claude03-brainstorming.md) du guide..."
   - Rappelez à Claude que vous travaillez dans le cadre de cette méthodologie : "Dans le contexte du Project Knowledge que je t'ai partagé précédemment..."

5. **Révision de contenu** :
   - Soumettez des extraits à Claude pour révision
   - Spécifiez clairement vos demandes (style, cohérence, etc.)
   - Intégrez les suggestions pertinentes dans vos documents

6. **Utilisation de la directive d'utilisation** :
   - Importez également le fichier `directive-utilisation-claude.md` en suivant le même processus
   - Ce document explique spécifiquement comment Claude doit interpréter et utiliser le guide
   - Cette étape optimise significativement l'efficacité de vos sessions de travail avec Claude

> **Pour approfondir** : Consultez la [directive d'utilisation de Claude](docs/directive-utilisation-claude.md) pour des techniques avancées d'interaction avec Claude et d'optimisation de vos sessions de travail.

## 7. Problèmes courants et solutions [Collaboration](pratique/collab01-collaboration.md) #Pratique

### "Obsidian Git ne trouve pas Git"

- Vérifiez que Git est bien installé : ouvrez CMD et tapez `git --version`
- Redémarrez Obsidian après l'installation de Git
- Assurez-vous que Git est dans votre PATH système

### "Je n'arrive pas à push vers GitHub"

- Vérifiez votre connexion internet
- Assurez-vous d'avoir configuré vos identifiants :
    
    ```bash
    git config --global user.name "Votre Nom"
    git config --global user.email "votre.email@exemple.com"
    ```
    
- Si vous avez l'authentification à deux facteurs, utilisez un token d'accès personnel comme expliqué dans la section 3

### "Conflits lors du pull"

- Git vous avertira des fichiers en conflit
- Ouvrez les fichiers concernés et cherchez les marqueurs de conflit (`<<<<<<<`, `=======`, `>>>>>>>`)
- Modifiez manuellement pour résoudre les conflits, puis faites un nouveau commit

## 8. Workflow complet illustré

Voici un exemple de workflow complet pour vous aider à démarrer :

1. **Configuration initiale** (à faire une seule fois) :
   - Installez Git, Obsidian et créez un compte Claude
   - Créez un dépôt GitHub et clonez-le localement
   - Configurez ce dossier comme vault Obsidian
   - Installez les plugins recommandés

2. **Démarrage d'un nouveau projet** :
   - Créez la structure de dossiers recommandée
   - Initialisez le fichier `index.md` comme point d'entrée
   - Créez un fichier `README.md` pour la documentation GitHub

3. **Intégration avec Claude** :
   - Créez un nouveau projet dans Claude
   - Importez le `guide-complet.md` et la `directive-utilisation-claude.md`
   - Initialisez le projet en expliquant votre concept à Claude

4. **Cycle de travail quotidien** :
   - Travaillez sur vos documents dans Obsidian
   - Utilisez Claude pour le brainstorming, la révision et l'amélioration
   - Committez régulièrement vos changements (idéalement toutes les heures)
   - Poussez vers GitHub en fin de journée

5. **Organisation de la connaissance** :
   - Utilisez les templates standardisés pour les personnages, lieux, etc.
   - Maintenez à jour votre `index.md` avec les liens vers les sections importantes
   - Utilisez la vue graphe d'Obsidian pour visualiser les connexions

Ce workflow combine les avantages de tous les outils : l'organisation d'Obsidian, l'assistance créative de Claude et la sécurité du versionnement Git.

## Ressources supplémentaires [Tutoriels](reference/tut01-tutoriels.md) #Référence

- [Guide Git simplifié](https://rogerdudler.github.io/git-guide/index.fr.html)
- [Tutoriel vidéo Obsidian en français](https://www.youtube.com/results?search_query=tutoriel+obsidian+fran%C3%A7ais)
- [Documentation officielle d'Obsidian](https://help.obsidian.md/)
- [Guide complet du Project Knowledge](docs/guide-complet.md)
- [Directive d'utilisation de Claude](docs/directive-utilisation-claude.md)
- [Astuces pour l'édition littéraire avec IA](https://blog.anthropic.com/claude-tips-creative-writing)

---

Ce guide est évolutif. N'hésitez pas à y ajouter vos propres notes et astuces au fur et à mesure de votre apprentissage.

Version: 1.1 | Dernière mise à jour: 19 mars 2025