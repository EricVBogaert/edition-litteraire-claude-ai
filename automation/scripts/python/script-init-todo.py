#!/usr/bin/env python3
# init_todo_system.py
"""
Script simple pour initialiser le système de gestion des tâches (TODO).
Crée les dossiers et templates nécessaires.
"""

import os
import shutil
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('init_todo')

# Templates simplifiés
TEMPLATE_INTERVENANT = """---
nom: <% tp.system.prompt("Nom de l'intervenant") %>
role: <% tp.system.prompt("Rôle principal") %>
expertise: <% tp.system.prompt("Domaines d'expertise principaux") %>
tags: intervenant
---

# <% tp.frontmatter.nom %>

**Rôle**: <% tp.frontmatter.role %>
**Expertise**: <% tp.frontmatter.expertise %>

## Compétences

- 
- 
- 

## Tâches assignées

- 
- 
- 

## Notes

"""

TEMPLATE_TODO = """---
id: TODO-<% Math.random().toString(36).substring(2, 7).toUpperCase() %>
titre: <% tp.system.prompt("Titre de la tâche") %>
statut: À faire
priorite: <% tp.system.prompt("Priorité (1-5, 1 étant la plus haute)", "3") %>
date_creation: <% tp.date.now("YYYY-MM-DD") %>
date_debut: <% tp.system.prompt("Date de début (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD")) %>
date_fin: <% tp.system.prompt("Date de fin prévue (YYYY-MM-DD)") %>
tags: tâche
---

# <% tp.frontmatter.titre %> [<% tp.frontmatter.id %>]

**Statut**: À faire
**Priorité**: <% tp.frontmatter.priorite %>/5
**Période**: <% tp.frontmatter.date_debut %> → <% tp.frontmatter.date_fin %>

## Description

<% tp.system.prompt("Description brève de la tâche") %>

## Sous-tâches

- [ ] 
- [ ] 
- [ ] 

## Intervenants assignés

- [[]]
- [[]]

## Ressources nécessaires

- 
- 

## Notes

"""

TEMPLATE_GANTT = """---
titre: <% tp.system.prompt("Titre du diagramme de Gantt") %>
date_debut: <% tp.system.prompt("Date de début du projet (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD")) %>
date_fin: <% tp.system.prompt("Date de fin du projet (YYYY-MM-DD)") %>
tags: gantt, planification
---

# <% tp.frontmatter.titre %>

**Période**: <% tp.frontmatter.date_debut %> → <% tp.frontmatter.date_fin %>

## Diagramme de Gantt

```mermaid
gantt
    title <% tp.frontmatter.titre %>
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    todayMarker on
    
    section Phase 1
    Tâche 1 :TODO-AAAAA, 2025-03-20, 3d
    Tâche 2 :TODO-BBBBB, after TODO-AAAAA, 5d
    
    section Phase 2
    Tâche 3 :TODO-CCCCC, after TODO-BBBBB, 4d
    Tâche 4 :TODO-DDDDD, 2025-03-26, 3d
```

## Liste des tâches

| ID | Tâche | Dates | Intervenants |
|---|---|---|---|
| TODO-AAAAA | Tâche 1 | 2025-03-20 → 2025-03-23 | [[nom-intervenant]] |
| TODO-BBBBB | Tâche 2 | 2025-03-23 → 2025-03-28 | [[nom-intervenant]] |
| TODO-CCCCC | Tâche 3 | 2025-03-28 → 2025-04-01 | [[nom-intervenant]] |
| TODO-DDDDD | Tâche 4 | 2025-03-26 → 2025-03-29 | [[nom-intervenant]] |

## Notes de planification

"""

GUIDE_UTILISATION = """# Guide d'utilisation du système TODO simplifié

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
"""

def create_todo_system(project_path):
    """
    Crée la structure minimale nécessaire pour le système de gestion des tâches.
    
    Args:
        project_path (Path): Chemin du projet littéraire
    """
    logger.info(f"Initialisation du système TODO dans: {project_path}")
    
    # Créer les dossiers nécessaires s'ils n'existent pas déjà
    folders = [
        project_path / "templates",
        project_path / "review" / "pending",
        project_path / "review" / "in_progress",
        project_path / "review" / "completed"
    ]
    
    for folder in folders:
        if not folder.exists():
            logger.info(f"Création du dossier: {folder}")
            folder.mkdir(parents=True, exist_ok=True)
        else:
            logger.info(f"Le dossier existe déjà: {folder}")
    
    # Créer les templates
    templates = {
        "intervenant.md": TEMPLATE_INTERVENANT,
        "todo.md": TEMPLATE_TODO,
        "gantt.md": TEMPLATE_GANTT
    }
    
    templates_dir = project_path / "templates"
    for filename, content in templates.items():
        file_path = templates_dir / filename
        if not file_path.exists():
            logger.info(f"Création du template: {file_path}")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        else:
            logger.info(f"Le template existe déjà: {file_path}")
    
    # Créer le guide d'utilisation
    guide_path = project_path / "todo-guide.md"
    if not guide_path.exists():
        logger.info(f"Création du guide d'utilisation: {guide_path}")
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(GUIDE_UTILISATION)
    else:
        logger.info(f"Le guide d'utilisation existe déjà: {guide_path}")
    
    logger.info("Initialisation du système TODO terminée!")
    logger.info("\nProchaines étapes:")
    logger.info("1. Dans Obsidian, vérifiez que le plugin Templater est installé et configuré")
    logger.info("2. Consultez le guide d'utilisation dans todo-guide.md")
    logger.info("3. Créez votre première tâche en utilisant le template todo.md")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1]).resolve()
    else:
        project_path = Path.cwd().resolve()
    
    create_todo_system(project_path)
