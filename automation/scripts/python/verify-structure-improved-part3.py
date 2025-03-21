    # Collecter tous les problèmes
    all_issues = []
    
    try:
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
    except Exception as e:
        logger.error(f"Erreur pendant la vérification: {e}")
        return 1
    
    # Afficher un résumé des problèmes
    error_count = sum(1 for issue in all_issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in all_issues if issue['level'] == 'warning')
    
    logger.info(f"Vérification terminée. Trouvé {error_count} erreurs et {warning_count} avertissements.")
    
    # Déterminer l'action selon le mode
    correction_results = {}
    
    if args.mode in ["fix", "interactive"]:
        logger.info(f"Mode {args.mode} activé. Préparation des corrections...")
        
        # Sauvegarde du projet avant modification (sauf en mode analyse)
        if not args.yes:
            backup_confirm = True
            if args.mode != "analyze":
                backup_confirm = input("Créer une sauvegarde avant de procéder aux modifications? [Y/n]: ").strip().lower()
                backup_confirm = not backup_confirm or backup_confirm in ('y', 'yes', 'oui')
            
            if backup_confirm:
                backup_time = datetime.now().strftime("%Y%m%d%H%M%S")
                backup_dir = project_path.parent / f"{project_path.name}_backup_{backup_time}"
                
                try:
                    logger.info(f"Création d'une sauvegarde du projet: {backup_dir}")
                    shutil.copytree(project_path, backup_dir, ignore=shutil.ignore_patterns('.git', '__pycache__', '.DS_Store'))
                    logger.info(f"Sauvegarde créée: {backup_dir}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
                    if not args.yes:
                        confirm = input("Impossible de créer une sauvegarde. Continuer quand même? [y/N]: ").strip().lower()
                        if confirm not in ('y', 'yes', 'oui'):
                            logger.info("Opération annulée.")
                            return 0
                    else:
                        logger.warning("Les modifications seront effectuées sans sauvegarde (mode automatique).")
        
        # Regrouper les problèmes pour le traitement par lots
        issue_groups = group_issues_by_pattern(all_issues)
        
        # Créer le plan de correction
        correction_plan = generate_correction_plan(all_issues, issue_groups)
        
        # En mode interactif, présenter le plan et demander confirmation
        if args.mode == "interactive" and not args.yes:
            execution_plan = present_correction_plan(correction_plan, True)
        else:
            # En mode fix non-interactif, exécuter toutes les étapes
            execution_plan = {i+1: True for i in range(len(correction_plan))}
            if not args.yes:
                # Si pas --yes, demander confirmation globale
                all_changes = sum(step['count'] for step in correction_plan)
                print(f"\nLes modifications suivantes seront effectuées:")
                for i, step in enumerate(correction_plan, 1):
                    print(f"- {step['title']} ({step['count']} éléments)")
                
                confirm = input(f"\nVoulez-vous procéder à ces {all_changes} corrections? [Y/n]: ").strip().lower()
                if confirm and confirm not in ('y', 'yes', 'oui'):
                    logger.info("Opération de correction annulée par l'utilisateur.")
                    
                    # Créer quand même le rapport pour référence
                    report_path = create_markdown_report(project_path, all_issues, {}, args.output)
                    logger.info(f"Rapport détaillé créé sans corrections: {report_path}")
                    
                    return 0
        
        # Exécuter le plan de correction
        interactive_mode = args.mode == "interactive" and not args.yes
        correction_results = execute_correction_plan(project_path, correction_plan, execution_plan, interactive_mode)
        
        # Vérifier à nouveau pour voir les problèmes résolus
        logger.info("Nouvelle vérification après corrections...")
        
        new_issues = []
        try:
            new_issues.extend(validate_structure(project_path, EXPECTED_STRUCTURE))
            new_issues.extend(validate_template_existence(project_path))
            new_issues.extend(validate_frontmatter(project_path))
            new_issues.extend(check_broken_links(project_path))
        except Exception as e:
            logger.error(f"Erreur pendant la vérification post-correction: {e}")
        
        new_error_count = sum(1 for issue in new_issues if issue['level'] == 'error')
        new_warning_count = sum(1 for issue in new_issues if issue['level'] == 'warning')
        
        logger.info(f"Après corrections: {new_error_count} erreurs et {new_warning_count} avertissements restants.")
        
        # Mettre à jour la liste des problèmes pour le rapport
        all_issues = new_issues
    
    # Créer le rapport Markdown
    report_path = create_markdown_report(project_path, all_issues, correction_results, args.output)
    logger.info(f"Rapport détaillé créé: {report_path}")
    
    # En mode rapport ou après corrections, créer des tâches pour les problèmes complexes
    if args.mode in ["report", "fix", "interactive"] and len(all_issues) > 0:
        logger.info("Création des tâches de révision manuelle pour les problèmes complexes...")
        
        # Grouper les problèmes par fichier
        grouped_issues = {}
        for issue in all_issues:
            if 'path' not in issue:
                continue
                
            path = issue['path']
            if path not in grouped_issues:
                grouped_issues[path] = []
            grouped_issues[path].append(issue)
        
        tasks_created = 0
        
        for file_path, file_issues in grouped_issues.items():
            # Déterminer si ce fichier nécessite une révision manuelle
            # (problèmes complexes uniquement, non résolus automatiquement)
            has_errors = any(issue['level'] == 'error' for issue in file_issues)
            has_frontmatter_issues = any('frontmatter' in issue['type'] for issue in file_issues)
            has_parsing_errors = any('parsing_error' in issue['type'] for issue in file_issues)
            has_missing_required = any('missing_required_field' in issue['type'] for issue in file_issues)
            
            # Ne créer une tâche que si le fichier a des problèmes complexes
            complex_issues = has_errors and (has_frontmatter_issues or has_parsing_errors or has_missing_required)
            if complex_issues:
                try:
                    task_path = create_manual_review_task(project_path, file_path, file_issues)
                    if task_path:
                        tasks_created += 1
                        logger.info(f"Tâche créée pour {file_path}: {task_path}")
                except Exception as e:
                    logger.error(f"Erreur lors de la création de la tâche pour {file_path}: {e}")
        
        logger.info(f"{tasks_created} tâches de révision manuelle créées.")
    
    # Retourner 1 s'il y a des erreurs, 0 sinon
    return 1 if error_count > 0 else 0

if __name__ == "__main__":
    sys.exit(main())#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions pour l'exécution du plan de correction et l'intégration avec le script principal
"""

import os
import re
import sys
import logging
import argparse
import shutil
import yaml
from pathlib import Path
from datetime import datetime, timedelta

# Importer les fonctions des modules précédents
from verify_structure_improved_part1 import (
    find_similar_files,
    detect_common_path_issues,
    suggest_prefix_replacements,
    replace_link_in_file,
    fix_prefix_in_group,
    create_missing_file
)

from verify_structure_improved_part2 import (
    group_issues_by_pattern,
    prioritize_issues,
    generate_correction_plan,
    present_correction_plan,
    batch_fix_broken_links,
    batch_create_missing_files
)

# Configuration du logging
logger = logging.getLogger('structure_verification')

def setup_logging(verbose=False):
    """Configure le système de logging."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Configurer le logger principal
    logger.setLevel(log_level)
    
    # Créer un formateur
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Créer et configurer le handler pour le fichier
    file_handler = logging.FileHandler("structure_verification.log")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Créer et configurer le handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers au logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def execute_correction_plan(project_path, plan, execution_plan, interactive=True):
    """
    Exécute le plan de correction en fonction des étapes approuvées.
    
    Args:
        project_path (Path): Chemin de base du projet
        plan (list): Plan de correction généré
        execution_plan (dict): Étapes approuvées pour exécution
        interactive (bool): Mode interactif pour les confirmations
        
    Returns:
        dict: Résultats des corrections par étape
    """
    results = {}
    
    for i, step in enumerate(plan, 1):
        if not execution_plan.get(i, False):
            logger.info(f"Étape {i} ({step['title']}) ignorée.")
            results[i] = {'executed': False, 'fixed': 0, 'total': step['count']}
            continue
        
        logger.info(f"Exécution de l'étape {i}: {step['title']}")
        
        # Exécuter l'action appropriée selon le type d'étape
        fixed = 0
        action = step.get('action', 'unknown')
        
        if action == 'create_missing_dirs':
            # Créer les dossiers manquants
            for issue in step['items']:
                dir_path = project_path / issue['path']
                try:
                    if not dir_path.exists():
                        os.makedirs(dir_path, exist_ok=True)
                        logger.info(f"Répertoire créé: {dir_path}")
                        fixed += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la création du répertoire {dir_path}: {e}")
        
        elif action == 'create_missing_files':
            # Créer les fichiers manquants
            fixed = batch_create_missing_files(project_path, step['items'], interactive)
        
        elif action == 'copy_missing_templates':
            # Copier les templates manquants
            for issue in step['items']:
                template_name = os.path.basename(issue['path'])
                
                # Chercher le template dans les sources possibles
                template_found = False
                
                # 1. Chercher dans le dossier review/claude_suggestions
                suggestions_dir = project_path / "review" / "claude_suggestions"
                for suggestion_file in suggestions_dir.glob(f"*{template_name}*"):
                    try:
                        template_dest = project_path / "templates" / template_name
                        shutil.copy2(suggestion_file, template_dest)
                        logger.info(f"Template copié de {suggestion_file} vers {template_dest}")
                        template_found = True
                        fixed += 1
                        break
                    except Exception as e:
                        logger.error(f"Erreur lors de la copie du template {template_name}: {e}")
                
                # 2. Créer un template par défaut si non trouvé
                if not template_found:
                    template_dest = project_path / "templates" / template_name
                    try:
                        with open(template_dest, 'w', encoding='utf-8') as f:
                            template_content = f"""---
title: Template {template_name.replace('.md', '')}
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {{{{title}}}}

<!-- Template créé automatiquement -->

## Contenu

<!-- Ajoutez le contenu du template ici -->

"""
                            f.write(template_content)
                        logger.info(f"Template par défaut créé: {template_dest}")
                        fixed += 1
                    except Exception as e:
                        logger.error(f"Erreur lors de la création du template {template_name}: {e}")
        
        elif action == 'fix_frontmatter':
            # Corriger les problèmes de frontmatter
            file_type = step.get('file_type', 'unknown')
            logger.info(f"Correction des frontmatter pour les fichiers de type {file_type}...")
            
            # Cette action nécessite souvent une intervention manuelle
            # Génération de tâches TODO pour les problèmes complexes
            todo_tasks_created = 0
            
            for issue in step['items']:
                if 'frontmatter_parsing_error' in issue['type'] or 'missing_required_field' in issue['type']:
                    todo_path = create_manual_review_task(project_path, issue['path'], [issue])
                    if todo_path:
                        todo_tasks_created += 1
            
            if todo_tasks_created > 0:
                logger.info(f"{todo_tasks_created} tâches de révision manuelle créées pour les problèmes de frontmatter.")
            
            if interactive:
                print(f"{todo_tasks_created} tâches de révision manuelle créées pour les problèmes de frontmatter.")
                print("Ces fichiers nécessitent une intervention humaine et ne peuvent pas être corrigés automatiquement.")
            
            fixed = todo_tasks_created
        
        elif action == 'fix_broken_links':
            # Corriger les liens cassés pour ce motif
            pattern = step.get('pattern', '')
            broken_links = {pattern: step['items']}
            fixed = batch_fix_broken_links(project_path, broken_links, interactive)
        
        else:
            logger.warning(f"Action inconnue: {action}")
        
        results[i] = {'executed': True, 'fixed': fixed, 'total': step['count']}
        logger.info(f"Étape {i} terminée: {fixed} éléments corrigés sur {step['count']}.")
    
    return results

def create_manual_review_task(project_path, file_path, issues):
    """
    Crée une tâche de révision manuelle pour un fichier problématique.
    
    Args:
        project_path (Path): Chemin de base du projet
        file_path (str): Chemin relatif du fichier problématique
        issues (list): Liste des problèmes détectés pour ce fichier
        
    Returns:
        str: Chemin du fichier de tâche créé ou None si échec
    """
    # Générer un ID unique pour la tâche
    task_id = f"TODO-{datetime.now().strftime('%Y%m%d%H%M')}-{os.path.basename(file_path).split('.')[0][:4].upper()}"
    
    # Définir le chemin de sortie
    output_dir = project_path / "review" / "claude_suggestions"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        logger.error(f"Impossible de créer le dossier {output_dir}: {e}")
        return None
    
    output_filename = f"{task_id}-structure-revision.md"
    output_path = output_dir / output_filename
    
    # Formatter les problèmes détectés pour le contenu de la tâche
    issues_content = ""
    for i, issue in enumerate(issues, 1):
        issues_content += f"{i}. **{issue['type'].replace('_', ' ').title()}**:\n"
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

**IMPORTANT**: Ne pas utiliser d'outils automatisés pour modifier ce fichier avant d'avoir résolu les problèmes structurels.
"""
    
    # Écrire le fichier de tâche
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Tâche de révision manuelle créée: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"Erreur lors de la création de la tâche de révision pour {file_path}: {e}")
        return None

def create_markdown_report(project_path, issues, results, output_file="structure-report.md"):
    """
    Crée un rapport au format Markdown des problèmes de structure détectés et des corrections effectuées.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes détectés
        results (dict): Résultats des corrections effectuées
        output_file (str): Nom du fichier de sortie
        
    Returns:
        str: Chemin du fichier de rapport créé
    """
    # Compter les problèmes par niveau
    error_count = sum(1 for issue in issues if issue['level'] == 'error')
    warning_count = sum(1 for issue in issues if issue['level'] == 'warning')
    
    # Calculer le nombre total de corrections effectuées
    total_fixed = sum(step['fixed'] for step in results.values() if step['executed'])
    
    # Créer le contenu du rapport
    report_content = f"""# Rapport de vérification et correction de structure

Projet: {project_path}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Résumé

- **Erreurs initiales**: {error_count}
- **Avertissements initiaux**: {warning_count}
- **Total des problèmes**: {len(issues)}
- **Problèmes corrigés**: {total_fixed}

## Actions effectuées

"""
    
    # Ajouter les résultats des étapes exécutées
    for step_num, result in results.items():
        if result['executed']:
            report_content += f"### Étape {step_num}\n"
            report_content += f"- **{result['fixed']}** éléments corrigés sur {result['total']}\n"
            if result['fixed'] < result['total']:
                report_content += f"- {result['total'] - result['fixed']} éléments non corrigés\n"
            report_content += "\n"
    
    # Ajouter les problèmes restants
    remaining_issues = []
    for issue in issues:
        # Vérifier si ce problème a été corrigé
        issue_path = issue.get('path', '')
        issue_type = issue.get('type', '')
        
        # Logique simple pour déterminer si un problème a été corrigé
        # (cette logique pourrait être améliorée pour être plus précise)
        corrected = False
        
        # Si c'est un répertoire manquant et qu'il existe maintenant, il est corrigé
        if issue_type == 'missing_required' and '.md' not in issue_path:
            dir_path = project_path / issue_path
            if dir_path.exists() and dir_path.is_dir():
                corrected = True
        
        # Si c'est un fichier manquant et qu'il existe maintenant, il est corrigé
        elif issue_type == 'missing_required' and '.md' in issue_path:
            file_path = project_path / issue_path
            if file_path.exists() and file_path.is_file():
                corrected = True
        
        # Pour les autres types, on devrait avoir une logique plus complexe
        # Par simplicité, on les considère comme non corrigés ici
        
        if not corrected:
            remaining_issues.append(issue)
    
    # S'il reste des problèmes, les ajouter au rapport
    if remaining_issues:
        report_content += """
## Problèmes restants

Les problèmes suivants n'ont pas été corrigés automatiquement et nécessitent une attention manuelle.

"""
        
        # Regrouper les problèmes par type
        issues_by_type = {}
        for issue in remaining_issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # Ajouter les problèmes au rapport, regroupés par type
        for issue_type, type_issues in sorted(issues_by_type.items()):
            report_content += f"### {issue_type.replace('_', ' ').title()} ({len(type_issues)})\n\n"
            
            for issue in sorted(type_issues, key=lambda x: x.get('path', '')):
                level_icon = "🔴" if issue['level'] == 'error' else "🟠"
                path_info = f" **{issue['path']}**:" if 'path' in issue else ""
                report_content += f"- {level_icon}{path_info} {issue['message']}\n"
            
            report_content += "\n"
    else:
        report_content += """
## Tous les problèmes ont été corrigés!

Aucun problème restant n'a été détecté. La structure du projet est maintenant conforme aux attentes.
"""
    
    # Ajouter des recommandations si nécessaire
    if remaining_issues:
        report_content += """
## Recommandations

1. Examinez les problèmes restants et corrigez-les manuellement
2. Portez une attention particulière aux problèmes de frontmatter YAML
3. Vérifiez que les liens internes fonctionnent correctement
4. Exécutez à nouveau ce script pour confirmer que tous les problèmes ont été résolus

"""
    
    # Écrire le rapport dans un fichier
    output_path = project_path / output_file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    logger.info(f"Rapport de structure créé: {output_path}")
    return str(output_path)

def main():
    """
    Fonction principale du script amélioré.
    """
    parser = argparse.ArgumentParser(description="Vérifie et corrige la structure du projet d'édition littéraire.")
    parser.add_argument("--project-dir", default=".", help="Chemin vers le répertoire du projet")
    parser.add_argument("--mode", choices=["analyze", "report", "fix", "interactive"], default="analyze", 
                       help="Mode de fonctionnement: 'analyze' (vérification simple), 'report' (génère des tâches), 'fix' (corrections automatiques) ou 'interactive' (corrections guidées)")
    parser.add_argument("--verbose", action="store_true", help="Affiche des informations détaillées")
    parser.add_argument("--output", default="structure-report.md", help="Chemin vers le fichier de sortie pour le rapport")
    parser.add_argument("--yes", "-y", action="store_true", help="Mode non-interactif: répond 'oui' à toutes les questions")
    
    args = parser.parse_args()
    
    # Configurer le logging
    setup_logging(args.verbose)
    
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
        auto_confirm = hasattr(args, 'yes') and args.yes
        if not auto_confirm:
            confirm = input("Continuer quand même? [y/N]: ").strip().lower()
            if confirm not in ('y', 'yes', 'oui'):
                logger.info("Opération annulée.")
                return 0
        else:
            logger.info("Continuation forcée (mode automatique).")
    
    # Importer les fonctions nécessaires du script original
    # Cette section devrait importer les fonctions du script existant qui sont nécessaires
    # (validate_structure, validate_template_existence, validate_frontmatter, check_broken_links)
    # Pour cet exemple, nous supposons qu'elles sont disponibles dans un module nommé validate_functions
    
    try:
        from verify_structure_script import (
            EXPECTED_STRUCTURE,
            EXPECTED_TEMPLATES,
            FRONTMATTER_RULES,
            validate_structure,
            validate_template_existence,
            validate_frontmatter,
            check_broken_links
        )
    except ImportError:
        logger.error("Impossible d'importer les fonctions du script original. Assurez-vous que verify_structure_script.py est dans le même répertoire.")
        return 1