#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de structure du projet d'édition littéraire.

Ce script analyse la structure du projet pour vérifier sa conformité avec 
les standards définis dans le guide complet. Il ne modifie aucun fichier 
directement mais génère des rapports et des tâches TODO pour les problèmes 
nécessitant une intervention manuelle.

Utilisation:
    python verify-structure-script.py [options]

Options:
    --project-dir PATH    Chemin vers le répertoire du projet (défaut: répertoire courant)
    --mode MODE           Mode de fonctionnement: 'analyze', 'report' ou 'fix' (défaut: analyze)
    --verbose             Affiche des informations détaillées pendant l'exécution
    --output FILE         Chemin vers le fichier de sortie pour le rapport (défaut: structure-report.md)
"""

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

# Structure attendue du projet basée sur le guide complet
EXPECTED_STRUCTURE = {
    'index.md': {'type': 'file', 'required': True},
    'README.md': {'type': 'file', 'required': True},
    'chapitres': {'type': 'dir', 'required': True},
    'structure': {
        'type': 'dir', 
        'required': True,
        'children': {
            'plan-general.md': {'type': 'file', 'required': True},
            'arcs-narratifs.md': {'type': 'file', 'required': False},
            'chronologie.md': {'type': 'file', 'required': False},
            'personnages.md': {'type': 'file', 'required': True},
            'univers.md': {'type': 'file', 'required': True}
        }
    },
    'personnages': {
        'type': 'dir', 
        'required': True,
        'children': {
            'index.md': {'type': 'file', 'required': True},
            'entites': {'type': 'dir', 'required': False},
            'manifestations': {'type': 'dir', 'required': False},
            'mortels': {'type': 'dir', 'required': False},
            'secondaires': {'type': 'dir', 'required': False}
        }
    },
    'lieux': {
        'type': 'dir', 
        'required': False,
        'children': {
            'reels': {'type': 'dir', 'required': False},
            'fictifs': {'type': 'dir', 'required': False}
        }
    },
    'concepts': {'type': 'dir', 'required': False},
    'references': {
        'type': 'dir', 
        'required': True,
        'children': {
            'index.md': {'type': 'file', 'required': True}
        }
    },
    'styles': {
        'type': 'dir', 
        'required': False,
        'children': {
            'index.md': {'type': 'file', 'required': False},
            'registres': {'type': 'dir', 'required': False}
        }
    },
    'ressources': {'type': 'dir', 'required': True},
    'claude-sessions': {'type': 'dir', 'required': True},
    'templates': {'type': 'dir', 'required': True},
    'export': {'type': 'dir', 'required': True},
    'automation': {
        'type': 'dir', 
        'required': True,
        'children': {
            'scripts': {
                'type': 'dir',
                'required': True,
                'children': {
                    'python': {'type': 'dir', 'required': True},
                    'bash': {'type': 'dir', 'required': False},
                    'js': {'type': 'dir', 'required': False}
                }
            },
            'config': {'type': 'dir', 'required': True},
            'templates': {'type': 'dir', 'required': True},
            'hooks': {'type': 'dir', 'required': False},
            'docs': {'type': 'dir', 'required': True}
        }
    },
    'review': {
        'type': 'dir', 
        'required': True,
        'children': {
            'pending': {'type': 'dir', 'required': True},
            'in_progress': {'type': 'dir', 'required': True},
            'completed': {'type': 'dir', 'required': True},
            'claude_suggestions': {'type': 'dir', 'required': True},
            'templates': {'type': 'dir', 'required': False}
        }
    },
    'media': {'type': 'dir', 'required': True}
}

# Templates attendus
EXPECTED_TEMPLATES = {
    'personnage-avance.md': {'required': True},
    'chapitre.md': {'required': True},
    'scene.md': {'required': False},
    'reference.md': {'required': True},
    'todo.md': {'required': True},
    'gantt.md': {'required': False},
    'intervenant.md': {'required': True}
}

# Règles pour les frontmatter YAML par type de document
FRONTMATTER_RULES = {
    'personnages/.*': {
        'required_fields': ['nom', 'tags'],
        'recommended_fields': ['citation', 'expertise'],
        'valid_tags': ['personnage', 'entite', 'mortel', 'manifestation', 'secondaire']
    },
    'review/.*todo.*\.md': {
        'required_fields': ['id', 'titre', 'statut', 'priorite', 'date_creation'],
        'recommended_fields': ['date_debut', 'date_fin', 'tags'],
        'valid_tags': ['tâche']
    }
}

def validate_structure(project_path, expected_structure, path="", issues=None):
    """
    Valide récursivement la structure du projet selon la définition attendue.
    
    Args:
        project_path (Path): Chemin de base du projet
        expected_structure (dict): Structure attendue pour ce niveau
        path (str): Chemin relatif actuel (pour le logging)
        issues (list): Liste pour accumuler les problèmes détectés
        
    Returns:
        list: Liste des problèmes détectés
    """
    if issues is None:
        issues = []
    
    for name, details in expected_structure.items():
        current_path = os.path.join(path, name)
        full_path = project_path / current_path
        
        # Vérifier l'existence de l'élément
        if not full_path.exists():
            if details.get('required', False):
                issues.append({
                    'level': 'error',
                    'type': 'missing_required',
                    'path': current_path,
                    'message': f"Élément requis manquant: {current_path}"
                })
            else:
                issues.append({
                    'level': 'warning',
                    'type': 'missing_optional',
                    'path': current_path,
                    'message': f"Élément recommandé manquant: {current_path}"
                })
            continue
        
        # Vérifier le type (fichier/dossier)
        expected_type = details['type']
        is_dir = full_path.is_dir()
        actual_type = 'dir' if is_dir else 'file'
        
        if expected_type != actual_type:
            issues.append({
                'level': 'error',
                'type': 'type_mismatch',
                'path': current_path,
                'message': f"Type incorrect pour {current_path}: attendu {expected_type}, trouvé {actual_type}"
            })
            continue
        
        # Si c'est un dossier avec une structure interne définie, vérifier récursivement
        if is_dir and 'children' in details:
            validate_structure(project_path, details['children'], current_path, issues)
    
    return issues

def validate_template_existence(project_path, issues=None):
    """
    Vérifie l'existence des templates requis.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste pour accumuler les problèmes détectés
        
    Returns:
        list: Liste des problèmes détectés
    """
    if issues is None:
        issues = []
    
    templates_dir = project_path / 'templates'
    if not templates_dir.exists() or not templates_dir.is_dir():
        issues.append({
            'level': 'error',
            'type': 'missing_templates_dir',
            'path': 'templates',
            'message': "Le dossier templates est manquant"
        })
        return issues
    
    for template_name, details in EXPECTED_TEMPLATES.items():
        template_path = templates_dir / template_name
        if not template_path.exists():
            level = 'error' if details.get('required', False) else 'warning'
            issues.append({
                'level': level,
                'type': 'missing_template',
                'path': f"templates/{template_name}",
                'message': f"Template {template_name} manquant"
            })
    
    return issues

def validate_frontmatter(project_path, issues=None):
    """
    Vérifie les frontmatter YAML des fichiers markdown selon les règles définies.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste pour accumuler les problèmes détectés
        
    Returns:
        list: Liste des problèmes détectés
    """
    if issues is None:
        issues = []
    
    # Parcourir tous les fichiers markdown du projet
    for md_file in project_path.glob('**/*.md'):
        # Ignorer les fichiers dans .git, export, etc.
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        # Vérifier si ce fichier correspond à une règle de frontmatter
        matching_rules = []
        for pattern, rules in FRONTMATTER_RULES.items():
            if re.match(pattern, str_path):
                matching_rules.append(rules)
        
        if not matching_rules:
            continue  # Aucune règle spécifique pour ce fichier
        
        # Extraire le frontmatter
        try:
            frontmatter, _ = extract_frontmatter(md_file)
            
            if frontmatter is None:
                issues.append({
                    'level': 'warning',
                    'type': 'missing_frontmatter',
                    'path': str_path,
                    'message': f"Frontmatter YAML manquant dans {str_path}"
                })
                continue
            
            # Vérifier les champs requis et recommandés selon les règles
            for rules in matching_rules:
                for field in rules.get('required_fields', []):
                    if field not in frontmatter:
                        issues.append({
                            'level': 'error',
                            'type': 'missing_required_field',
                            'path': str_path,
                            'message': f"Champ requis manquant dans {str_path}: {field}"
                        })
                
                for field in rules.get('recommended_fields', []):
                    if field not in frontmatter:
                        issues.append({
                            'level': 'warning',
                            'type': 'missing_recommended_field',
                            'path': str_path,
                            'message': f"Champ recommandé manquant dans {str_path}: {field}"
                        })
                
                # Vérifier les tags si définis
                if 'tags' in frontmatter and 'valid_tags' in rules:
                    tags = frontmatter['tags']
                    if isinstance(tags, str):
                        # Certains fichiers pourraient avoir les tags comme une chaîne
                        tags = [tag.strip() for tag in tags.split(',')]
                    
                    valid_tags = rules['valid_tags']
                    if not any(tag in valid_tags for tag in tags):
                        issues.append({
                            'level': 'warning',
                            'type': 'invalid_tags',
                            'path': str_path,
                            'message': f"Aucun tag valide trouvé dans {str_path}. Tags attendus: {', '.join(valid_tags)}"
                        })
        
        except Exception as e:
            issues.append({
                'level': 'error',
                'type': 'frontmatter_parsing_error',
                'path': str_path,
                'message': f"Erreur lors de l'analyse du frontmatter dans {str_path}: {str(e)}"
            })
    
    return issues

def extract_frontmatter(file_path):
    """
    Extrait le frontmatter YAML d'un fichier markdown.
    
    Args:
        file_path (Path): Chemin du fichier
        
    Returns:
        tuple: (frontmatter_dict, content_str) ou (None, content_str) si pas de frontmatter
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Rechercher le frontmatter délimité par ---
    frontmatter_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not frontmatter_match:
        return None, content
    
    frontmatter_str = frontmatter_match.group(1)
    remaining_content = content[frontmatter_match.end():]
    
    try:
        frontmatter_dict = yaml.safe_load(frontmatter_str)
        return frontmatter_dict, remaining_content
    except yaml.YAMLError:
        # En cas d'erreur de parsing, retourner l'erreur
        raise ValueError(f"YAML invalide dans le frontmatter: {frontmatter_str}")

def check_broken_links(project_path, issues=None):
    """
    Vérifie les liens internes cassés dans les fichiers markdown.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste pour accumuler les problèmes détectés
        
    Returns:
        list: Liste des problèmes détectés
    """
    if issues is None:
        issues = []
    
    # Collecter tous les fichiers markdown existants
    existing_files = set()
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        existing_files.add(str(relative_path))
        # Ajouter aussi sans extension .md
        existing_files.add(str(relative_path)[:-3])
    
    # Vérifier les liens dans chaque fichier
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Rechercher les liens wiki [[lien]]
        wiki_links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
        
        # Rechercher les liens markdown [texte](lien)
        md_links = re.findall(r'\[.*?\]\((.*?)\)', content)
        
        # Vérifier tous les liens
        all_links = wiki_links + md_links
        for link in all_links:
            # Ignorer les liens externes et les ancres
            if link.startswith(('http://', 'https://', '#')):
                continue
            
            # Normaliser le lien
            link = link.split('#')[0]  # Enlever les ancres
            
            # Si le lien est relatif au dossier courant du fichier
            if not link.startswith('/'):
                current_dir = os.path.dirname(str_path)
                link = os.path.normpath(os.path.join(current_dir, link))
            else:
                # Enlever le / initial pour les chemins absolus dans le projet
                link = link.lstrip('/')
            
            # Vérifier si le fichier cible existe
            if link and link not in existing_files and link + '.md' not in existing_files:
                issues.append({
                    'level': 'warning',
                    'type': 'broken_link',
                    'path': str_path,
                    'message': f"Lien cassé dans {str_path}: '{link}'"
                })
    
    return issues

def create_manual_review_task(project_path, file_path, issues_detected):
    """
    Crée une tâche de révision manuelle pour un fichier problématique.
    
    Args:
        project_path (Path): Chemin de base du projet
        file_path (str): Chemin relatif du fichier problématique
        issues_detected (list): Liste des problèmes détectés pour ce fichier
        
    Returns:
        str: Chemin du fichier de tâche créé
    """
    # Générer un ID unique pour la tâche
    task_id = f"TODO-{datetime.now().strftime('%Y%m%d%H%M')}-{os.path.basename(file_path).split('.')[0][:4].upper()}"
    
    # Définir le chemin de sortie
    output_dir = project_path / "review" / "claude_suggestions"
    os.makedirs(output_dir, exist_ok=True)
    
    output_filename = f"{task_id}-structure-revision.md"
    output_path = output_dir / output_filename
    
    # Formatter les problèmes détectés pour le contenu de la tâche
    issues_content = ""
    for i, issue in enumerate(issues_detected, 1):
        issues_content += f"{i}. **{issue['type'].replace('_', ' ').title()}** ({issue.get('details', '')}):\n"
        issues_content += f"   {issue['message']}\n\n"
    
    # Créer le contenu de la tâche selon le template standard
    content = f"""---
id: {task_id}
titre: Révision manuelle requise pour {os.path.basename(file_path)}
statut: À faire
priorite: 2
date_creation: {datetime.now().strftime('%Y-%m-%d')}
date_debut: {datetime.now().strftime('%Y-%m-%d')}
date_fin: {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}
tags: tâche, révision-structure
---

# Révision manuelle requise pour {os.path.basename(file_path)} [{task_id}]

**Statut**: À faire
**Priorité**: 2/5
**Période**: {datetime.now().strftime('%Y-%m-%d')} → {(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')}

## Description

Le fichier `{file_path}` présente des problèmes de structure qui nécessitent une révision manuelle. Une modification automatique pourrait corrompre le contenu.

## Problèmes détectés

{issues_content}

## Actions recommandées

- [ ] Ouvrir le fichier dans un éditeur de texte
- [ ] Corriger les problèmes structurels identifiés
- [ ] Vérifier que le contenu reste cohérent et valide
- [ ] Exécuter le script de vérification en mode analyse uniquement pour confirmer les corrections

## Intervenants assignés

- [[]] <!-- Ajouter manuellement les intervenants appropriés -->

## Ressources nécessaires

- Format standard attendu pour ce type de fichier
- Documentation de référence sur la structure du projet

## Notes

**IMPORTANT** : Ne pas utiliser d'outils automatisés pour modifier ce fichier avant d'avoir résolu les problèmes structurels.
"""
    
    # Écrire le fichier de tâche
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Tâche de révision manuelle créée: {output_path}")
    return str(output_path)

def group_issues_by_file(issues):
    """
    Groupe les problèmes par fichier.
    
    Args:
        issues (list): Liste des problèmes détectés
        
    Returns:
        dict: Dictionnaire des problèmes groupés par fichier
    """
    grouped = {}
    for issue in issues:
        path = issue['path']
        if path not in grouped:
            grouped[path] = []
        grouped[path].append(issue)
    
    return grouped

def create_markdown_report(project_path, issues, output_file="structure-report.md"):
    """
    Crée un rapport au format Markdown des problèmes de structure détectés.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        output_file (str): Nom du fichier de sortie
        
    Returns:
        str: Chemin du fichier de rapport créé
    """
    # Compter les problèmes par niveau
    error_count = sum(1 for issue in issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in issues if issue['level'] == 'warning')
    
    # Créer le contenu du rapport
    report_content = f"""# Rapport de vérification de structure

Projet: {project_path}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé

- **Erreurs**: {error_count}
- **Avertissements**: {warning_count}
- **Total**: {len(issues)}

## Problèmes détectés

"""
    
    # Regrouper les problèmes par type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue['type']
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)
    
    # Ajouter les problèmes au rapport, regroupés par type
    for issue_type, type_issues in sorted(issues_by_type.items()):
        report_content += f"### {issue_type.replace('_', ' ').title()} ({len(type_issues)})\n\n"
        
        for issue in sorted(type_issues, key=lambda x: x['path']):
            level_icon = "🔴" if issue['level'] == 'error' else "🟠"
            report_content += f"- {level_icon} **{issue['path']}**: {issue['message']}\n"
        
        report_content += "\n"
    
    # Ajouter la section des tâches générées
    report_content += """
## Tâches de révision manuelle

Les fichiers suivants nécessitent une révision manuelle et des tâches ont été créées dans le dossier `review/claude_suggestions/` :

"""
    
    # Grouper les problèmes par fichier pour déterminer lesquels nécessitent une révision manuelle
    grouped_issues = group_issues_by_file(issues)
    files_needing_manual_review = []
    
    for file_path, file_issues in grouped_issues.items():
        # Critères pour déterminer si une révision manuelle est nécessaire
        has_errors = any(issue['level'] == 'error' for issue in file_issues)
        has_frontmatter_issues = any('frontmatter' in issue['type'] for issue in file_issues)
        
        if has_errors and has_frontmatter_issues:
            files_needing_manual_review.append((file_path, file_issues))
    
    if files_needing_manual_review:
        for file_path, _ in files_needing_manual_review:
            report_content += f"- `{file_path}`\n"
    else:
        report_content += "Aucun fichier ne nécessite de révision manuelle immédiate.\n"
    
    # Ajouter les recommandations
    report_content += """
## Recommandations

1. Corriger d'abord les erreurs critiques liées à la structure de base du projet
2. Résoudre ensuite les problèmes de frontmatter dans les fichiers spécifiques
3. Vérifier et corriger les liens internes cassés
4. Exécuter à nouveau ce script pour confirmer que tous les problèmes ont été résolus

"""
    
    # Écrire le rapport dans un fichier
    output_path = project_path / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Rapport de structure créé: {output_path}")
    return str(output_path)

def fix_missing_dirs(project_path, issues):
    """
    Crée les répertoires manquants identifiés dans les problèmes.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        
    Returns:
        int: Nombre de répertoires créés
    """
    dirs_created = 0
    for issue in issues:
        if issue['level'] == 'error' and issue['type'] == 'missing_required' and '.md' not in issue['path']:
            try:
                # C'est un répertoire manquant
                dir_path = project_path / issue['path']
                if not dir_path.exists():
                    os.makedirs(dir_path, exist_ok=True)
                    logger.info(f"Répertoire créé: {dir_path}")
                    dirs_created += 1
            except Exception as e:
                logger.error(f"Erreur lors de la création du répertoire {issue['path']}: {e}")
    
    return dirs_created

def copy_missing_templates(project_path, issues):
    """
    Copie les templates manquants à partir des templates standard.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        
    Returns:
        int: Nombre de templates copiés
    """
    templates_copied = 0
    templates_dir = project_path / 'templates'
    
    # S'assurer que le répertoire templates existe
    if not templates_dir.exists():
        os.makedirs(templates_dir, exist_ok=True)
    
    # Dictionnaire des templates standard et leurs sources
    standard_templates = {
        'todo.md': {
            'source': project_path / 'automation' / 'scripts' / 'python' / 'script-init-todo.py',
            'extraction_func': lambda content: re.search(r'TEMPLATE_TODO\s*=\s*"""(.*?)"""', content, re.DOTALL).group(1)
        },
        'intervenant.md': {
            'source': project_path / 'automation' / 'scripts' / 'python' / 'script-init-todo.py',
            'extraction_func': lambda content: re.search(r'TEMPLATE_INTERVENANT\s*=\s*"""(.*?)"""', content, re.DOTALL).group(1)
        },
        'personnage-avance.md': {
            'source': project_path / 'review' / 'claude_suggestions' / '2025-03-20-template-personnage-avance (1).md',
            'extraction_func': lambda content: content
        }
    }
    
    for issue in issues:
        if issue['type'] == 'missing_template':
            template_name = os.path.basename(issue['path'])
            
            if template_name in standard_templates:
                source_info = standard_templates[template_name]
                source_path = source_info['source']
                
                if source_path.exists():
                    try:
                        with open(source_path, 'r', encoding='utf-8') as f:
                            source_content = f.read()
                        
                        # Extraire le contenu du template selon la fonction d'extraction
                        template_content = source_info['extraction_func'](source_content)
                        
                        # Écrire le template
                        target_path = templates_dir / template_name
                        with open(target_path, 'w', encoding='utf-8') as f:
                            f.write(template_content)
                        
                        logger.info(f"Template créé: {target_path}")
                        templates_copied += 1
                    except Exception as e:
                        logger.error(f"Erreur lors de la création du template {template_name}: {e}")
    
    return templates_copied

def create_missing_index_files(project_path, issues):
    """
    Crée les fichiers index.md manquants dans les répertoires où ils sont requis.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        
    Returns:
        int: Nombre de fichiers index créés
    """
    index_files_created = 0
    
    # Modèles pour différents types d'index files
    index_templates = {
        'index.md': """# Projet d'édition littéraire

## Métadonnées
- Titre: [Titre du projet]
- Auteur: [Nom de l'auteur]
- Date de création: {date}
- Statut: #en-cours

## Structure
- [Plan général](structure/plan-general.md)
- [Personnages](structure/personnages.md)
- [Univers](structure/univers.md)

## Chapitres
<!-- Les liens vers les chapitres seront ajoutés ici -->

## Notes
<!-- Notes générales sur le projet -->
""",
        'personnages/index.md': """# Index des personnages

Ce document répertorie tous les personnages du projet et leurs relations.

## Personnages principaux
<!-- Liens vers les personnages principaux -->

## Personnages secondaires
<!-- Liens vers les personnages secondaires -->

## Relations clés
<!-- Description des relations importantes entre personnages -->
""",
        'references/index.md': """# Index des références

Ce document organise toutes les références externes utilisées dans le projet.

## Navigation par type
<!-- Liens vers les différents types de références -->

## Navigation par thème
<!-- Liens vers les références organisées par thème -->

## Tags fréquemment utilisés
<!-- Liste des tags couramment utilisés -->
"""
    }
    
    for issue in issues:
        if issue['level'] == 'error' and issue['type'] == 'missing_required' and issue['path'].endswith('index.md'):
            try:
                # C'est un fichier index manquant
                file_path = project_path / issue['path']
                
                # S'assurer que le répertoire parent existe
                os.makedirs(file_path.parent, exist_ok=True)
                
                # Déterminer quel template utiliser
                template_key = issue['path']
                if template_key not in index_templates:
                    template_key = 'index.md'  # Template par défaut
                
                # Créer le contenu avec la date actuelle
                content = index_templates[template_key].format(date=datetime.now().strftime('%Y-%m-%d'))
                
                # Écrire le fichier
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Fichier index créé: {file_path}")
                index_files_created += 1
            except Exception as e:
                logger.error(f"Erreur lors de la création du fichier index {issue['path']}: {e}")
    
    return index_files_created

def fix_broken_links(project_path, issues, interactive=True):
    """
    Corrige les liens cassés simples (renommages, changements de casse, etc.)
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        interactive (bool): Demander confirmation pour chaque fichier modifié
        
    Returns:
        int: Nombre de liens corrigés
    """
    links_fixed = 0
    
    # Collecter tous les fichiers markdown existants pour rechercher les correspondances
    existing_files = {}
    for md_file in project_path.glob('**/*.md'):
        if any(part.startswith('.') for part in md_file.parts) or 'export' in md_file.parts:
            continue
        
        relative_path = md_file.relative_to(project_path)
        str_path = str(relative_path)
        
        # Ajouter le chemin complet
        existing_files[str_path.lower()] = str_path
        # Ajouter aussi sans extension .md
        existing_files[str_path[:-3].lower()] = str_path[:-3]
    
    # Filtrer les problèmes de liens cassés
    broken_link_issues = [issue for issue in issues if issue['type'] == 'broken_link']
    
    if not broken_link_issues:
        return 0
    
    # Traiter chaque fichier contenant des liens cassés
    processed_files = set()
    for issue in broken_link_issues:
        file_path = project_path / issue['path']
        
        if str(file_path) in processed_files:
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Trouver tous les liens wiki et markdown
            wiki_links = re.findall(r'\[\[(.*?)(?:\|.*?)?\]\]', content)
            md_links = re.findall(r'\[.*?\]\((.*?)\)', content)
            
            # Créer une copie du contenu pour les modifications
            new_content = content
            
            # Corriger les liens cassés
            fixed_in_this_file = 0
            links_to_fix = []
            
            for link_pattern in (wiki_links + md_links):
                # Ignorer les liens externes et les ancres
                if link_pattern.startswith(('http://', 'https://', '#')):
                    continue
                
                # Normaliser le lien pour la recherche
                normalized_link = link_pattern.split('#')[0].lower()  # Enlever les ancres et mettre en minuscules
                
                # Si le lien normalisé existe dans notre dictionnaire de fichiers existants
                if normalized_link in existing_files and existing_files[normalized_link] != link_pattern:
                    correct_link = existing_files[normalized_link]
                    links_to_fix.append((link_pattern, correct_link))
            
            # Demander confirmation si interactive
            if interactive and links_to_fix:
                print(f"\nFichier: {file_path}")
                print("Liens à corriger:")
                for i, (old, new) in enumerate(links_to_fix, 1):
                    print(f"{i}. '{old}' -> '{new}'")
                
                confirm = input("Corriger ces liens? [Y/n/s(elect)]: ").strip().lower()
                
                if confirm == 's' or confirm == 'select':
                    # Mode sélection: demander pour chaque lien
                    selected_links = []
                    for i, (old, new) in enumerate(links_to_fix, 1):
                        link_confirm = input(f"  Corriger '{old}' -> '{new}'? [Y/n]: ").strip().lower()
                        if not link_confirm or link_confirm in ('y', 'yes', 'oui'):
                            selected_links.append((old, new))
                    
                    links_to_fix = selected_links
                elif confirm and confirm not in ('y', 'yes', 'oui'):
                    # Si la réponse n'est pas vide et n'est pas oui, passer ce fichier
                    logger.info(f"Liens non corrigés dans {file_path}")
                    continue
            
            # Appliquer les corrections
            for old_link, new_link in links_to_fix:
                # Remplacer dans les liens wiki
                wiki_pattern = f'\\[\\[{re.escape(old_link)}(?:\\|.*?)?\\]\\]'
                wiki_replacement = lambda m: m.group(0).replace(old_link, new_link)
                new_content = re.sub(wiki_pattern, wiki_replacement, new_content)
                
                # Remplacer dans les liens markdown
                md_pattern = f'\\[.*?\\]\\({re.escape(old_link)}\\)'
                md_replacement = lambda m: m.group(0).replace(old_link, new_link)
                new_content = re.sub(md_pattern, md_replacement, new_content)
                
                fixed_in_this_file += 1
            
            # Sauvegarder les modifications si des liens ont été corrigés
            if fixed_in_this_file > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Corrigé {fixed_in_this_file} liens dans {file_path}")
                links_fixed += fixed_in_this_file
            
            processed_files.add(str(file_path))
        except Exception as e:
            logger.error(f"Erreur lors de la correction des liens dans {file_path}: {e}")
    
    return links_fixed

def main():
    """
    Fonction principale du script.
    """
    parser = argparse.ArgumentParser(description="Vérifie la structure du projet d'édition littéraire.")
    parser.add_argument("--project-dir", default=".", help="Chemin vers le répertoire du projet")
    parser.add_argument("--mode", choices=["analyze", "report", "fix"], default="analyze", 
                       help="Mode de fonctionnement: 'analyze' (vérification simple), 'report' (génère des tâches) ou 'fix' (corrige automatiquement les problèmes simples)")
    parser.add_argument("--verbose", action="store_true", help="Affiche des informations détaillées")
    parser.add_argument("--output", default="structure-report.md", help="Chemin vers le fichier de sortie pour le rapport")
    
    args = parser.parse_args()
    
    # Configurer le niveau de log
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Convertir le chemin du projet en Path
    project_path = Path(args.project_dir).resolve()
    logger.info(f"Vérification de la structure du projet: {project_path}")
    
    # Vérifier que le chemin existe et contient un projet
    if not project_path.exists() or not project_path.is_dir():
        logger.error(f"Le répertoire spécifié n'existe pas: {project_path}")
        return 1
    
    # Vérifier qu'il s'agit bien d'un projet littéraire
    if not (project_path / "index.md").exists() and not (project_path / "README.md").exists():
        logger.warning(f"Ce dossier ne semble pas être un projet littéraire (index.md ou README.md manquants): {project_path}")
        if not args.yes:
            confirm = input("Continuer quand même? [y/N]: ").strip().lower()
            if confirm not in ('y', 'yes', 'oui'):
                logger.info("Opération annulée.")
                return 0
        else:
            logger.info("Continuation forcée (mode automatique).")
    
    # Collecter tous les problèmes
    all_issues = []
    
    # 1. Valider la structure des dossiers et fichiers
    logger.info("Vérification de la structure de base...")
    structure_issues = validate_structure(project_path, EXPECTED_STRUCTURE)
    all_issues.extend(structure_issues)
    
    # 2. Vérifier les templates
    logger.info("Vérification des templates...")
    template_issues = validate_template_existence(project_path)
    all_issues.extend(template_issues)
    
    # 3. Vérifier les frontmatters
    logger.info("Vérification des frontmatter YAML...")
    frontmatter_issues = validate_frontmatter(project_path)
    all_issues.extend(frontmatter_issues)
    
    # 4. Vérifier les liens internes
    logger.info("Vérification des liens internes...")
    link_issues = check_broken_links(project_path)
    all_issues.extend(link_issues)
    
    # Afficher un résumé des problèmes
    error_count = sum(1 for issue in all_issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in all_issues if issue['level'] == 'warning')
    
    logger.info(f"Vérification terminée. Trouvé {error_count} erreurs et {warning_count} avertissements.")
    
    # Mode de correction automatique des problèmes simples
    if args.mode == "fix":
        logger.info("Mode de correction automatique activé. Correction des problèmes simples...")
        
        # Demander confirmation avant de procéder aux modifications
        if not args.yes:
            print("\nLes modifications suivantes seront effectuées:")
            print(f"- Création de répertoires manquants ({sum(1 for i in all_issues if i['type'] == 'missing_required' and '.md' not in i['path'])})")
            print(f"- Création de templates manquants ({sum(1 for i in all_issues if i['type'] == 'missing_template')})")
            print(f"- Création de fichiers index.md manquants ({sum(1 for i in all_issues if i['type'] == 'missing_required' and i['path'].endswith('index.md'))})")
            print(f"- Correction de liens cassés ({sum(1 for i in all_issues if i['type'] == 'broken_link')})")
            
            confirm = input("\nVoulez-vous procéder à ces corrections? [Y/n]: ").strip().lower()
            if confirm and confirm not in ('y', 'yes', 'oui'):
                logger.info("Opération de correction annulée par l'utilisateur.")
                
                # Créer quand même le rapport pour référence
                report_path = create_markdown_report(project_path, all_issues, args.output)
                logger.info(f"Rapport détaillé créé sans corrections: {report_path}")
                
                return 0
        
        # 1. Corriger les répertoires manquants
        dirs_created = fix_missing_dirs(project_path, all_issues)
        logger.info(f"{dirs_created} répertoires manquants créés.")
        
        # 2. Corriger les templates manquants
        templates_copied = copy_missing_templates(project_path, all_issues)
        logger.info(f"{templates_copied} templates manquants copiés.")
        
        # 3. Créer les fichiers index.md manquants
        index_files_created = create_missing_index_files(project_path, all_issues)
        logger.info(f"{index_files_created} fichiers index.md créés.")
        
        # 4. Corriger les liens cassés simples
        links_fixed = fix_broken_links(project_path, all_issues, not args.yes)
        logger.info(f"{links_fixed} liens cassés corrigés.")
        
        # Refaire une vérification pour voir les problèmes restants
        logger.info("Nouvelle vérification après corrections...")
        
        new_issues = []
        new_issues.extend(validate_structure(project_path, EXPECTED_STRUCTURE))
        new_issues.extend(validate_template_existence(project_path))
        new_issues.extend(validate_frontmatter(project_path))
        new_issues.extend(check_broken_links(project_path))
        
        new_error_count = sum(1 for issue in new_issues if issue['level'] == 'error')
        new_warning_count = sum(1 for issue in new_issues if issue['level'] == 'warning')
        
        logger.info(f"Après corrections: {new_error_count} erreurs et {new_warning_count} avertissements restants.")
        
        # Mettre à jour la liste des problèmes pour le rapport
        all_issues = new_issues
    
    # Créer le rapport Markdown
    report_path = create_markdown_report(project_path, all_issues, args.output)
    logger.info(f"Rapport détaillé créé: {report_path}")
    
    # En mode rapport, créer des tâches uniquement pour les problèmes complexes
    if args.mode == "report" or (args.mode == "fix" and len(all_issues) > 0):
        logger.info("Création des tâches de révision manuelle pour les problèmes complexes...")
        
        # Grouper les problèmes par fichier
        grouped_issues = group_issues_by_file(all_issues)
        tasks_created = 0
        
        for file_path, file_issues in grouped_issues.items():
            # Critères pour déterminer si une révision manuelle est VRAIMENT nécessaire
            # (problèmes complexes uniquement, non résolus automatiquement)
            has_errors = any(issue['level'] == 'error' for issue in file_issues)
            has_frontmatter_issues = any('frontmatter' in issue['type'] for issue in file_issues)
            has_parsing_errors = any('parsing_error' in issue['type'] for issue in file_issues)
            
            # Ne créer une tâche que si le fichier a des problèmes complexes
            if (has_errors and (has_frontmatter_issues or has_parsing_errors)):
                try:
                    task_path = create_manual_review_task(project_path, file_path, file_issues)
                    tasks_created += 1
                    logger.info(f"Tâche créée pour {file_path}: {task_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la tâche pour {file_path}: {e}")
        
        logger.info(f"{tasks_created} tâches de révision manuelle créées.")
    
    # Retourner 1 s'il y a des erreurs, 0 sinon
    return 1 if error_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())