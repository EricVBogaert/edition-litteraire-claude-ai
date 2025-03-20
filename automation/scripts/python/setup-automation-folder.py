#!/usr/bin/env python3
# setup_automation_structure.py
"""
Ce script met à jour la structure d'un projet littéraire existant
pour intégrer la nouvelle architecture d'automatisation.
"""

import os
import sys
import shutil
from pathlib import Path
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('setup_automation')

# Définition de la nouvelle structure d'automatisation
AUTOMATION_STRUCTURE = {
    'automation': {
        'scripts': {
            'python': {},
            'bash': {},
            'js': {}
        },
        'config': {},
        'hooks': {},
        'templates': {},
        'docs': {'README.md': "# Documentation des scripts d'automatisation\n\nCe dossier contient la documentation pour les scripts et workflows d'automatisation."}
    },
    'review': {
        'pending': {},
        'in_progress': {},
        'completed': {},
        'claude_suggestions': {},
        'templates': {}
    }
}

def create_directory_structure(base_path, structure, existing_scripts=None):
    """
    Crée récursivement la structure de répertoires et fichiers définie.
    
    Args:
        base_path (Path): Chemin de base où créer la structure
        structure (dict): Dictionnaire représentant la structure à créer
        existing_scripts (dict, optional): Dictionnaire des scripts existants à déplacer
    """
    for name, content in structure.items():
        current_path = base_path / name
        
        # Si c'est un fichier (contenu est une chaîne)
        if isinstance(content, str):
            if not current_path.exists():
                logger.info(f"Création du fichier: {current_path}")
                with open(current_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                logger.info(f"Le fichier existe déjà: {current_path}")
        # Si c'est un dossier (contenu est un dictionnaire)
        else:
            if not current_path.exists():
                logger.info(f"Création du dossier: {current_path}")
                current_path.mkdir(parents=True, exist_ok=True)
            else:
                logger.info(f"Le dossier existe déjà: {current_path}")
            
            # Récursion pour créer la structure interne
            create_directory_structure(current_path, content, existing_scripts)

def find_existing_scripts(project_path):
    """
    Parcourt le projet existant pour trouver des scripts à migrer vers la nouvelle structure.
    
    Args:
        project_path (Path): Chemin du projet à analyser
        
    Returns:
        dict: Dictionnaire des scripts trouvés avec leur type et chemin
    """
    existing_scripts = {
        'python': [],
        'bash': [],
        'js': []
    }
    
    # Extensions à rechercher
    extensions = {
        '.py': 'python',
        '.sh': 'bash',
        '.js': 'js'
    }
    
    # Dossiers à exclure de la recherche
    excluded_dirs = {'.git', 'venv', 'env', '__pycache__', 'node_modules', 'export'}
    
    for root, dirs, files in os.walk(project_path):
        # Exclure les dossiers non désirés
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        
        for file in files:
            _, ext = os.path.splitext(file)
            if ext in extensions:
                script_type = extensions[ext]
                script_path = os.path.join(root, file)
                existing_scripts[script_type].append(script_path)
    
    return existing_scripts

def propose_script_migration(project_path, scripts):
    """
    Propose à l'utilisateur de migrer les scripts existants vers la nouvelle structure.
    
    Args:
        project_path (Path): Chemin du projet
        scripts (dict): Dictionnaire des scripts trouvés
    """
    automation_path = project_path / 'automation' / 'scripts'
    
    for script_type, script_list in scripts.items():
        if not script_list:
            continue
            
        logger.info(f"\nScripts {script_type} trouvés ({len(script_list)}):")
        for i, script_path in enumerate(script_list, 1):
            relative_path = os.path.relpath(script_path, str(project_path))
            logger.info(f"{i}. {relative_path}")
        
        response = input(f"\nVoulez-vous migrer ces scripts {script_type} vers automation/scripts/{script_type}/ ? [Y/n]: ").strip().lower()
        
        if response in ('', 'y', 'yes', 'oui'):
            target_dir = automation_path / script_type
            for script_path in script_list:
                script_name = os.path.basename(script_path)
                target_path = target_dir / script_name
                
                # Vérifier si le script existe déjà dans la destination
                if target_path.exists():
                    response = input(f"Le script {script_name} existe déjà à la destination. Écraser ? [y/N]: ").strip().lower()
                    if response not in ('y', 'yes', 'oui'):
                        logger.info(f"Migration ignorée pour: {script_name}")
                        continue
                
                # Copier ou déplacer ?
                action = input(f"Voulez-vous copier ou déplacer {script_name} ? [C(opier)/d(éplacer)]: ").strip().lower()
                
                if action.startswith('d'):
                    logger.info(f"Déplacement de {script_path} vers {target_path}")
                    shutil.move(script_path, target_path)
                else:
                    logger.info(f"Copie de {script_path} vers {target_path}")
                    shutil.copy2(script_path, target_path)
        else:
            logger.info(f"Migration des scripts {script_type} ignorée.")

def main():
    """
    Fonction principale du script.
    """
    # Déterminer le chemin du projet (dossier courant par défaut)
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1]).resolve()
    else:
        project_path = Path.cwd().resolve()
    
    logger.info(f"Mise à jour de la structure d'automatisation pour le projet: {project_path}")
    
    # Vérifier si le dossier est bien un projet littéraire
    if not (project_path / "index.md").exists():
        response = input("Le fichier index.md n'a pas été trouvé. Est-ce bien un projet littéraire ? [y/N]: ").strip().lower()
        if response not in ('y', 'yes', 'oui'):
            logger.error("Opération annulée: le dossier ne semble pas être un projet littéraire.")
            return
    
    # Trouver les scripts existants
    existing_scripts = find_existing_scripts(project_path)
    
    # Créer la nouvelle structure
    create_directory_structure(project_path, AUTOMATION_STRUCTURE)
    
    # Proposer la migration des scripts existants
    propose_script_migration(project_path, existing_scripts)
    
    # Créer des fichiers README dans les dossiers principaux
    readme_content = {
        'automation': "# Dossier d'automatisation\n\nCe dossier contient les scripts et outils pour automatiser les tâches de gestion du projet littéraire.",
        'review': "# Système de révision\n\nCe dossier organise le workflow de révision collaborative, y compris les intégrations avec Claude."
    }
    
    for folder, content in readme_content.items():
        readme_path = project_path / folder / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    logger.info("\nMise à jour de la structure d'automatisation terminée avec succès!")
    logger.info(f"Un journal des opérations a été enregistré dans: {project_path}/automation_setup.log")
    logger.info("\nProchaines étapes recommandées:")
    logger.info("1. Vérifier le contenu du dossier 'automation/'")
    logger.info("2. Ajuster les configurations dans 'automation/config/'")
    logger.info("3. Ajouter/adapter les scripts dans 'automation/scripts/'")
    logger.info("4. Configurer le système de révision dans le dossier 'review/'")

if __name__ == "__main__":
    main()
