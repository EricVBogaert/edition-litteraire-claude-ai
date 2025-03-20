# STRUCTURE RÉVISÉE DU PROJET LITTÉRAIRE

## Organisation des fichiers

```
mon-projet-litteraire/
├── index.md                          # Document principal de navigation
├── chapitres/                        # Contenu principal narratif
│   ├── chapitre-01.md
│   ├── chapitre-02.md
│   └── ...
│
├── structure/                        # Plan et structure narrative
│   ├── plan-general.md               # Vue d'ensemble 
│   ├── arcs-narratifs.md             # Définition des arcs principaux
│   └── chronologie.md                # Ligne temporelle des événements
│
├── personnages/                      # Système de personnages
│   ├── index.md                      # Vue d'ensemble des personnages
│   ├── entites/                      # Entités fondamentales
│   │   ├── datura.md
│   │   └── ...
│   ├── manifestations/               # Avatars/manifestations
│   │   ├── tura.md 
│   │   └── ...
│   ├── mortels/                      # Personnages humains
│   │   ├── eliza.md
│   │   └── ...
│   └── secondaires/                  # Personnages mineurs
│       └── ...
│
├── lieux/                            # Environnements et décors
│   ├── reels/                        # Lieux existants
│   └── fictifs/                      # Lieux inventés
│
├── concepts/                         # Concepts narratifs clés  
│   ├── temporalite.md                # Règles du temps dans l'univers
│   ├── manifestations.md             # Comment fonctionnent les avatars
│   └── ...
│
├── references/                       # Système de références plat
│   ├── index.md                      # Navigation et catégorisation
│   ├── references.bib                # Format BibTeX pour références académiques
│   ├── oeuvres-inspirantes.md        # Littérature, films, etc.
│   ├── personnes.md                  # Auteurs, philosophes, etc.
│   ├── lieux-historiques.md          # Sites et lieux réels importants
│   └── concepts-philosophiques.md    # Théories et idées clés
│
├── styles/                           # Styles narratifs
│   ├── index.md                      # Vue d'ensemble
│   ├── registres/                    # Registres narratifs par personnage
│   │   ├── datura.md
│   │   ├── tura.md
│   │   └── ...
│   ├── transitions.md                # Matrices de transition entre styles
│   └── verification.md               # Checklist de cohérence stylistique
│
├── ressources/                       # Matériel de recherche et développement
│   ├── brainstorming/                # Sessions et idées
│   │   ├── session-2025-03-20.md
│   │   └── ...
│   ├── recherche/                    # Documentation thématique
│   │   ├── temporalite.md
│   │   └── ...
│   ├── medias/                       # Inspirations visuelles/sonores
│   │   ├── playlists/
│   │   └── moodboards/
│   └── extraits/                     # Fragments textuels inspirants
│
├── claude-sessions/                  # Interactions avec Claude
│   ├── index.md                      # Organisation des sessions
│   ├── developpement/                # Sessions de développement narratif
│   ├── personnages/                  # Sessions sur les personnages
│   ├── revision/                     # Sessions de révision
│   └── brainstorming/                # Sessions de brainstorming
│
├── tools/                            # Scripts et outils
│   ├── generation/                   # Scripts de génération
│   ├── analyse/                      # Outils d'analyse
│   └── typographie/                  # Outils typographiques
│
├── templates/                        # Modèles réutilisables
│   ├── personnage-avance.md
│   ├── chapitre.md
│   ├── reference.md                  # Nouveau template de référence
│   └── ...
│
└── export/                           # Fichiers générés
    ├── pdf/
    ├── epub/
    └── html/
```

## Templates clés

### Template de référence plat (Modèle académique adapté)

```markdown
# Template de Référence
<!-- À utiliser pour toute référence externe (littérature, personne, lieu, concept, média) -->

## Entrée

<!-- Format générique inspiré du style académique mais adapté au brainstorming créatif -->

**ID**: [Identifiant unique - ex: Rice1994, Louvre, Borges-Labyrinthe]

**Type**: [Livre | Auteur | Lieu | Concept | Film | Chanson | Article | etc.]

**Titre/Nom**: [Titre principal ou nom]

**Créateur(s)**: [Auteur | Réalisateur | Artiste | Penseur | etc. - Laisser vide si non applicable]

**Date**: [Année | Période | Époque - Format flexible]

**Source/Localisation**: [Éditeur | Pays | Ville | URL | etc. - selon pertinence]

## Description concise
<!-- 1-3 phrases décrivant l'élément et sa pertinence générale -->

## Pertinence pour le projet
<!-- En quoi cette référence est importante pour le projet littéraire -->

## Éléments clés à retenir
<!-- Liste à puces des aspects les plus importants -->
- Élément 1
- Élément 2
- Élément 3

## Citations/Extraits notables
<!-- Citations directes ou descriptions d'éléments visuels/sonores pertinents -->
> Citation ou description...

## Connexions internes
<!-- Liens vers d'autres éléments du projet reliés à cette référence -->
- [[lien-interne-1]]
- [[lien-interne-2]]

## Mots-clés
#tag1 #tag2 #tag3

## Notes additionnelles
<!-- Réflexions personnelles, idées d'utilisation, etc. -->
```

### Template de session de brainstorming

```markdown
# Session de Brainstorming: [Date-Thème]

## Participants
- [Liste des participants, incluant Claude si applicable]

## Objectifs
- [Objectif 1]
- [Objectif 2]
- [Objectif 3]

## Idées générées

### Thème 1
- Idée 1
  - Sous-idée
  - Développement potentiel
- Idée 2
  - ...

### Thème 2
- Idée 1
  - ...
- Idée 2
  - ...

## Décisions prises
- [Décision 1]
- [Décision 2]

## Éléments à explorer davantage
- [Élément 1] - Pourquoi: [Raison]
- [Élément 2] - Pourquoi: [Raison]

## Prochaines étapes
- [Action 1] - Responsable: [Nom] - Échéance: [Date]
- [Action 2] - Responsable: [Nom] - Échéance: [Date]

## Références utilisées
- [[reference-1]]
- [[reference-2]]

## Notes complémentaires
[Notes libres, réflexions, intuitions]
```

## Exemple de référence (Format plat)

```markdown
# Entretien avec le vampire (Interview with the Vampire)

## Entrée

**ID**: Rice1994-InterviewVampire

**Type**: Livre/Film

**Titre/Nom**: Entretien avec le vampire (Interview with the Vampire)

**Créateur(s)**: Anne Rice (livre), Neil Jordan (film)

**Date**: 1976 (livre), 1994 (film)

**Source/Localisation**: Alfred A. Knopf (livre), Warner Bros. (film)

## Description concise
Roman gothique et son adaptation cinématographique narrant l'histoire de Louis de Pointe du Lac, transformé en vampire par Lestat de Lioncourt, et leur relation complexe à travers les siècles, racontée à travers un entretien avec un journaliste.

## Pertinence pour le projet
L'œuvre offre un modèle de narration où un être immortel partage son expérience avec un mortel (journaliste), créant un parallèle avec la relation Datura-Eliza. Le style introspectif de Louis et la caractérisation de Lestat influencent notre approche narrative.

## Éléments clés à retenir
- Utilisation d'un cadre narratif contemporain pour explorer des existences séculaires
- Contrastes stylistiques entre les différentes époques traversées par les personnages
- Caractérisation de Lestat comme être immortel charismatique et moralement ambigu
- Technique narrative de "l'entretien" comme dispositif d'exposition
- Approche de l'immortalité comme source de mélancolie et de détachement

## Citations/Extraits notables
> "C'est comme si la mort m'avait donné une liberté qui n'appartient qu'aux enfants et aux fous." - Louis
> 
> "Le mal est un point de vue. Dieu tue indistinctement, et ainsi ferons-nous, car aucune créature sur terre n'est plus semblable à Dieu que nous." - Lestat

## Connexions internes
- [[datura]] - Inspiration pour le détachement temporel et la relation avec Eliza
- [[tura]] - Contrastes avec le personnage de Claudia (immortelle dans un corps d'enfant)
- [[styles-narratifs]] - Référence pour les transitions entre récit contemporain et historique

## Mots-clés
#immortalité #narration-cadre #introspection #relation-immortel-mortel #mélancolie

## Notes additionnelles
Le style riche et sensoriel d'Anne Rice pourrait inspirer les passages où Datura évoque ses expériences à travers les siècles. La façon dont les vampires perçoivent différemment le temps offre des parallèles intéressants avec notre concept de perception temporelle multistrate.
```

## Document d'index pour les références

```markdown
# Index des Références

Ce document organise toutes les références externes utilisées dans le projet selon différentes catégories pour faciliter la recherche et l'inspiration.

## Navigation par type

### Œuvres littéraires
- [[Rice1994-InterviewVampire]] - Entretien avec le vampire - Anne Rice
- [[Borges-Labyrinthe]] - Le Jardin aux sentiers qui bifurquent - Jorge Luis Borges
- [[SanAntonio-Selection]] - Sélection de romans San-Antonio - Frédéric Dard
- ...

### Films et séries
- [[Lynch-TwinPeaks]] - Twin Peaks - David Lynch
- [[Nolan-Interstellar]] - Interstellar - Christopher Nolan
- ...

### Musique
- [[Glass-Einstein]] - Einstein on the Beach - Philip Glass
- [[Radiohead-OKComputer]] - OK Computer - Radiohead
- ...

### Personnes
- [[Borges-JorgeLuis]] - Jorge Luis Borges
- [[Benjamin-Walter]] - Walter Benjamin
- ...

### Lieux
- [[SanFrancisco-GoldenGate]] - Golden Gate Bridge, San Francisco
- [[Paris-Passages]] - Passages couverts de Paris
- ...

### Concepts philosophiques
- [[Nietzsche-EternelRetour]] - L'Éternel Retour (Nietzsche)
- [[Bergson-Duree]] - La Durée (Bergson)
- ...

## Navigation par thème

### Temporalité
- [[Bergson-Duree]] - La Durée (Bergson)
- [[Nolan-Interstellar]] - Interstellar - Christopher Nolan
- [[Lynch-TwinPeaks]] - Twin Peaks - David Lynch
- ...

### Immortalité
- [[Rice1994-InterviewVampire]] - Entretien avec le vampire - Anne Rice
- [[Borges-Immortel]] - L'Immortel - Jorge Luis Borges
- ...

### Journalisme
- [[Woodward-Bernstein]] - Carl Woodward et Bob Bernstein
- [[Thompson-GonzoJournalism]] - Journalisme Gonzo - Hunter S. Thompson
- ...

### Style narratif
- [[SanAntonio-Selection]] - Sélection de romans San-Antonio - Frédéric Dard
- [[Woolf-MrsDalloway]] - Mrs Dalloway - Virginia Woolf
- ...

## Tags fréquemment utilisés
#temporalité #immortalité #narration #style #introspection #mythologie #journalisme #sanfrancisco #philosophie #identité

## Notes sur l'utilisation
- Les références sont conçues pour l'inspiration et la recherche rapide
- Chaque référence utilise le format standardisé du template `reference.md`
- Les connexions entre références sont maintenues dans chaque document individuel
- Pour ajouter une nouvelle référence, utilisez le template et mettez à jour cet index
```

## Mise en œuvre et intégration

Cette structure révisée du projet littéraire propose plusieurs améliorations:

1. **Organisation plus claire** avec séparation des personnages par types (entités, manifestations, mortels)

2. **Système de références plat** inspiré des bibliographies académiques mais adapté au processus créatif:
   - Format standardisé pour tous types de références
   - Organisation flexible par types et thèmes
   - Connexions avec les éléments internes du projet
   - Format suffisamment concis mais complet pour des recherches ultérieures

3. **Intégration des styles narratifs** comme section dédiée et non plus comme simple aspect des personnages

4. **Structure de brainstorming** formalisée pour capturer efficacement les sessions créatives

5. **Connexions multidirectionnelles** entre tous les éléments du projet grâce aux liens Wiki et aux tags

Pour mettre en œuvre cette structure:

1. Réorganisez progressivement vos fichiers existants selon cette nouvelle structure
2. Utilisez les templates fournis pour standardiser vos références et sessions de brainstorming
3. Maintenez l'index des références à jour en y ajoutant chaque nouvelle entrée
4. Utilisez abondamment les liens Wiki d'Obsidian pour créer des connexions entre les éléments

Cette structure supporte un processus créatif non-linéaire tout en maintenant une organisation suffisante pour retrouver facilement l'information.
