# PROJECT KNOWLEDGE: GUIDE COMPLET

## Édition littéraire assistée par Claude.ai avec Obsidian & VS Code

---

## DIRECTIVE D'UTILISATION

Ce guide documente un workflow d'édition littéraire assisté par IA combinant Claude.ai, Obsidian et VS Code. Il est conçu pour les auteurs et éditeurs habitués aux outils traditionnels (Word, etc.) souhaitant adopter un environnement de travail plus puissant.

### Système de navigation par tags

Ce document utilise un système de tags structurés pour faciliter la navigation et permettre à Claude.ai de comprendre les références croisées:

#[NomDuConcept](TypeDeRéférence:IdentifiantSection)

  

Types de références:

- Workflow (W) - Étapes du processus d'édition
    
- Outil (O) - Logiciels et interfaces
    
- Technique (T) - Méthodes spécifiques d'édition
    
- Structure (S) - Éléments d'organisation du contenu
    
- Format (F) - Types de fichiers et formats de sortie
    
- Pratique (P) - Bonnes pratiques recommandées
    
- IA (I) - Utilisation spécifique de Claude.ai
    
- Référence (R) - Ressources supplémentaires
    

---

## 1. VUE D'ENSEMBLE DU WORKFLOW

Notre workflow d'édition littéraire combine trois outils principaux:

1. Claude.ai #[Claude](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751) - Assistant IA pour la révision, l'amélioration et la génération de contenu
    
2. Obsidian #[Obsidian](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751) - Pour l'idéation, l'organisation conceptuelle et la structure
    
3. VS Code #[VSCode](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751) - Pour le travail technique et les intégrations
    

Le flux de travail se décompose en 6 phases principales:

graph TD

    A[Idéation dans Obsidian] --> B[Construction de la structure]

    B --> C[Rédaction assistée par Claude.ai]

    C --> D[Révision collaborative]

    D --> E[Mise en forme technique dans VS Code]

    E --> F[Production des formats finaux]

  

### Avantages clés de ce workflow

- Organisation non-linéaire des idées
    
- Versionnement robuste avec Git
    
- Assistance IA personnalisée
    
- Séparation contenu/mise en forme
    
- Génération automatisée de multiples formats de sortie
    

---

## 2. PRÉPARATION DE L'ENVIRONNEMENT

### Installation des outils #[Installation](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

1. Claude.ai  
      
    

- Accédez à [claude.ai](https://claude.ai/)
    
- Créez un compte si nécessaire
    

3. Obsidian  
      
    

- Téléchargez depuis [obsidian.md](https://obsidian.md/)
    
- Installez les plugins recommandés:
    

- Outliner
    
- Kanban
    
- Templates
    
- Tag Pane
    
- Obsidian Git
    

5. VS Code  
      
    

- Téléchargez depuis [code.visualstudio.com](https://code.visualstudio.com/)
    
- Installez les extensions recommandées:
    

- Markdown All in One
    
- Markdown Preview Enhanced
    
- GitLens
    
- Paste Image
    

### Configuration du dépôt Git #[GitSetup](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Créez un nouveau dépôt Git local:  
  
mkdir mon-projet-litteraire

cd mon-projet-litteraire

git init

1.   
    
2. Configurez Obsidian pour utiliser ce dossier comme coffre (vault)  
      
    
3. Installez et configurez le plugin Obsidian Git:  
      
    

- Intervalle de sauvegarde: 10 minutes
    
- Messages de commit automatiques
    

---

## 3. STRUCTURE DU PROJECT KNOWLEDGE

### Organisation des fichiers #[Structure](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

mon-projet-litteraire/

├── index.md                # Document principal

├── structure/              # Plan et structure 

├── chapitres/              # Contenu principal

├── ressources/             # Recherches et références

├── media/                  # Images et autres médias

├── templates/              # Modèles de documents

└── export/                 # Fichiers générés

  

### Document index #[IndexDoc](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Le fichier index.md sert de point d'entrée et contient:

- Métadonnées du projet
    
- Liens vers les sections principales
    
- État d'avancement
    
- Notes éditoriales générales
    

Exemple:

# Mon Projet Littéraire

  

## Métadonnées

- Titre: [Titre de l'œuvre]

- Auteur: [Votre nom]

- Genre: [Genre littéraire]

- Statut: #en-cours

  

## Structure

- [[structure/plan-general]]

- [[structure/personnages]]

- [[structure/univers]]

  

## Chapitres

- [[chapitres/chapitre-01]]

- [[chapitres/chapitre-02]]

...

  

---

## 4. UTILISATION DE CLAUDE.AI

### Organisation en projets Claude.ai #[ProjetsClaude](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Structurez votre travail efficacement sur Claude.ai:

1. Créez des projets distincts pour:  
      
    

- Développement narratif global
    
- Travail sur les personnages
    
- Révision stylistique
    
- Recherche thématique
    

3. Avantages de l'organisation en projets:  
      
    

- Contexte préservé entre les sessions
    
- Historique des conversations accessible
    
- Séparation claire des différentes dimensions du travail
    
- Facilite le partage avec des collaborateurs
    

Nommez clairement vos projets pour faciliter la navigation:  
  
[Titre du livre] - Développement narratif

[Titre du livre] - Personnages

[Titre du livre] - Révision

3.   
    

### Importation de documents GitHub #[ImportGitHub](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Claude.ai peut importer directement des documents depuis GitHub:

1. Avantages:  
      
    

- Partage de documents volumineux
    
- Conservation de la mise en forme
    
- Travail sur des versions spécifiques
    
- Analyse de sections entières
    

3. Comment importer:  
      
    

- Utilisez la fonction d'upload de document dans l'interface Claude.ai
    
- Partagez des liens directs vers les fichiers raw de GitHub
    
- Demandez à Claude d'analyser des sections spécifiques
    

5. Bonnes pratiques:  
      
    

- Fragmentez les documents volumineux en sections logiques
    
- Utilisez des commentaires dans les fichiers pour guider Claude
    
- Référez-vous à des lignes ou sections spécifiques dans vos prompts
    

### Initialisation du projet #[InitProjet](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Pour initialiser Claude.ai avec votre projet:

1. Créez une session de chat dédiée
    
2. Présentez le concept général et le genre littéraire
    
3. Définissez le ton et le style souhaités
    
4. Établissez une terminologie spécifique
    

Exemple de prompt initial:

Je travaille sur un roman [genre] intitulé "[titre]". 

Le concept central est [concept]. 

Les personnages principaux sont [personnages].

J'aimerais que tu m'aides avec le développement de l'intrigue, 

la cohérence des personnages et le style d'écriture, 

qui devrait être [caractéristiques du style].

  

### Sessions de brainstorming #[Brainstorming](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Utilisez Claude.ai pour explorer de nouvelles idées:

1. Décrivez un élément spécifique (personnage, scène, concept)
    
2. Demandez des variations ou développements
    
3. Enregistrez les idées pertinentes dans Obsidian
    

Exemple:

Peux-tu m'aider à développer le personnage de [nom]?

Voici ce que j'ai déjà: [description existante].

J'aimerais explorer ses motivations et son arc narratif.

  

### Gestion des limitations de session #[LimiteSessions](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Optimisez l'utilisation de Claude.ai malgré les limitations:

1. Contraintes actuelles:  
      
    

- Limite de taille par message
    
- Limite d'échanges par période
    
- Historique limité par conversation
    

3. Stratégies d'optimisation:  
      
    

- Divisez les longs textes en segments thématiques
    
- Utilisez des liens GitHub pour partager de longs documents
    
- Résumez les conversations précédentes dans les nouveaux prompts
    
- Exportez régulièrement les conversations importantes
    

5. Préparation du contexte:  
      
    

- Créez des résumés à jour de votre projet
    
- Préparez des "fiches contextuelles" réutilisables
    
- Indiquez clairement où vous en étiez lors de la dernière session
    

### Révision de contenu #[Revision](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Pour soumettre du contenu à révision:

1. Copiez le texte depuis Obsidian ou importez depuis GitHub
    
2. Spécifiez clairement vos demandes de révision
    
3. Intégrez les suggestions pertinentes dans votre document
    

Exemple:

Voici un extrait du chapitre 3:

  

[Votre texte]

  

J'aimerais que tu:

1. Améliores la fluidité des dialogues

2. Vérifies la cohérence avec les événements du chapitre 2

3. Renforces la caractérisation du personnage principal

  

### Stockage des interactions #[SessionsLog](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Documenter vos sessions avec Claude.ai:

1. Créez un dossier claude-sessions/ dans votre projet
    
2. Pour chaque session importante, créez un fichier Markdown
    
3. Incluez le contexte, les prompts et les réponses clés
    

---

## 5. WORKFLOW OBSIDIAN

### Création de la structure #[StructureCreation](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Utilisez Obsidian pour établir la structure principale:

1. Créez un fichier structure/plan-general.md
    
2. Utilisez des titres et sous-titres pour établir la hiérarchie
    
3. Créez des liens vers des fichiers détaillés pour chaque section
    

### Gestion des personnages et éléments #[ElementsGestion](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Créez des fiches détaillées:

1. Un fichier par personnage/élément important
    
2. Utilisez des templates standardisés
    
3. Créez des liens bidirectionnels entre éléments connexes
    

Exemple de template personnage:

# {{nom}}

  

## Caractéristiques

- Âge:

- Apparence:

- Traits de caractère:

  

## Contexte

- Origine:

- Famille:

- Occupation:

  

## Arc narratif

- Motivation:

- Conflit:

- Évolution:

  

## Apparitions

- [[chapitres/chapitre-où-le-personnage-apparaît]]

  

## Notes

  

### Navigation par graphe #[GraphView](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Exploitez la vue graphique d'Obsidian:

1. Activez la vue graphe (icône de nœuds dans la barre latérale)
    
2. Filtrez par tags pour visualiser des aspects spécifiques
    
3. Identifiez les connexions non évidentes entre éléments
    

---

## 6. INTÉGRATION VS CODE

### Configuration optimale #[VSCodeSetup](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Configurez VS Code pour le travail d'édition littéraire:

{

  "markdown.extension.toc.updateOnSave": true,

  "markdown.extension.preview.autoShowPreviewToSide": true,

  "editor.wordWrap": "on",

  "editor.lineHeight": 24

}

  

### Scripts d'automatisation #[Scripts](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Développez des scripts Python pour automatiser certaines tâches:

1. Création d'un script d'assemblage:
    

# compile.py

# Script qui assemble tous les fichiers Markdown selon la structure

import os

import re

  

def compile_document(index_file, output_file):

    # Logique d'assemblage

    pass

  

2. Script d'extraction pour Claude.ai:
    

# extract_for_claude.py

# Extrait une section pour révision avec Claude.ai

import sys

  

def extract_section(file_path, section_name):

    # Logique d'extraction

    pass

  

### Options multiplateforme #[Multiplateforme](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Pour accommoder les utilisateurs de différents environnements:

1. Interface graphique simple:  
      
    

- Créez un script Python avec interface Tkinter:
    

import tkinter as tk

from tkinter import filedialog

  

def create_simple_gui():

    root = tk.Tk()

    root.title("Outils d'édition")

    # Ajoutez des boutons pour les fonctions courantes

    # Exemple: assembler, vérifier, exporter

2.   
    
3. Utilisateurs Windows (CMD):  
      
    

- Créez des fichiers batch (.bat) équivalents:
    

@echo off

REM compile.bat

python compile.py %1 %2

4.   
    
5. Interface web GitHub:  
      
    

- Ajoutez des Actions GitHub dans .github/workflows/:
    

name: Compiler Document

on: [push]

jobs:

  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v2

      - name: Set up Python

        uses: actions/setup-python@v2

      - name: Compiler

        run: python compile.py

6.   
    

---

## 6.1 GESTION DE LA TYPOGRAPHIE #[Typographie](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

### Typographie française avancée #[TypoFR](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

La typographie française comporte des règles spécifiques à respecter:

1. Espaces insécables:  
      
    

- Avant les signes doubles (:, ?, !, ;)
    
- Après l'ouverture et avant la fermeture des guillemets français (« »)
    
- Dans les nombres pour séparer les milliers
    

3. Guillemets:  
      
    

- Utilisation des guillemets français (« ») pour les citations principales
    
- Guillemets anglais (" ") pour les citations à l'intérieur d'autres citations
    

5. Tirets:  
      
    

- Tiret cadratin (—) pour les dialogues
    
- Tiret demi-cadratin (–) pour les incises
    

### Outils de vérification typographique #[OutilsTypo](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Grammarleck (Python):  
  
# typo_check.py

import grammalecte

  

def check_typography(text_file):

    with open(text_file, 'r', encoding='utf-8') as f:

        text = f.read()

    gc = grammalecte.GrammarChecker("fr")

    result = gc.correct(text)

    return result

1.   
    

Adaptation aux standards d'édition: Créez un fichier de configuration pour respecter le style d'une maison d'édition:  
  
{

  "typographie": {

    "guillemets": "français",

    "dialogues": "cadratin",

    "citation_imbriquée": "anglais",

    "espaces_insécables": true

  }

}

2.   
    

Script de correction automatique:  
  
# auto_typography.py

import re

  

def fix_french_typography(text):

    # Remplace les guillemets droits par des guillemets français

    text = re.sub(r'"([^"]*)"', r'« \1 »', text)

    # Ajoute des espaces insécables

    text = re.sub(r'([?!:;])', r' \1', text)

    # Corrige les dialogues

    text = re.sub(r'- ', r'— ', text)

    return text

3.   
    

### Interface utilisateur pour la correction #[InterfaceTypo](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Pour les utilisateurs moins techniques:

1. Extension VS Code:  
      
    

- Créez une extension simple avec des boutons pour appliquer les règles
    
- Ajoutez une prévisualisation en temps réel des corrections
    

3. Interface web simple:  
      
    

- Formulaire HTML permettant de coller du texte et d'obtenir une version corrigée
    
- Déployable sur GitHub Pages
    

5. Intégration avec Obsidian:  
      
    

- Créez un plugin personnalisé
    
- Ajoutez des commandes accessibles dans la palette d'Obsidian
    

### Standards spécifiques par genre #[GenreTypo](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Configurez des préréglages pour différents genres littéraires:

1. Roman littéraire:  
      
    

- Guillemets français
    
- Dialogues avec tiret cadratin et retour à la ligne
    

3. Poésie:  
      
    

- Préservation des espaces en début de ligne
    
- Traitement spécial des enjambements
    

5. Documentation technique:  
      
    

- Format de référence ISO
    
- Espacement spécifique pour les listes
    

7. Livres académiques:  
      
    

- Format de citation standardisé (APA, MLA, Chicago)
    
- Gestion des notes de bas de page
    

---

## 7. GÉNÉRATION DES FORMATS FINAUX #[Export](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Utilisez VS Code pour générer les formats de sortie:

### HTML et site web

1. Installez l'extension "Markdown PDF" dans VS Code
    
2. Configurez les options d'export HTML
    
3. Exportez chaque chapitre ou le document assemblé
    

### PDF de qualité édition

1. Utilisez Pandoc via terminal:
    

pandoc -s document.md -o document.pdf --pdf-engine=xelatex --template=template.tex

  

2. Personnalisez les styles avec un fichier template.tex
    

### Format EPUB

1. Utilisez Pandoc pour générer l'EPUB:
    

pandoc -s document.md -o document.epub --epub-cover-image=cover.jpg

  

2. Validez le format avec EpubCheck
    

---

## 8. BONNES PRATIQUES

### Versionnement #[Versionnement](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

1. Committez fréquemment avec des messages descriptifs
    
2. Créez des branches pour les révisions majeures
    
3. Utilisez des tags Git pour marquer les versions importantes:
    

git tag -a v0.1 -m "Premier jet complet"

  

### Sauvegarde #[Sauvegarde](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

1. Configurez un dépôt Git distant (GitHub, GitLab)
    
2. Poussez régulièrement vos modifications
    
3. Envisagez des sauvegardes supplémentaires hors Git
    

### Collaboration #[Collaboration](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

Pour travailler à plusieurs:

1. Établissez des conventions de nommage claires
    
2. Assignez des sections distinctes à chaque collaborateur
    
3. Utilisez des Pull Requests pour les fusions importantes
    
4. Planifiez des sessions de révision communes
    

---

## 9. RESSOURCES COMPLÉMENTAIRES

### Tutoriels recommandés #[Tutoriels](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

- [Guide officiel Obsidian](https://help.obsidian.md/)
    
- [Markdown Guide](https://www.markdownguide.org/)
    
- [Utilisation avancée de Git](https://git-scm.com/book)
    

### Extensions et plugins utiles #[Extensions](https://claude.ai/chat/f9fb33fd-e95d-4a5f-838c-ccc1c60df751)

- Obsidian: Dataview, Admonition
    
- VS Code: Code Spell Checker, Word Count
    

---

## FIN DU GUIDE

Ce document est évolutif. Référez-vous à la version la plus récente sur le dépôt Git.

Version: 1.0 | Dernière mise à jour: [Date]

  
**