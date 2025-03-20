#!/usr/bin/env python3
# verify_structure.py
"""
Script pour vérifier et mettre à jour la structure d'un projet littéraire.
Vérifie l'existence des répertoires et fichiers essentiels et propose des corrections.

Usage:
  python verify_structure.py                  # Vérifie le projet dans le dossier courant
  python verify_structure.py -p /chemin/projet # Vérifie un projet spécifique
  python verify_structure.py -d               # Mode dry-run (sans modifications)
  python verify_structure.py -n               # Mode non-interactif (sans confirmation)
"""

import os
import sys
import shutil
import filecmp
from pathlib import Path
import logging
import argparse
import time

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"structure_verification_{time.strftime('%Y%m%d-%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('verify_structure')

# Définition de la structure standard du projet
PROJECT_STRUCTURE = {
    'index.md': "# Projet Littéraire\n\n[Description du projet]",
    'import': {
        'README.md': "# Dossier d'import\n\nCe dossier est destiné à contenir les manuscrits originaux et documents externes à importer dans le projet.\n\n## Utilisation\n\n1. Placez vos documents originaux (manuscrits, notes, etc.) dans ce dossier\n2. Utilisez les scripts d'importation du dossier `automation/scripts/python/` pour les traiter\n3. Les documents traités seront convertis au format approprié et placés dans les dossiers correspondants"
    },
    'chapitres': {},
    'structure': {
        'plan-general.md': "# Plan Général\n\n[Ajouter le plan général ici]",
        'arcs-narratifs.md': "# Arcs Narratifs\n\n[Ajouter les arcs narratifs ici]",
        'chronologie.md': "# Chronologie\n\n[Ajouter la chronologie ici]",
        'personnages': {
            'index.md': "# Index des Personnages\n\n[Liste des personnages]",
            'entites': {},
            'manifestations': {},
            'mortels': {},
            'secondaires': {}
        }
    },
    'lieux': {
        'reels': {},
        'fictifs': {}
    },
    'concepts': {
        'temporalite.md': "# Temporalité\n\n[Concepts liés au temps]",
        'manifestations.md': "# Manifestations\n\n[Concept des manifestations]"
    },
    'ressources': {
        'brainstorming': {},
        'recherche': {},
        'medias': {
            'playlists': {},
            'moodboards': {}
        },
        'extraits': {},
        'auteurs': {}
    },
    'references': {
        'index.md': "# Index des Références\n\n[Liste des références]"
    },
    'styles': {
        'index.md': "# Styles Narratifs\n\n[Vue d'ensemble des styles]",
        'registres': {},
        'transitions.md': "# Transitions entre styles\n\n[Matrices de transition]",
        'verification.md': "# Vérification de style\n\n[Checklist de cohérence]"
    },
    'claude-sessions': {
        'index.md': "# Sessions Claude\n\n[Organisation des sessions]",
        'developpement': {},
        'personnages': {},
        'revision': {},
        'brainstorming': {}
    },
    'automation': {
        'scripts': {
            'python': {
                'README.md': "# Scripts Python\n\nCette section contient les scripts Python pour l'automatisation du projet littéraire."
            },
            'bash': {},
            'js': {}
        },
        'config': {},
        'hooks': {},
        'templates': {},
        'docs': {
            'README.md': "# Documentation des scripts\n\nCette section contient la documentation pour les scripts et workflows d'automatisation."
        }
    },
    'review': {
        'pending': {},
        'in_progress': {},
        'completed': {},
        'claude_suggestions': {},
        'templates': {}
    },
    'templates': {
        'personnage-avance.md': "# Template de Personnage Avancé\n\n[Contenu du template]",
        'chapitre.md': "# Template de Chapitre\n\n[Contenu du template]",
        'reference.md': "# Template de Référence\n\n[Contenu du template]",
        'intervenant.md': "# Template d'Intervenant\n\n[Contenu du template]",
        'todo.md': "# Template de Tâche\n\n[Contenu du template]",
        'gantt.md': "# Template de Diagramme Gantt\n\n[Contenu du template]"
    },
    'export': {
        'pdf': {},
        'epub': {},
        'html': {}
    }
}

def file_needs_update(src_content, dest_path):
    """
    Vérifie si un fichier doit être mis à jour.
    
    Args:
        src_content (str): Contenu source du fichier
        dest_path (Path): Chemin du fichier de destination
    
    Returns:
        bool: True si le fichier doit être mis à jour, False sinon
    """
    if not dest_path.exists():
        return True
    
    try:
        with open(dest_path, 'r', encoding='utf-8') as f:
            dest_content = f.read()
        
        # Si le contenu est identique, pas besoin de mise à jour
        return dest_content != src_content
    except Exception as e:
        logger.warning(f"Erreur lors de la lecture du fichier {dest_path}: {e}")
        return True

def check_structure(project_path, structure=None, path_prefix="", dry_run=False, interactive=True):
    """
    Vérifie récursivement la structure du projet et propose des corrections.
    
    Args:
        project_path (Path): Chemin racine du projet
        structure (dict): Structure à vérifier (partie de PROJECT_STRUCTURE)
        path_prefix (str): Préfixe du chemin pour l'affichage
        dry_run (bool): Si True, affiche les actions sans les exécuter
        interactive (bool): Si True, demande confirmation avant chaque action
    
    Returns:
        tuple: (nb_issues, nb_fixed) Nombre de problèmes détectés et corrigés
    """
    if structure is None:
        structure = PROJECT_STRUCTURE
    
    nb_issues = 0
    nb_fixed = 0
    
    for item_name, item_content in structure.items():
        item_path = project_path / item_name
        full_path = f"{path_prefix}/{item_name}" if path_prefix else item_name
        
        # Si c'est un fichier (contenu est une chaîne)
        if isinstance(item_content, str):
            if not item_path.exists():
                nb_issues += 1
                action = f"Créer le fichier manquant: {full_path}"
                logger.warning(f"Problème: Fichier manquant {full_path}")
                
                if not dry_run and (not interactive or prompt_user(action)):
                    logger.info(f"Action: {action}")
                    item_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(item_content)
                    nb_fixed += 1
            elif file_needs_update(item_content, item_path):
                # Le fichier existe mais a peut-être besoin d'être mis à jour
                nb_issues += 1
                action = f"Mettre à jour le fichier: {full_path}"
                logger.warning(f"Problème: Fichier différent du standard {full_path}")
                
                if not dry_run and (not interactive or prompt_user(action)):
                    # Créer une sauvegarde avant mise à jour
                    backup_path = item_path.with_suffix(item_path.suffix + '.bak')
                    shutil.copy2(item_path, backup_path)
                    logger.info(f"Sauvegarde créée: {backup_path}")
                    
                    # Mettre à jour le fichier
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(item_content)
                    logger.info(f"Action: {action}")
                    nb_fixed += 1
        
        # Si c'est un dossier (contenu est un dictionnaire)
        else:
            if not item_path.exists():
                nb_issues += 1
                action = f"Créer le dossier manquant: {full_path}"
                logger.warning(f"Problème: Dossier manquant {full_path}")
                
                if not dry_run and (not interactive or prompt_user(action)):
                    logger.info(f"Action: {action}")
                    item_path.mkdir(parents=True, exist_ok=True)
                    nb_fixed += 1
            
            # Récursion pour vérifier la structure interne
            sub_issues, sub_fixed = check_structure(
                item_path, item_content, full_path, dry_run, interactive
            )
            nb_issues += sub_issues
            nb_fixed += sub_fixed
    
    return nb_issues, nb_fixed

def prompt_user(action):
    """
    Demande confirmation à l'utilisateur avant d'effectuer une action.
    
    Args:
        action (str): Description de l'action à effectuer
    
    Returns:
        bool: True si l'utilisateur confirme, False sinon
    """
    response = input(f"{action} [Y/n]: ").strip().lower()
    return response in ('', 'y', 'yes', 'oui')

def main():
    parser = argparse.ArgumentParser(description="Vérifie et corrige la structure d'un projet littéraire.")
    parser.add_argument("--project-path", "-p", type=Path, default=Path.cwd(),
                        help="Chemin du projet (par défaut: répertoire courant)")
    parser.add_argument("--dry-run", "-d", action="store_true",
                        help="Affiche les actions sans les exécuter")
    parser.add_argument("--non-interactive", "-n", action="store_true",
                        help="N'attend pas la confirmation de l'utilisateur")
    
    args = parser.parse_args()
    
    project_path = args.project_path.resolve()
    logger.info(f"Vérification de la structure du projet dans: {project_path}")
    
    # Vérifier si le dossier est bien un projet littéraire
    if not any([(project_path / key).exists() for key in ['index.md', 'chapitres', 'structure']]):
        logger.warning(f"Attention: {project_path} ne semble pas être un projet littéraire.")
        if args.non_interactive or prompt_user("Continuer quand même?"):
            logger.info("Continuation de la vérification...")
        else:
            logger.info("Vérification annulée.")
            return 1
    
    # Lancer la vérification
    start_time = time.time()
    nb_issues, nb_fixed = check_structure(
        project_path, 
        dry_run=args.dry_run, 
        interactive=not args.non_interactive
    )
    end_time = time.time()
    
    # Afficher le résumé
    if nb_issues == 0:
        logger.info("Aucun problème de structure détecté. Le projet est conforme.")
    else:
        logger.info(f"Problèmes détectés: {nb_issues}")
        if args.dry_run:
            logger.info("Mode dry-run: aucune modification n'a été effectuée.")
        else:
            logger.info(f"Problèmes corrigés: {nb_fixed}")
            if nb_fixed < nb_issues:
                logger.warning(f"Problèmes restants: {nb_issues - nb_fixed}")
    
    logger.info(f"Vérification terminée en {end_time - start_time:.2f} secondes.")
    return 0 if nb_issues == 0 or nb_fixed == nb_issues else 1

if __name__ == "__main__":
    sys.exit(main())
