#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fonctions améliorées pour la détection et la correction de liens cassés
"""

import os
import re
import logging
from pathlib import Path
from difflib import SequenceMatcher

logger = logging.getLogger('structure_verification')

def find_similar_files(project_path, broken_link):
    """
    Recherche des fichiers similaires au lien cassé dans le projet.
    
    Args:
        project_path (Path): Chemin de base du projet
        broken_link (str): Lien cassé à rechercher
        
    Returns:
        list: Liste de fichiers similaires trouvés [(chemin, score_similitude)]
    """
    # Extraire le nom de fichier sans le chemin
    link_parts = broken_link.split('/')
    filename = link_parts[-1]
    
    # Si le nom de fichier contient une extension, la conserver, sinon ajouter .md
    if '.' not in filename:
        filename += '.md'
    
    # Rechercher des fichiers avec le même nom dans tout le projet
    similar_files = []
    for file_path in project_path.glob(f'**/{filename}'):
        # Ignorer les fichiers dans .git, export, etc.
        if any(part.startswith('.') for part in file_path.parts) or 'export' in file_path.parts:
            continue
        
        rel_path = file_path.relative_to(project_path)
        
        # Calculer un score de similarité
        similarity = calculate_path_similarity(str(rel_path), broken_link)
        similar_files.append((str(rel_path), similarity))
    
    # Si aucun fichier avec le même nom n'est trouvé, chercher des noms similaires
    if not similar_files:
        for file_path in project_path.glob('**/*.md'):
            # Ignorer les fichiers dans .git, export, etc.
            if any(part.startswith('.') for part in file_path.parts) or 'export' in file_path.parts:
                continue
            
            rel_path = file_path.relative_to(project_path)
            file_basename = os.path.basename(str(rel_path))
            link_basename = os.path.basename(broken_link)
            
            # Calculer la similarité entre les noms de fichier
            name_similarity = SequenceMatcher(None, file_basename, link_basename).ratio()
            if name_similarity > 0.6:  # Seuil de similarité pour les noms
                # Calculer la similarité globale du chemin
                path_similarity = calculate_path_similarity(str(rel_path), broken_link)
                # Combiner les deux scores, en donnant plus de poids à la similarité du nom
                combined_similarity = (name_similarity * 0.7) + (path_similarity * 0.3)
                if combined_similarity > 0.5:  # Seuil minimal de similarité combinée
                    similar_files.append((str(rel_path), combined_similarity))
    
    return sorted(similar_files, key=lambda x: x[1], reverse=True)

def calculate_path_similarity(path1, path2):
    """
    Calcule un score de similarité entre deux chemins.
    
    Args:
        path1 (str): Premier chemin
        path2 (str): Deuxième chemin
        
    Returns:
        float: Score de similarité (0.0 à 1.0)
    """
    # Normaliser les chemins (remplacer \ par / et supprimer .md si présent)
    path1 = path1.replace('\\', '/')
    path2 = path2.replace('\\', '/')
    
    if path1.endswith('.md'):
        path1 = path1[:-3]
    if path2.endswith('.md'):
        path2 = path2[:-3]
    
    # Diviser en parties
    parts1 = path1.split('/')
    parts2 = path2.split('/')
    
    # Score de base pour le nom de fichier
    filename1 = parts1[-1]
    filename2 = parts2[-1]
    filename_similarity = SequenceMatcher(None, filename1, filename2).ratio()
    
    # Score pour les dossiers parents
    parent_similarity = 0
    if len(parts1) > 1 and len(parts2) > 1:
        # Calculer le nombre de parties communes
        common_parts = sum(1 for p1, p2 in zip(parts1[:-1], parts2[:-1]) if p1 == p2)
        max_parts = max(len(parts1) - 1, len(parts2) - 1)  # -1 pour exclure le nom de fichier
        if max_parts > 0:
            parent_similarity = common_parts / max_parts
    
    # Combiner les scores (poids plus important pour le nom de fichier)
    return (filename_similarity * 0.7) + (parent_similarity * 0.3)

def detect_common_path_issues(issues):
    """
    Détecte les problèmes de chemin communs (par exemple, préfixe 'docs/' incorrect).
    
    Args:
        issues (list): Liste des problèmes de liens cassés
        
    Returns:
        dict: Dictionnaire des motifs de préfixe détectés et leur fréquence
    """
    prefix_patterns = {}
    
    for issue in issues:
        if issue['type'] != 'broken_link':
            continue
        
        # Extraire le chemin du message d'erreur
        message = issue['message']
        link_match = re.search(r"'([^']+)'", message)
        if not link_match:
            continue
            
        path = link_match.group(1)
        
        # Détecter les préfixes communs
        parts = path.split('/')
        if len(parts) > 1:
            prefix = parts[0]
            if prefix not in prefix_patterns:
                prefix_patterns[prefix] = 0
            prefix_patterns[prefix] += 1
    
    return prefix_patterns

def suggest_prefix_replacements(prefix_patterns, project_path):
    """
    Suggère des remplacements pour les préfixes problématiques.
    
    Args:
        prefix_patterns (dict): Dictionnaire des motifs de préfixe et leur fréquence
        project_path (Path): Chemin de base du projet
        
    Returns:
        dict: Dictionnaire des suggestions de remplacement de préfixe
    """
    suggestions = {}
    
    # Vérifier les dossiers de premier niveau du projet
    root_dirs = [d.name for d in project_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    for prefix, count in prefix_patterns.items():
        if count < 3:  # Ignorer les préfixes peu fréquents
            continue
            
        # Chercher un dossier similaire
        best_match = None
        best_score = 0
        
        for dir_name in root_dirs:
            # Score simple basé sur les caractères communs
            score = SequenceMatcher(None, prefix, dir_name).ratio()
            if score > 0.5 and score > best_score:  # Seuil arbitraire de similarité
                best_match = dir_name
                best_score = score
        
        if best_match:
            suggestions[prefix] = best_match
    
    return suggestions

def replace_link_in_file(file_path, old_link, new_link):
    """
    Remplace un lien spécifique dans un fichier.
    
    Args:
        file_path (Path): Chemin du fichier
        old_link (str): Ancien lien à remplacer
        new_link (str): Nouveau lien
        
    Returns:
        bool: True si le remplacement a réussi, False sinon
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Normaliser les liens pour la recherche
        old_link_norm = old_link.replace('\\', '/').strip()
        new_link_norm = new_link.replace('\\', '/').strip()
        
        # Escape les caractères spéciaux pour la regex
        old_link_esc = re.escape(old_link_norm)
        
        # Remplacer dans les liens markdown
        md_pattern = r'\[([^\]]*)\]\(' + old_link_esc + r'(?:#[^)]+)?\)'
        content = re.sub(md_pattern, lambda m: f'[{m.group(1)}]({new_link_norm})', content)
        
        # Remplacer dans les liens wiki
        wiki_pattern = r'\[\[' + old_link_esc + r'(\|[^\]]+)?\]\]'
        
        def wiki_replacer(match):
            pipe_part = match.group(1) if match.group(1) else ''
            return f'[[{new_link_norm}{pipe_part}]]'
        
        content = re.sub(wiki_pattern, wiki_replacer, content)
        
        # Vérifier si des modifications ont été apportées
        # Utiliser une différence de longueur pour éviter les faux positifs
        # dus aux caractères spéciaux dans les regex
        original_len = len(content)
        new_content = content
        if new_content == content:
            logger.debug(f"Aucune modification apportée à {file_path}")
            return False
        
        # Sauvegarder les modifications
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        logger.info(f"Liens remplacés dans {file_path}: '{old_link}' → '{new_link}'")
        return True
    except Exception as e:
        logger.error(f"Erreur lors du remplacement de liens dans {file_path}: {e}")
        return False

def fix_prefix_in_group(project_path, issues, prefix, replacement):
    """
    Remplace un préfixe de chemin dans un groupe de liens cassés.
    
    Args:
        project_path (Path): Chemin de base du projet
        issues (list): Liste des problèmes de liens cassés
        prefix (str): Préfixe à remplacer
        replacement (str): Préfixe de remplacement
        
    Returns:
        int: Nombre de liens corrigés
    """
    fixed_count = 0
    processed_files = set()
    
    for issue in issues:
        # Extraire le chemin du fichier contenant le lien cassé
        file_path = project_path / issue['path']
        if str(file_path) in processed_files:
            continue
        
        # Extraire le lien cassé du message
        link_match = re.search(r"'([^']+)'", issue['message'])
        if not link_match:
            continue
            
        broken_link = link_match.group(1)
        
        # Vérifier si ce lien commence par le préfixe à remplacer
        if not broken_link.startswith(f"{prefix}/"):
            continue
        
        # Créer le nouveau lien avec le préfixe remplacé
        new_link = broken_link.replace(f"{prefix}/", f"{replacement}/", 1)
        
        try:
            # Remplacer le lien dans le fichier
            success = replace_link_in_file(file_path, broken_link, new_link)
            if success:
                fixed_count += 1
            
            processed_files.add(str(file_path))
        except Exception as e:
            logger.error(f"Erreur lors du remplacement des préfixes dans {file_path}: {e}")
    
    return fixed_count

def create_missing_file(project_path, broken_link, template_name=None):
    """
    Crée un fichier manquant à partir d'un template.
    
    Args:
        project_path (Path): Chemin de base du projet
        broken_link (str): Chemin du lien cassé
        template_name (str, optional): Nom du template à utiliser
        
    Returns:
        bool: True si le fichier a été créé, False sinon
    """
    from datetime import datetime
    
    # Normaliser le chemin
    normalized_path = broken_link.replace('\\', '/')
    if not normalized_path.endswith('.md'):
        normalized_path += '.md'
    
    target_path = project_path / normalized_path
    
    # Vérifier que le dossier parent existe
    parent_dir = target_path.parent
    if not parent_dir.exists():
        try:
            os.makedirs(parent_dir, exist_ok=True)
            logger.info(f"Dossier créé: {parent_dir}")
        except Exception as e:
            logger.error(f"Impossible de créer le dossier {parent_dir}: {e}")
            return False
    
    # Déterminer le template à utiliser
    template_content = ""
    if template_name:
        template_path = project_path / "templates" / f"{template_name}.md"
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                logger.debug(f"Template utilisé: {template_name}")
            except Exception as e:
                logger.warning(f"Erreur lors de la lecture du template {template_name}: {e}")
        else:
            logger.warning(f"Template {template_name} non trouvé, utilisation du template par défaut")
    
    if not template_content:
        # Template par défaut si aucun template spécifique n'est trouvé
        file_name = os.path.basename(normalized_path)
        title = os.path.splitext(file_name)[0].replace('-', ' ').title()
        
        # Déterminer un template approprié en fonction du chemin
        if '/personnages/' in normalized_path:
            template_content = f"""---
nom: {title}
tags: personnage
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {title}

## Caractéristiques
- **Rôle**: 
- **Apparence**: 
- **Traits de caractère**: 

## Contexte
- **Origine**: 
- **Motivation**: 
- **Relation avec les autres personnages**: 

## Arc narratif
<!-- Évolution du personnage au fil de l'histoire -->

## Notes
<!-- Notes et idées sur ce personnage -->
"""
        elif '/structure/' in normalized_path:
            template_content = f"""---
title: {title}
type: structure
created: {datetime.now().strftime('%Y-%m-%d')}
---

# {title}

## Aperçu
<!-- Description générale -->

## Éléments principaux
<!-- Liste des éléments clés -->
- 
- 
- 

## Relations avec d'autres éléments
<!-- Connexions avec d'autres parties de la structure -->

## Notes
<!-- Notes complémentaires et idées -->
"""
        else:
            # Template générique
            template_content = f"""---
title: {title}
created: {datetime.now().strftime('%Y-%m-%d')}
status: draft
---

# {title}

Ce document a été créé automatiquement pour corriger un lien cassé.

## Contenu à remplir

Remplacez ce texte par le contenu approprié.

"""
    
    # Écrire le fichier
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        logger.info(f"Fichier créé: {target_path}")
        return True
    except Exception as e:
        logger.error(f"Impossible de créer le fichier {target_path}: {e}")
        return False
