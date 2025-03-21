#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions pour le traitement par lots et la prioritisation des problèmes
"""

import os
import re
import logging
import textwrap
from pathlib import Path

logger = logging.getLogger('structure_verification')

def group_issues_by_pattern(issues):
    """
    Regroupe les problèmes par motifs similaires pour un traitement par lots.
    
    Args:
        issues (list): Liste des problèmes détectés
        
    Returns:
        dict: Dictionnaire des groupes de problèmes
    """
    groups = {
        'missing_dirs': [],
        'missing_files': [],
        'broken_links': {},
        'frontmatter_issues': {},
        'template_issues': [],
        'other_issues': []
    }
    
    # Regrouper les problèmes par type
    for issue in issues:
        if issue['type'] == 'missing_required' and '.md' not in issue['path']:
            groups['missing_dirs'].append(issue)
        elif issue['type'] == 'missing_required' and '.md' in issue['path']:
            groups['missing_files'].append(issue)
        elif issue['type'] == 'missing_template':
            groups['template_issues'].append(issue)
        elif issue['type'] == 'broken_link':
            # Extraire le lien cassé
            link_match = re.search(r"'([^']+)'", issue['message'])
            if not link_match:
                groups['other_issues'].append(issue)
                continue
                
            link = link_match.group(1)
            
            # Déterminer le motif (par ex: docs/, personnages/, etc.)
            pattern = 'autres'
            parts = link.split('/')
            if len(parts) > 1:
                pattern = parts[0]
            
            if pattern not in groups['broken_links']:
                groups['broken_links'][pattern] = []
            groups['broken_links'][pattern].append(issue)
        elif 'frontmatter' in issue['type']:
            # Regrouper par type de fichier
            file_type = 'autres'
            path = issue['path']
            
            if 'personnages/' in path:
                file_type = 'personnages'
            elif 'chapitres/' in path:
                file_type = 'chapitres'
            elif 'structure/' in path:
                file_type = 'structure'
            elif 'review/' in path:
                file_type = 'review'
            
            if file_type not in groups['frontmatter_issues']:
                groups['frontmatter_issues'][file_type] = []
            groups['frontmatter_issues'][file_type].append(issue)
        else:
            groups['other_issues'].append(issue)
    
    return groups

def prioritize_issues(issues):
    """
    Classe les problèmes par ordre de priorité pour une résolution efficace.
    
    Args:
        issues (list): Liste des problèmes détectés
        
    Returns:
        list: Liste des problèmes classés par priorité
    """
    # Définir les poids de priorité pour chaque type de problème
    priority_weights = {
        'missing_required': 100,    # Éléments requis manquants (plus haute priorité)
        'missing_template': 90,     # Templates manquants
        'type_mismatch': 80,        # Type incorrect (fichier vs dossier)
        'frontmatter_parsing_error': 70,  # Erreurs de parsing YAML
        'missing_required_field': 60,     # Champs requis manquants
        'broken_link': 50,          # Liens cassés
        'invalid_tags': 40,         # Tags invalides
        'missing_recommended_field': 30,  # Champs recommandés manquants
        'missing_optional': 20,     # Éléments optionnels manquants (priorité plus basse)
        'default': 10               # Valeur par défaut pour les autres types
    }
    
    # Fonction de calcul du score de priorité
    def get_priority_score(issue):
        # Score de base selon le type d'issue
        base_score = priority_weights.get(issue['type'], priority_weights['default'])
        
        # Ajustements basés sur le niveau de sévérité
        level_multiplier = 2 if issue['level'] == 'error' else 1
        
        # Ajustements basés sur le chemin (les fichiers de structure ont une priorité plus élevée)
        path_bonus = 0
        if 'path' in issue:
            if 'structure/' in issue['path']:
                path_bonus += 20
            elif 'templates/' in issue['path']:
                path_bonus += 15
            elif 'index.md' in issue['path']:
                path_bonus += 10
        
        return base_score * level_multiplier + path_bonus
    
    # Trier les problèmes selon le score de priorité
    prioritized_issues = sorted(issues, key=get_priority_score, reverse=True)
    
    return prioritized_issues

def generate_correction_plan(issues, groups):
    """
    Génère un plan de correction étape par étape basé sur les problèmes détectés.
    
    Args:
        issues (list): Liste des problèmes détectés
        groups (dict): Groupes de problèmes similaires
        
    Returns:
        list: Plan d'actions recommandées
    """
    plan = []
    
    # Étape 1: Corriger la structure de base (dossiers requis)
    if groups['missing_dirs']:
        plan.append({
            'title': "Créer les dossiers manquants",
            'description': "Ces dossiers sont requis pour la structure de base du projet.",
            'count': len(groups['missing_dirs']),
            'items': groups['missing_dirs'],
            'action': 'create_missing_dirs'
        })
    
    # Étape 2: Corriger les fichiers de structure manquants
    if groups['missing_files']:
        plan.append({
            'title': "Créer les fichiers de structure manquants",
            'description': "Ces fichiers sont essentiels à la structure du projet.",
            'count': len(groups['missing_files']),
            'items': groups['missing_files'],
            'action': 'create_missing_files'
        })
    
    # Étape 3: Corriger les templates manquants
    if groups['template_issues']:
        plan.append({
            'title': "Ajouter les templates manquants",
            'description': "Les templates sont essentiels pour maintenir la cohérence du projet.",
            'count': len(groups['template_issues']),
            'items': groups['template_issues'],
            'action': 'copy_missing_templates'
        })
    
    # Étape 4: Corriger les problèmes de frontmatter par type de fichier
    for file_type, frontmatter_issues in groups['frontmatter_issues'].items():
        if frontmatter_issues:
            plan.append({
                'title': f"Corriger les problèmes de frontmatter dans les fichiers {file_type}",
                'description': "Les métadonnées frontmatter sont essentielles pour les fonctionnalités d'Obsidian.",
                'count': len(frontmatter_issues),
                'items': frontmatter_issues,
                'action': 'fix_frontmatter',
                'file_type': file_type
            })
    
    # Étape 5: Corriger les liens cassés par groupe
    for pattern, link_issues in groups['broken_links'].items():
        if link_issues:
            plan.append({
                'title': f"Corriger les liens cassés avec le motif '{pattern}/'",
                'description': f"Ces liens cassés partagent un motif commun et peuvent être traités ensemble.",
                'count': len(link_issues),
                'items': link_issues,
                'action': 'fix_broken_links',
                'pattern': pattern
            })
    
    # Étape 6: Autres problèmes
    if groups['other_issues']:
        plan.append({
            'title': "Corriger les autres problèmes",
            'description': "Problèmes divers qui nécessitent une attention particulière.",
            'count': len(groups['other_issues']),
            'items': groups['other_issues'],
            'action': 'fix_other_issues'
        })
    
    return plan

def present_correction_plan(plan, interactive=True):
    """
    Présente le plan de correction à l'utilisateur et permet une exécution étape par étape.
    
    Args:
        plan (list): Plan de correction généré
        interactive (bool): Mode interactif pour obtenir des confirmations
        
    Returns:
        dict: Plan d'exécution avec les étapes approuvées
    """
    if not plan:
        print("\nAucun problème à corriger. Tout est en ordre!")
        return {}
        
    execution_plan = {}
    
    print("\n" + "="*50)
    print(" PLAN DE CORRECTION ")
    print("="*50)
    
    for i, step in enumerate(plan, 1):
        print(f"\n{i}. {step['title']} ({step['count']} éléments)")
        print("   " + "-"*40)
        print("   " + step['description'])
        
        # Afficher quelques exemples
        print("\n   Exemples:")
        for item in step['items'][:3]:  # Limiter à 3 exemples
            if 'path' in item:
                message = textwrap.shorten(item['message'], width=70, placeholder="...")
                print(f"   - {item['path']}: {message}")
            else:
                message = textwrap.shorten(item['message'], width=80, placeholder="...")
                print(f"   - {message}")
        
        if len(step['items']) > 3:
            print(f"   ... et {len(step['items']) - 3} autres éléments")
        
        print()
        
        if interactive:
            action = input(action_prompt).strip()
        else:
            # Mode non-interactif: commencer par les préfixes
            action = "1"
        
        # Appliquer l'action choisie
        group_fixed = 0
        
        if action == "1":
            # Corriger les préfixes
            prefix = pattern if pattern in prefix_suggestions else None
            if prefix:
                replacement = prefix_suggestions[prefix]
                fixed = fix_prefix_in_group(project_path, issues, prefix, replacement)
                group_fixed += fixed
                if interactive:
                    print(f"  ✓ {fixed} liens corrigés en remplaçant '{prefix}/' par '{replacement}/'")
            elif interactive:
                print("  Aucune correction de préfixe applicable pour ce groupe")
                
                # Si aucune correction de préfixe n'est possible, proposer l'option 2
                second_choice = input("  Essayer de trouver des fichiers similaires à la place? [Y/n]: ").strip().lower()
                if not second_choice or second_choice in ('y', 'yes', 'oui'):
                    action = "2"
                else:
                    continue
        
        if action == "2":
            # Chercher des fichiers similaires
            for issue in issues:
                link_match = re.search(r"'([^']+)'", issue['message'])
                if not link_match:
                    continue
                    
                link = link_match.group(1)
                similar_files = find_similar_files(project_path, link)
                
                if similar_files:
                    file_path = project_path / issue['path']
                    best_match = similar_files[0][0]
                    similarity_score = similar_files[0][1]
                    
                    # Déterminer automatiquement si le score est suffisamment élevé
                    auto_accept = similarity_score > 0.8  # Score très élevé = acceptation automatique
                    
                    if interactive and not auto_accept:
                        print(f"\nPour le lien '{link}' dans {issue['path']}:")
                        print(f"  Meilleure correspondance: {best_match} (score: {similarity_score:.2f})")
                        
                        # Si plusieurs correspondances, les afficher
                        if len(similar_files) > 1:
                            print("  Autres correspondances possibles:")
                            for i, (alt_match, alt_score) in enumerate(similar_files[1:3], 1):  # Limiter à 2 alternatives
                                print(f"    {i}. {alt_match} (score: {alt_score:.2f})")
                            
                            choice = input("  Utiliser quelle correspondance? [1 = meilleure/2/3/n(on)]: ").strip().lower()
                            
                            if choice == "2" and len(similar_files) >= 2:
                                best_match = similar_files[1][0]
                            elif choice == "3" and len(similar_files) >= 3:
                                best_match = similar_files[2][0]
                            elif choice in ('n', 'no', 'non'):
                                continue
                        else:
                            approval = input("  Remplacer par cette correspondance? [Y/n]: ").strip().lower()
                            if approval and approval not in ('y', 'yes', 'oui'):
                                continue
                    
                    # Effectuer le remplacement
                    success = replace_link_in_file(file_path, link, best_match)
                    if success:
                        group_fixed += 1
                        if interactive:
                            print(f"  ✓ Lien corrigé: '{link}' → '{best_match}'")
                elif interactive:
                    print(f"\nAucune correspondance trouvée pour '{link}' dans {issue['path']}")
                    create_option = input("  Créer ce fichier? [y/N]: ").strip().lower()
                    if create_option in ('y', 'yes', 'oui'):
                        action = "3"  # Basculer vers la création de fichier pour ce lien
                        template_name = input("  Nom du template à utiliser (vide pour le template par défaut): ").strip()
                        success = create_missing_file(project_path, link, template_name)
                        if success:
                            group_fixed += 1
        
        elif action == "3":
            # Créer les fichiers manquants
            template_name = None
            if interactive:
                template_name = input("Nom du template à utiliser (vide pour le template par défaut): ").strip()
            
            for issue in issues:
                link_match = re.search(r"'([^']+)'", issue['message'])
                if not link_match:
                    continue
                    
                link = link_match.group(1)
                success = create_missing_file(project_path, link, template_name)
                if success:
                    group_fixed += 1
        
        total_fixed += group_fixed
        
        if interactive:
            print(f"Groupe '{pattern}/': {group_fixed} liens traités sur {len(issues)}")
    
    return total_fixed

def batch_create_missing_files(project_path, missing_files, interactive=True):
    """
    Crée par lots les fichiers manquants identifiés.
    
    Args:
        project_path (Path): Chemin de base du projet
        missing_files (list): Liste des problèmes de fichiers manquants
        interactive (bool): Demander confirmation à l'utilisateur
        
    Returns:
        int: Nombre de fichiers créés
    """
    files_created = 0
    
    # Regrouper les fichiers par type
    file_groups = {}
    for issue in missing_files:
        file_path = issue['path']
        file_type = 'autres'
        
        if 'personnages/' in file_path:
            file_type = 'personnage'
        elif 'structure/' in file_path:
            file_type = 'structure'
        elif file_path.endswith('index.md'):
            file_type = 'index'
        elif 'chapitre' in file_path:
            file_type = 'chapitre'
        
        if file_type not in file_groups:
            file_groups[file_type] = []
        file_groups[file_type].append(issue)
    
    # Traiter chaque groupe
    for file_type, issues in file_groups.items():
        if not issues:
            continue
        
        if interactive:
            print(f"\nTraitement de {len(issues)} fichiers manquants de type '{file_type}':")
            for i, issue in enumerate(issues[:5]):  # Montrer seulement les 5 premiers exemples
                print(f"  {i+1}. {issue['path']}")
            if len(issues) > 5:
                print(f"  ... et {len(issues) - 5} autres")
        
        # Déterminer le template à utiliser
        template_name = None
        if interactive:
            default_template = file_type if file_type != 'autres' else ''
            template_prompt = f"Nom du template à utiliser [par défaut: {default_template or 'générique'}]: "
            template_input = input(template_prompt).strip()
            template_name = template_input if template_input else default_template
        else:
            template_name = file_type if file_type != 'autres' else None
        
        # Créer les fichiers
        for issue in issues:
            file_path = issue['path']
            success = create_missing_file(project_path, file_path, template_name)
            if success:
                files_created += 1
        
        if interactive:
            print(f"Groupe '{file_type}': {files_created} fichiers créés sur {len(issues)}")
    
    return files_created

# Importer les fonctions nécessaires du module précédent
from verify_structure_improved_part1 import (
    find_similar_files, 
    detect_common_path_issues, 
    suggest_prefix_replacements, 
    replace_link_in_file, 
    fix_prefix_in_group, 
    create_missing_file
)f"Exécuter l'étape {i}? [Y/n/v(voir plus)]: ").strip().lower()
            
            if action == 'v':
                # Afficher plus de détails
                print("\n   Détails complets:")
                for j, item in enumerate(step['items'], 1):
                    if 'path' in item:
                        print(f"   {j}. {item['path']}: {item['message']}")
                    else:
                        print(f"   {j}. {item['message']}")
                print()
                
                action = input(f"Exécuter l'étape {i}? [Y/n]: ").strip().lower()
            
            execution_plan[i] = not action or action in ('y', 'yes', 'oui')
        else:
            execution_plan[i] = True
            print("   [Étape approuvée automatiquement en mode non-interactif]")
    
    return execution_plan

def batch_fix_broken_links(project_path, link_groups, interactive=True):
    """
    Corrige par lots des groupes de liens cassés similaires.
    
    Args:
        project_path (Path): Chemin de base du projet
        link_groups (dict): Groupes de liens cassés par motif
        interactive (bool): Demander confirmation à l'utilisateur
        
    Returns:
        int: Nombre de liens corrigés
    """
    total_fixed = 0
    
    # Détecter les préfixes problématiques
    all_broken_links = []
    for group in link_groups.values():
        all_broken_links.extend(group)
    
    prefix_patterns = detect_common_path_issues(all_broken_links)
    prefix_suggestions = suggest_prefix_replacements(prefix_patterns, project_path)
    
    # Proposer des corrections par préfixe
    if prefix_suggestions and interactive:
        print("\nCorrections de préfixe suggérées:")
        for prefix, suggestion in prefix_suggestions.items():
            count = prefix_patterns.get(prefix, 0)
            print(f"  '{prefix}/' → '{suggestion}/' ({count} occurrences)")
        
        apply_all = input("\nAppliquer toutes ces corrections de préfixe? [Y/n/s(elect)]: ").strip().lower()
        
        if apply_all == 's' or apply_all == 'select':
            # Mode sélection individuelle
            approved_prefixes = {}
            for prefix, suggestion in prefix_suggestions.items():
                approval = input(f"  Remplacer '{prefix}/' par '{suggestion}/'? [Y/n]: ").strip().lower()
                if not approval or approval in ('y', 'yes', 'oui'):
                    approved_prefixes[prefix] = suggestion
            prefix_suggestions = approved_prefixes
        elif apply_all and apply_all not in ('y', 'yes', 'oui'):
            prefix_suggestions = {}  # Annuler toutes les suggestions
    
    # Traiter chaque groupe de liens
    for pattern, issues in link_groups.items():
        if not issues:
            continue
        
        if interactive:
            print(f"\nTraitement de {len(issues)} liens cassés avec le motif '{pattern}/':")
            for i, issue in enumerate(issues[:5]):  # Montrer seulement les 5 premiers exemples
                link_match = re.search(r"'([^']+)'", issue['message'])
                if link_match:
                    link = link_match.group(1)
                    print(f"  {i+1}. {link} (dans {issue['path']})")
            if len(issues) > 5:
                print(f"  ... et {len(issues) - 5} autres")
        
        # Déterminer l'action pour ce groupe
        action = None
        if interactive:
            action_prompt = """
Quelle action souhaitez-vous effectuer pour ce groupe?
1. Corriger les préfixes (si applicable)
2. Chercher des fichiers similaires pour chaque lien
3. Créer les fichiers manquants
4. Ignorer ce groupe
Votre choix [1-4]: """
            action = input(