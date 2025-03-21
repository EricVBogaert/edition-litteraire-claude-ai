#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'intégration pour fusionner les modules et créer le script amélioré complet
"""

import os
import re
import importlib.util
import argparse
from pathlib import Path

def extract_functions_from_file(filepath):
    """
    Extrait toutes les définitions de fonctions d'un fichier Python.
    
    Args:
        filepath (str): Chemin du fichier source
        
    Returns:
        list: Liste des fonctions extraites avec leur code
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire les imports
    module_pattern = r'(from\s+[\w.]+\s+import\s+[\w,\s]+|import\s+[\w,\s.]+)'
    imports = re.findall(module_pattern, content)
    
    # Extraire les définitions de classes
    class_pattern = r'(class\s+\w+\([^)]*\):\n(?:[ \t].*\n)*)'
    classes = re.findall(class_pattern, content)
    
    # Extraire les définitions de fonctions
    function_pattern = r'(def\s+\w+\([^)]*\):\n(?:[ \t].*\n|\n)*)'
    functions = re.findall(function_pattern, content)
    
    return {'imports': imports, 'classes': classes, 'functions': functions}

def merge_scripts(source_files, output_file):
    """
    Fusionne plusieurs scripts Python en un seul.
    
    Args:
        source_files (list): Liste des chemins des fichiers source
        output_file (str): Chemin du fichier de sortie
        
    Returns:
        bool: True si la fusion a réussi, False sinon
    """
    try:
        parts = []
        
        # En-tête du fichier fusionné
        header = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script amélioré de vérification et correction de structure pour les projets d'édition littéraire

Ce script combine les fonctionnalités de détection de problèmes de structure et de correction automatique,
avec une approche par lots pour gérer efficacement les problèmes similaires et une prioritisation
intelligente des corrections.

Utilisation:
    python verify_structure_improved.py [options]

Options:
    --project-dir PATH      Chemin vers le répertoire du projet (défaut: répertoire courant)
    --mode MODE            Mode de fonctionnement: 'analyze', 'report', 'fix' ou 'interactive' 
                          (défaut: analyze)
    --verbose              Affiche des informations détaillées pendant l'exécution
    --output FILE          Chemin vers le fichier de sortie pour le rapport 
                          (défaut: structure-report.md)
    --yes, -y              Mode non-interactif: répond 'oui' à toutes les questions
\"\"\"

# Imports standard
import os
import sys
import re
import json
import yaml
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("structure_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('structure_verification')

"""
        parts.append(header)
        
        # Extraire et ajouter les constantes et les fonctions des scripts originaux
        for source_file in source_files:
            print(f"Traitement de {source_file}...")
            
            # Extraire les constantes directement du module
            try:
                # Importer dynamiquement le module
                module_name = os.path.basename(source_file).split('.')[0]
                spec = importlib.util.spec_from_file_location(module_name, source_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Extraire les constantes
                constants = {}
                for name in dir(module):
                    if name.isupper() and not name.startswith('__'):
                        constants[name] = getattr(module, name)
                
                # Ajouter les constantes au script fusionné
                for name, value in constants.items():
                    parts.append(f"\n# Constant importé depuis {module_name}")
                    parts.append(f"{name} = {repr(value)}")
            except Exception as e:
                print(f"Erreur lors de l'extraction des constantes de {source_file}: {e}")
            
            # Extraire les fonctions
            extracted = extract_functions_from_file(source_file)
            for function in extracted['functions']:
                parts.append("\n" + function)
        
        # Ajouter la fonction main() et le bloc if __name__ == "__main__" depuis le dernier fichier
        # (assumant que c'est le fichier principal avec la fonction main())
        main_file = source_files[-1]
        with open(main_file, 'r', encoding='utf-8') as f:
            main_content = f.read()
        
        # Extraire la fonction main()
        main_match = re.search(r'def main\(\):(.*?)def ', main_content, re.DOTALL)
        if main_match:
            main_function = "def main():" + main_match.group(1)
            parts.append("\n" + main_function)
        
        # Extraire le bloc if __name__ == "__main__"
        main_block_match = re.search(r'if __name__ == "__main__":(.*?)$', main_content, re.DOTALL)
        if main_block_match:
            main_block = 'if __name__ == "__main__":' + main_block_match.group(1)
            parts.append("\n" + main_block)
        
        # Écrire le fichier fusionné
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
        
        print(f"Script fusionné créé avec succès: {output_file}")
        return True
    except Exception as e:
        print(f"Erreur lors de la fusion des scripts: {e}")
        return False

def create_integration_script():
    """
    Crée un script qui intègre les fonctions des modules précédents
    avec le script de vérification de structure original.
    
    Returns:
        str: Chemin du script d'intégration créé
    """
    integration_code = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script d'intégration pour les améliorations de vérification de structure
\"\"\"

import os
import sys
import importlib.util
from pathlib import Path

def load_module(filepath):
    \"\"\"Charge dynamiquement un module Python.\"\"\"
    module_name = os.path.basename(filepath).split('.')[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    # Vérifier que tous les modules nécessaires sont présents
    script_dir = Path(__file__).parent
    
    module_paths = {
        'original': script_dir / 'verify-structure-script.py',
        'part1': script_dir / 'verify-structure-improved-part1.py',
        'part2': script_dir / 'verify-structure-improved-part2.py',
        'part3': script_dir / 'verify-structure-improved-part3.py'
    }
    
    # Vérifier l'existence des fichiers
    for name, path in module_paths.items():
        if not path.exists():
            print(f"Erreur: Le module {name} ({path}) est introuvable.")
            return 1
    
    # Créer le script fusionné
    output_path = script_dir / 'verify-structure-improved.py'
    
    source_files = [
        str(module_paths['part1']),
        str(module_paths['part2']),
        str(module_paths['part3'])
    ]
    
    if merge_scripts(source_files, str(output_path)):
        # Rendre le script exécutable
        try:
            os.chmod(output_path, 0o755)
        except Exception:
            # Ignorer les erreurs sur Windows
            pass
        
        print("Script d'intégration terminé avec succès!")
        print(f"Script amélioré créé: {output_path}")
        print("\\nUtilisation:")
        print(f"python {output_path} --mode interactive --project-dir [CHEMIN_DU_PROJET]")
        return 0
    else:
        print("Erreur lors de la création du script intégré.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
"""
    
    output_path = "integrate_structure_improvements.py"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    # Rendre le script exécutable
    try:
        os.chmod(output_path, 0o755)
    except Exception:
        # Ignorer les erreurs sur Windows
        pass
    
    return output_path

def create_readme():
    """
    Crée un fichier README expliquant les améliorations et leur utilisation.
    
    Returns:
        str: Chemin du fichier README créé
    """
    readme_content = """# Améliorations du Script de Vérification de Structure

Ce package contient des améliorations significatives pour le script de vérification de structure des projets d'édition littéraire.

## Fichiers inclus

1. `verify-structure-improved-part1.py` - Améliorations pour la détection et correction des liens cassés
2. `verify-structure-improved-part2.py` - Traitement par lots et prioritisation des problèmes
3. `verify-structure-improved-part3.py` - Exécution du plan de correction et intégration avec le script original
4. `integrate_structure_improvements.py` - Script pour fusionner les modules en un script unique

## Nouvelles fonctionnalités

### 1. Amélioration de la correction des liens cassés
- Détection intelligente de chemins relatifs incorrects
- Recherche de fichiers similaires dans tout le projet
- Correction automatique des préfixes communs problématiques
- Création automatique de fichiers manquants à partir de templates

### 2. Traitement par lots des problèmes similaires
- Regroupement des problèmes par motifs récurrents
- Interface de correction par lots pour gérer efficacement de nombreux problèmes
- Options pour appliquer les mêmes corrections à plusieurs fichiers

### 3. Prioritisation des problèmes
- Classement intelligent des problèmes par ordre d'importance
- Plan de correction étape par étape pour une résolution optimale
- Traitement prioritaire des problèmes structurels critiques

### 4. Nouveau mode "interactive"
- Interface utilisateur améliorée pour guider les corrections
- Confirmation étape par étape pour un contrôle précis
- Suggestions intelligentes pour chaque type de problème

## Installation

1. Placez tous les fichiers dans le même répertoire que le script `verify-structure-script.py` original
2. Exécutez le script d'intégration pour créer le script amélioré complet:
   ```
   python integrate_structure_improvements.py
   ```
3. Le script créera un fichier `verify-structure-improved.py` prêt à l'emploi

## Utilisation

```
python verify-structure-improved.py --mode interactive --project-dir [CHEMIN_DU_PROJET]
```

### Options

- `--mode analyze` - Analyse simple sans modifications (par défaut)
- `--mode report` - Analyse et génération de rapports de tâches
- `--mode fix` - Corrections automatiques avec confirmation globale
- `--mode interactive` - Corrections guidées avec confirmations détaillées
- `--yes` ou `-y` - Mode non-interactif (répond 'oui' à toutes les confirmations)
- `--verbose` - Affiche des informations détaillées pendant l'exécution
- `--output FILE` - Spécifie le chemin du fichier de rapport

## Exemple d'utilisation

```
# Analyse simple
python verify-structure-improved.py --project-dir ~/mon-projet

# Correction interactive avec confirmations
python verify-structure-improved.py --mode interactive --project-dir ~/mon-projet

# Correction automatique complète sans confirmations
python verify-structure-improved.py --mode fix --yes --project-dir ~/mon-projet
```

## Notes importantes

1. Créez toujours une sauvegarde avant d'appliquer des corrections automatiques
2. Commencez par le mode `interactive` pour vous familiariser avec les options
3. Vérifiez le rapport généré après l'exécution pour voir les problèmes restants

"""
    
    output_path = "README-structure-improvements.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    return output_path

def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description="Crée les scripts d'intégration pour les améliorations de vérification de structure.")
    parser.add_argument("--build", action="store_true", help="Construit directement le script intégré")
    args = parser.parse_args()
    
    # Créer le script d'intégration
    integration_script = create_integration_script()
    print(f"Script d'intégration créé: {integration_script}")
    
    # Créer le README
    readme_path = create_readme()
    print(f"Documentation créée: {readme_path}")
    
    # Si --build est spécifié, exécuter directement le script d'intégration
    if args.build:
        print("\nConstruction du script intégré...")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        source_files = [
            os.path.join(current_dir, "verify-structure-improved-part1.py"),
            os.path.join(current_dir, "verify-structure-improved-part2.py"),
            os.path.join(current_dir, "verify-structure-improved-part3.py")
        ]
        output_file = os.path.join(current_dir, "verify-structure-improved.py")
        
        if merge_scripts(source_files, output_file):
            # Rendre le script exécutable
            try:
                os.chmod(output_file, 0o755)
            except Exception:
                # Ignorer les erreurs sur Windows
                pass
            
            print("\nScript amélioré construit avec succès!")
            print(f"Fichier créé: {output_file}")
            print("\nUtilisation:")
            print(f"python {output_file} --mode interactive --project-dir [CHEMIN_DU_PROJET]")
        else:
            print("Échec de la construction du script intégré.")
    else:
        print("\nPour construire le script intégré, exécutez:")
        print(f"python {integration_script}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Fonction merge_scripts importée du haut du fichier pour référence
def merge_scripts(source_files, output_file):
    """
    Fusionne plusieurs scripts Python en un seul.
    
    Args:
        source_files (list): Liste des chemins des fichiers source
        output_file (str): Chemin du fichier de sortie
        
    Returns:
        bool: True si la fusion a réussi, False sinon
    """
    try:
        parts = []
        
        # En-tête du fichier fusionné
        header = """#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
Script amélioré de vérification et correction de structure pour les projets d'édition littéraire

Ce script combine les fonctionnalités de détection de problèmes de structure et de correction automatique,
avec une approche par lots pour gérer efficacement les problèmes similaires et une prioritisation
intelligente des corrections.

Utilisation:
    python verify_structure_improved.py [options]

Options:
    --project-dir PATH      Chemin vers le répertoire du projet (défaut: répertoire courant)
    --mode MODE            Mode de fonctionnement: 'analyze', 'report', 'fix' ou 'interactive' 
                          (défaut: analyze)
    --verbose              Affiche des informations détaillées pendant l'exécution
    --output FILE          Chemin vers le fichier de sortie pour le rapport 
                          (défaut: structure-report.md)
    --yes, -y              Mode non-interactif: répond 'oui' à toutes les questions
\"\"\"

# Imports standard
import os
import sys
import re
import json
import yaml
import logging
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("structure_verification.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('structure_verification')

"""
        parts.append(header)
        
        # Ajouter le contenu des fichiers source
        for source_file in source_files:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Enlever les lignes d'importation et de configuration du logging
                content = re.sub(r'^\s*import\s+.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^\s*from\s+.*import.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'^\s*logger\s*=.*$', '', content, flags=re.MULTILINE)
                content = re.sub(r'logging\.basicConfig.*?\)', '', content, flags=re.DOTALL)
                
                parts.append(content)
        
        # Ajouter une section finale avec le bloc if __name__ == "__main__"
        footer = """

# Section principale
if __name__ == "__main__":
    sys.exit(main())
"""
        parts.append(footer)
        
        # Écrire le fichier fusionné
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(parts))
        
        return True
    except Exception as e:
        print(f"Erreur lors de la fusion des scripts: {e}")
        return False
