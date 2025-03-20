# Guide d'utilisation du système TODO simplifié

Ce guide explique comment utiliser le système de gestion de tâches simplifié dans votre projet littéraire.

## Structure recommandée

```
mon-projet-litteraire/
├── review/
│   ├── pending/           # Tâches à faire
│   │   ├── TODO-A1B2C.md  # Tâche avec ID unique
│   │   └── ...
│   ├── in_progress/       # Tâches en cours
│   ├── completed/         # Tâches terminées
│   └── ...
├── templates/
│   ├── intervenant.md     # Template pour les intervenants
│   ├── todo.md            # Template pour les tâches
│   ├── gantt.md           # Template pour les diagrammes Gantt
│   └── ...
└── ...
```

## Utilisation des templates

### 1. Création d'un intervenant

1. Créez une nouvelle note avec le template `intervenant.md`
2. Remplissez les informations de base (3 prompts seulement)
3. Complétez manuellement les sections restantes (compétences, tâches assignées)
4. Enregistrez la note où vous le souhaitez (dossier de votre choix)

### 2. Création d'une tâche TODO

1. Créez une nouvelle note avec le template `todo.md`
2. Un ID unique est automatiquement généré dans le frontmatter
3. Remplissez les informations de base (4 prompts seulement)
4. Ajoutez manuellement les sous-tâches et les liens vers les intervenants
5. Enregistrez la note dans `/review/pending/`

### 3. Création d'un diagramme de Gantt

1. Créez une nouvelle note avec le template `gantt.md`
2. Remplissez les dates de début et de fin du projet
3. Modifiez manuellement l'exemple de diagramme Mermaid pour inclure vos tâches
4. Mettez à jour le tableau des tâches en dessous du diagramme
5. Enregistrez la note où vous le souhaitez

## Workflow de gestion des tâches

1. **Création** : Créez les tâches dans le dossier `/review/pending/`
2. **Suivi** : Quand vous commencez à travailler sur une tâche, déplacez-la dans `/review/in_progress/`
3. **Achèvement** : Une fois terminée, déplacez la tâche dans `/review/completed/`

## Bonnes pratiques simplifiées

### Identification des tâches
- Utilisez toujours les IDs uniques (format `TODO-XXXXX`) pour référencer les tâches
- Dans le diagramme Gantt, utilisez ces IDs pour identifier clairement chaque tâche

### Liens entre éléments
- Utilisez la syntaxe Wiki d'Obsidian (`[[nom-intervenant]]`) pour établir des liens
- Ajoutez les liens des intervenants dans chaque tâche pour faciliter le suivi

### Organisation du travail
- Utilisez les statuts clairs (À faire, En cours, Terminée)
- Numérotez les priorités de 1 (haute) à 5 (basse)
- Utilisez des dates au format YYYY-MM-DD pour assurer la compatibilité

## Utilisation d'Obsidian pour le suivi

### Recherches utiles

- `tag:tâche "statut: À faire"`  
  Trouve toutes les tâches encore à réaliser

- `line:(priorite: 1)` ou `line:(priorite: 2)`  
  Trouve les tâches de haute priorité

- `[[nom-intervenant]]`  
  Trouve toutes les notes qui font référence à cet intervenant

### Vue graphique

Le graphe d'Obsidian vous permet de visualiser les relations entre intervenants et tâches :

- Activez la vue graphe (icône dans la barre latérale)
- Filtrez par tag (`#tâche` ou `#intervenant`)
- Observez les connexions pour identifier les intervenants surchargés

Ce système simplifié vous permet de maintenir une organisation efficace de votre projet sans vous perdre dans la complexité de configurations avancées.
