# STRUCTURE POUR SCRIPTS ET AUTOMATISATION

Cette section détaille l'organisation des scripts, des outils d'automatisation et des workflows d'intégration pour le projet littéraire, incluant l'interaction avec des API comme Claude.

## Organisation révisée des dossiers

```
mon-projet-litteraire/
├── ...
├── automation/                      # Dossier central pour tous les scripts et automatisations
│   ├── scripts/                     # Scripts principaux d'automatisation
│   │   ├── python/                  # Scripts Python
│   │   │   ├── compile.py           # Assemblage des chapitres
│   │   │   ├── analyze.py           # Analyse stylistique
│   │   │   ├── extract_for_claude.py # Extraction pour soumission à Claude
│   │   │   └── ...
│   │   ├── bash/                    # Scripts shell (Bash)
│   │   │   ├── git_workflow.sh      # Automatisation des opérations Git
│   │   │   ├── build_all.sh         # Construction complète du projet
│   │   │   └── ...
│   │   └── js/                      # Scripts JavaScript (pour intégration web)
│   │       └── ...
│   │
│   ├── config/                      # Fichiers de configuration pour les scripts
│   │   ├── paths.json               # Configuration des chemins
│   │   ├── api_keys.json.template   # Template pour les clés API (sans clés réelles)
│   │   ├── build_settings.yaml      # Paramètres de construction
│   │   └── style_rules.json         # Règles pour la vérification stylistique
│   │
│   ├── hooks/                       # Hooks Git pour workflow automatisé
│   │   ├── pre-commit               # Vérifications avant commit
│   │   └── post-merge               # Actions après merge
│   │
│   ├── templates/                   # Templates utilisés par les scripts
│   │   ├── review_request.md        # Structure d'une demande de révision
│   │   ├── claude_prompt.md         # Template de prompt pour Claude
│   │   └── ...
│   │
│   └── docs/                        # Documentation des scripts et workflows
│       ├── README.md                # Vue d'ensemble
│       ├── setup.md                 # Instructions d'installation
│       └── workflows.md             # Documentation des workflows disponibles
│
├── review/                          # Système de révision collaborative
│   ├── pending/                     # Éléments en attente de révision
│   │   ├── [YYYY-MM-DD]-[element]-[id].md  # Format standard de soumission
│   │   └── ...
│   ├── in_progress/                 # Révisions en cours
│   │   └── ...
│   ├── completed/                   # Révisions terminées
│   │   └── ...
│   ├── claude_suggestions/          # Suggestions générées par Claude
│   │   ├── [YYYY-MM-DD]-[element]-[id].md
│   │   └── ...
│   └── templates/                   # Templates spécifiques aux révisions
│       ├── review_form.md           # Formulaire de révision
│       └── acceptance_criteria.md   # Critères d'acceptation
│
├── .github/                         # Configuration pour GitHub (si utilisé)
│   └── workflows/                   # GitHub Actions
│       ├── build.yml                # Workflow de construction
│       ├── style_check.yml          # Vérification de style
│       └── claude_integration.yml   # Intégration avec l'API Claude
├── ...
```

## Description des composants clés

### 1. Dossier `automation/scripts/`

Ce dossier contient tous les scripts exécutables organisés par langage.

#### Exemples de scripts Python essentiels

```python
# compile.py - Assemblage du manuscrit
import os, json, argparse
from pathlib import Path

def load_config():
    """Charge la configuration des chemins et des paramètres"""
    config_path = Path(__file__).parent.parent / "config" / "paths.json"
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def compile_manuscript(output_format='markdown', chapters=None):
    """Assemble les chapitres spécifiés dans un document unique"""
    config = load_config()
    chapters_dir = Path(config['paths']['chapitres'])
    output_dir = Path(config['paths']['export'])
    
    # Logique d'assemblage...
    
    print(f"Manuscrit compilé avec succès dans {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile les chapitres en un manuscrit unique")
    parser.add_argument("--format", choices=["markdown", "docx", "pdf", "epub"], default="markdown", 
                        help="Format de sortie")
    parser.add_argument("--chapters", nargs="+", help="Chapitres spécifiques à compiler")
    args = parser.parse_args()
    
    compile_manuscript(args.format, args.chapters)
```

```python
# extract_for_claude.py - Extraction pour soumission à Claude
import os, json, argparse
from pathlib import Path

def extract_for_claude(element_type, element_id, context_size=1):
    """Extrait un élément et son contexte pour soumission à Claude"""
    config = load_config()
    
    # Déterminer le chemin selon le type d'élément
    if element_type == "chapitre":
        element_path = Path(config['paths']['chapitres']) / f"{element_id}.md"
    elif element_type == "personnage":
        element_path = Path(config['paths']['personnages']) / f"{element_id}.md"
    # etc.
    
    # Extraire le contenu et le contexte
    
    # Générer le prompt pour Claude selon le template
    template_path = Path(__file__).parent.parent / "templates" / "claude_prompt.md"
    with open(template_path, 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Remplir le template
    prompt = prompt_template.format(
        element_type=element_type,
        element_id=element_id,
        content=content,
        # Autres variables
    )
    
    # Enregistrer dans le dossier de révision
    output_path = Path(config['paths']['review']) / "pending" / f"{date.today()}-{element_type}-{element_id}.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"Extrait préparé pour Claude: {output_path}")
    # Optionnel: Soumission directe à l'API Claude

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrait un élément pour soumission à Claude")
    parser.add_argument("type", choices=["chapitre", "personnage", "scene", "concept"], 
                        help="Type d'élément à extraire")
    parser.add_argument("id", help="Identifiant de l'élément")
    parser.add_argument("--context", type=int, default=1, help="Taille du contexte à inclure")
    args = parser.parse_args()
    
    extract_for_claude(args.type, args.id, args.context)
```

#### Exemple de script Bash pour workflow Git

```bash
#!/bin/bash
# git_workflow.sh - Automatisation des opérations Git courantes

function help {
    echo "Usage: ./git_workflow.sh [command]"
    echo "Commands:"
    echo "  sync        - Pull changes, stash local changes if needed"
    echo "  snapshot    - Create a snapshot of current work"
    echo "  chapter     - Prepare a chapter for review"
    echo "  backup      - Create and push a backup branch"
}

function sync {
    echo "Synchronizing with remote repository..."
    git fetch
    
    # Check if we have local changes
    if [[ $(git status --porcelain) ]]; then
        echo "Local changes detected, stashing..."
        git stash
        git pull
        git stash pop
        echo "Local changes reapplied."
    else
        git pull
        echo "Repository synchronized."
    fi
}

function snapshot {
    # Create a dated snapshot of the current work
    DATE=$(date +"%Y-%m-%d_%H-%M")
    BRANCH="snapshot/$DATE"
    
    echo "Creating snapshot branch: $BRANCH"
    git checkout -b "$BRANCH"
    git add .
    git commit -m "Snapshot: $DATE"
    
    echo "Snapshot created. Use 'git checkout main' to return to main branch."
}

# Fonction principale
case "$1" in
    "sync")
        sync
        ;;
    "snapshot")
        snapshot
        ;;
    # Autres commandes...
    *)
        help
        ;;
esac
```

### 2. Intégration avec l'API Claude

```python
# claude_api.py - Intégration avec l'API Claude
import os, json, requests
from pathlib import Path

def load_api_config():
    """Charge la configuration de l'API Claude"""
    config_path = Path(__file__).parent.parent / "config" / "api_keys.json"
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration API introuvable: {config_path}")
        print("Copiez api_keys.json.template vers api_keys.json et ajoutez votre clé API.")
        exit(1)

def submit_to_claude(prompt, model="claude-3-opus-20240229"):
    """Soumet un prompt à l'API Claude et retourne la réponse"""
    config = load_api_config()
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config["claude"]["api_key"],
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4000
    }
    
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        return response.json()["content"][0]["text"]
    else:
        print(f"Erreur API Claude: {response.status_code}")
        print(response.text)
        return None

def process_review_request(request_path):
    """Traite une demande de révision avec Claude"""
    # Charger la demande
    with open(request_path, 'r', encoding='utf-8') as f:
        request_content = f.read()
    
    # Extraire les métadonnées (supposées en YAML frontmatter)
    # ...
    
    # Soumettre à Claude
    response = submit_to_claude(request_content)
    
    if response:
        # Créer le fichier de suggestion
        filename = os.path.basename(request_path)
        output_path = Path(__file__).parent.parent.parent / "review" / "claude_suggestions" / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"""# Suggestion de Claude
            
## Demande originale
```
{request_content}
```

## Réponse de Claude
{response}
            """)
        
        print(f"Suggestion enregistrée dans {output_path}")
        
        # Mettre à jour le statut de la demande
        # ...
```

### 3. Workflow d'intégration des révisions

```python
# integrate_review.py - Intégration des révisions approuvées
import os, json, argparse, shutil
from pathlib import Path
from datetime import datetime

def integrate_review(review_id, accept=False):
    """Intègre une révision au projet principal"""
    config = load_config()
    
    # Chemin de la révision
    review_path = Path(config['paths']['review']) / "completed" / f"{review_id}.md"
    
    if not review_path.exists():
        print(f"Révision non trouvée: {review_path}")
        return False
    
    # Charger la révision
    with open(review_path, 'r', encoding='utf-8') as f:
        review_content = f.read()
    
    # Extraire les métadonnées
    # ...
    
    # Déterminer le chemin du fichier cible
    target_path = Path(config['paths'][target_type]) / f"{target_id}.md"
    
    if not target_path.exists():
        print(f"Fichier cible non trouvé: {target_path}")
        return False
    
    # Créer une sauvegarde
    backup_path = target_path.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d%H%M%S')}")
    shutil.copy2(target_path, backup_path)
    
    if accept:
        # Intégrer les modifications
        # ...
        print(f"Révision intégrée: {target_path}")
    else:
        # Afficher les différences pour vérification manuelle
        # ...
        print(f"Modifications préparées pour intégration manuelle")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Intègre une révision approuvée")
    parser.add_argument("review_id", help="Identifiant de la révision")
    parser.add_argument("--accept", action="store_true", help="Accepter automatiquement les modifications")
    args = parser.parse_args()
    
    integrate_review(args.review_id, args.accept)
```

## Système de révision collaboratif

Le dossier `review/` est organisé pour faciliter un workflow de révision clair:

1. **Soumission (`pending/`)**:
   - Les éléments sont extraits et formatés pour révision
   - Inclut les soumissions manuelles et celles préparées pour Claude

2. **Révision en cours (`in_progress/`)**:
   - Éléments actuellement en cours de révision
   - Peut inclure des commentaires intermédiaires

3. **Révisions terminées (`completed/`)**:
   - Révisions finalisées prêtes à être intégrées
   - Contient l'historique des révisions

4. **Suggestions de Claude (`claude_suggestions/`)**:
   - Réponses générées par l'API Claude
   - Nécessitent validation humaine avant intégration

### Format standard d'une demande de révision

```markdown
---
id: chapitre-01-revision-2
type: chapitre
target: chapitre-01
created: 2025-03-21
author: nom_auteur
status: pending
focus: 
  - cohérence_personnage
  - style_narratif
---

# Demande de révision: Chapitre 1

## Contexte
Ce chapitre introduit la rencontre entre Eliza et Datura. Je souhaite vérifier la cohérence du style narratif de Datura et la crédibilité de la réaction d'Eliza.

## Contenu à réviser

```markdown
[Contenu du chapitre ou de la section à réviser]
```

## Questions spécifiques
1. Est-ce que les transitions entre le style "déesse millénaire" et "adolescente" de Datura sont fluides?
2. La réaction d'Eliza semble-t-elle crédible?
3. Le rythme de la révélation est-il approprié?

## Notes additionnelles
J'hésite sur la quantité d'informations à révéler dès ce premier chapitre. Je souhaite maintenir un certain mystère tout en donnant suffisamment d'éléments pour captiver le lecteur.
```

## Intégration avec GitHub Actions

Pour les projets hébergés sur GitHub, le fichier `.github/workflows/claude_integration.yml` pourrait automatiser l'interaction avec Claude:

```yaml
name: Claude API Integration

on:
  push:
    paths:
      - 'review/pending/*.md'
  workflow_dispatch:
    inputs:
      file_path:
        description: 'Path to the file to be reviewed'
        required: true

jobs:
  submit_to_claude:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests pyyaml
          
      - name: Process review requests
        env:
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}
        run: |
          python automation/scripts/python/batch_claude_process.py
          
      - name: Commit Claude suggestions
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add review/claude_suggestions/*.md
          git commit -m "Add Claude API suggestions" || echo "No changes to commit"
          git push
```

## Notes d'implémentation

1. **Sécurité des API keys**:
   - Ne jamais committer les clés API directement
   - Utiliser des variables d'environnement ou des secrets GitHub
   - Fournir des templates avec des instructions claires

2. **Documentation complète**:
   - Documenter chaque script avec des commentaires explicites
   - Créer des README détaillés pour chaque dossier principal
   - Inclure des exemples d'utilisation pour les commandes principales

3. **Configuration centralisée**:
   - Utiliser des fichiers de configuration externes pour les chemins et paramètres
   - Éviter les valeurs codées en dur dans les scripts
   - Permettre la personnalisation sans modifier les scripts eux-mêmes

4. **Tests et validation**:
   - Ajouter des tests unitaires pour les fonctions critiques
   - Inclure des validations pour éviter les modifications destructives accidentelles
   - Créer des scripts de vérification d'intégrité du projet

Cette structure d'automatisation complète le projet littéraire en facilitant:
- L'assemblage du manuscrit dans différents formats
- La révision collaborative avec intégration de l'IA
- La gestion des versions et des sauvegardes
- La cohérence stylistique et structurelle
