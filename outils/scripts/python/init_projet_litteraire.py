#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script d'initialisation de projet littéraire
Ce script crée l'arborescence d'un projet littéraire et importe un document existant,
en le segmentant éventuellement en chapitres.
"""

import os
import re
import argparse
import shutil
from datetime import datetime
from pathlib import Path


def create_directory_structure(root_dir):
    """Crée la structure de répertoires pour le projet littéraire."""
    directories = [
        "",  # Root directory
        "structure",
        "chapitres",
        "ressources",
        "media",
        "templates",
        "claude-sessions",
        "scripts", 
        "export"
    ]
    
    print(f"Création de l'arborescence dans {root_dir}...")
    
    for directory in directories:
        path = os.path.join(root_dir, directory)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"✓ Répertoire créé: {path}")
        else:
            print(f"! Répertoire existant: {path}")


def create_index_file(root_dir, title, author):
    """Crée le fichier index.md à la racine du projet."""
    index_path = os.path.join(root_dir, "index.md")
    
    if os.path.exists(index_path):
        print(f"! Fichier index.md existant: {index_path}")
        overwrite = input("Voulez-vous l'écraser? (o/n): ")
        if overwrite.lower() != 'o':
            return
    
    now = datetime.now().strftime("%d %B %Y")
    
    content = f"""# {title}

## Métadonnées
- Titre: {title}
- Auteur: {author}
- Genre: [Genre littéraire]
- Statut: #en-cours

## Structure
- [Plan général](structure/plan-general.md)
- [Personnages](structure/personnages.md)
- [Univers](structure/univers.md)

## Chapitres
<!-- Les liens vers les chapitres seront générés automatiquement -->

## Notes
- Projet initialisé le {now}

"""
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✓ Fichier index.md créé: {index_path}")


def create_template_files(root_dir):
    """Crée des fichiers de templates pour les personnages, les lieux, etc."""
    templates = {
        "personnage.md": """# {{nom}}

## Caractéristiques
- Âge:
- Apparence:
- Traits de caractère:

## Contexte
- Origine:
- Famille:
- Occupation:

## Arc narratif
- Motivation:
- Conflit:
- Évolution:

## Apparitions
<!-- Liens vers les chapitres où le personnage apparaît -->

## Notes
""",
        "chapitre.md": """# {{titre}}

## Synopsis
<!-- Brève description du chapitre -->

## Scènes
<!-- Liste des scènes ou sections -->

## Personnages présents
<!-- Personnages apparaissant dans ce chapitre -->

## Notes
<!-- Notes et idées pour ce chapitre -->
""",
        "scene.md": """# {{titre}}

## Lieu
<!-- Où se déroule la scène -->

## Moment
<!-- Quand se déroule la scène -->

## Personnages présents
<!-- Personnages apparaissant dans cette scène -->

## Objectif narratif
<!-- Rôle de cette scène dans l'histoire -->

## Contenu
<!-- Le contenu de la scène -->
"""
    }
    
    templates_dir = os.path.join(root_dir, "templates")
    
    for filename, content in templates.items():
        file_path = os.path.join(templates_dir, filename)
        
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Template créé: {file_path}")
        else:
            print(f"! Template existant: {file_path}")


def create_structure_files(root_dir):
    """Crée les fichiers de base pour la structure du projet."""
    structure_files = {
        "plan-general.md": """# Plan Général

## Introduction
<!-- Présentation générale de l'œuvre -->

## Premières idées
<!-- Idées initiales à développer -->

## Structure narrative
<!-- Description de la structure globale -->

## Arcs narratifs
<!-- Description des principaux arcs narratifs -->

## Notes et idées
<!-- Notes et idées diverses -->
""",
        "personnages.md": """# Personnages

## Personnages principaux
<!-- Liste des personnages principaux avec liens vers leurs fiches -->

## Personnages secondaires
<!-- Liste des personnages secondaires avec liens vers leurs fiches -->

## Relations entre personnages
<!-- Description des relations importantes entre personnages -->

## Notes et idées
<!-- Notes et idées sur les personnages -->
""",
        "univers.md": """# Univers

## Cadre général
<!-- Description du cadre général de l'histoire -->

## Lieux importants
<!-- Liste des lieux importants avec liens vers leurs fiches -->

## Règles et particularités
<!-- Règles spécifiques de l'univers (si applicable) -->

## Chronologie
<!-- Chronologie générale si pertinent -->

## Notes et idées
<!-- Notes et idées sur l'univers -->
"""
    }
    
    structure_dir = os.path.join(root_dir, "structure")
    
    for filename, content in structure_files.items():
        file_path = os.path.join(structure_dir, filename)
        
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Fichier structure créé: {file_path}")
        else:
            print(f"! Fichier structure existant: {file_path}")


def detect_chapters(text):
    """
    Détecte automatiquement les chapitres dans le texte.
    Retourne une liste de tuples (titre_chapitre, contenu_chapitre).
    """
    # Différents motifs pour détecter les chapitres
    patterns = [
        r"^#\s+(.*?)$(.*?)(?=^#\s+|\Z)",  # Format Markdown: # Titre
        r"^##\s+(.*?)$(.*?)(?=^##\s+|\Z)",  # Format Markdown: ## Titre
        r"^Chapitre\s+(\d+|[IVXLCDM]+)(?:\s*:\s*(.*?))?$(.*?)(?=^Chapitre\s+|\Z)",  # Chapitre X: Titre
        r"^CHAPITRE\s+(\d+|[IVXLCDM]+)(?:\s*:\s*(.*?))?$(.*?)(?=^CHAPITRE\s+|\Z)",  # CHAPITRE X: Titre
    ]
    
    # Essayer chaque pattern
    for pattern in patterns:
        chapters = []
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            if len(match.groups()) == 2:  # Format: # Titre + Contenu
                title = match.group(1).strip()
                content = match.group(2).strip()
                chapters.append((title, content))
            elif len(match.groups()) == 3:  # Format: Chapitre X: Titre + Contenu
                chapter_num = match.group(1).strip()
                title = match.group(2).strip() if match.group(2) else f"Chapitre {chapter_num}"
                content = match.group(3).strip()
                chapters.append((title, content))
        
        if chapters:
            return chapters
    
    # Si aucun chapitre détecté, retourner le texte entier comme un seul chapitre
    return [("Document complet", text)]


def import_document(root_dir, document_path, title, author, split_chapters=True):
    """
    Importe un document existant et le segmente éventuellement en chapitres.
    """
    if not os.path.exists(document_path):
        print(f"Erreur: Le document {document_path} n'existe pas.")
        return
    
    print(f"Importation du document: {document_path}")
    
    # Lecture du document
    with open(document_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Créer une copie du document original dans le répertoire ressources
    doc_filename = os.path.basename(document_path)
    doc_copy_path = os.path.join(root_dir, "ressources", "original_" + doc_filename)
    shutil.copy2(document_path, doc_copy_path)
    print(f"✓ Copie du document original créée: {doc_copy_path}")
    
    # Si split_chapters est vrai, détecter et créer des fichiers séparés par chapitre
    chapters_dir = os.path.join(root_dir, "chapitres")
    chapter_links = []
    
    if split_chapters:
        chapters = detect_chapters(content)
        
        if len(chapters) > 1:
            print(f"Détection de {len(chapters)} chapitres...")
            
            for i, (title, chapter_content) in enumerate(chapters, 1):
                # Nettoyer le titre pour le nom de fichier
                clean_title = re.sub(r'[\\/*?:"<>|]', "", title).strip()
                clean_title = re.sub(r'\s+', "-", clean_title).lower()
                
                # Formatage du numéro de chapitre avec zéros de tête
                chapter_num = f"{i:02d}"
                
                # Créer le nom de fichier
                chapter_filename = f"chapitre-{chapter_num}-{clean_title[:30]}.md"
                chapter_path = os.path.join(chapters_dir, chapter_filename)
                
                # Formater le contenu du chapitre
                chapter_md_content = f"""# {title}

{chapter_content}
"""
                
                # Écrire le fichier de chapitre
                with open(chapter_path, "w", encoding="utf-8") as f:
                    f.write(chapter_md_content)
                
                print(f"✓ Chapitre créé: {chapter_path}")
                
                # Ajouter le lien au chapitre pour l'index
                chapter_links.append(f"- [Chapitre {chapter_num}: {title}](chapitres/{chapter_filename})")
        else:
            print("Aucune structure de chapitres détectée. Création d'un fichier unique.")
            
            # Créer un seul fichier
            chapter_path = os.path.join(chapters_dir, "document-complet.md")
            with open(chapter_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"✓ Document unique créé: {chapter_path}")
            chapter_links.append("- [Document complet](chapitres/document-complet.md)")
    else:
        # Créer un seul fichier sans segmentation
        chapter_path = os.path.join(chapters_dir, "document-complet.md")
        with open(chapter_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"✓ Document unique créé: {chapter_path}")
        chapter_links.append("- [Document complet](chapitres/document-complet.md)")
    
    # Mettre à jour l'index avec les liens vers les chapitres
    index_path = os.path.join(root_dir, "index.md")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
        
        # Remplacer la section des chapitres
        chapter_section_pattern = r"## Chapitres\n.*?(?=\n## |$)"
        chapter_section_replacement = f"## Chapitres\n" + "\n".join(chapter_links)
        
        if re.search(chapter_section_pattern, index_content, re.DOTALL):
            new_index_content = re.sub(
                chapter_section_pattern,
                chapter_section_replacement,
                index_content,
                flags=re.DOTALL
            )
        else:
            new_index_content = index_content
        
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_index_content)
        
        print(f"✓ Index mis à jour avec les liens vers les chapitres")


def create_simple_scripts(root_dir):
    """Crée des scripts utilitaires de base."""
    scripts_dir = os.path.join(root_dir, "scripts")
    
    scripts = {
        "compile_book.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Compile tous les chapitres en un seul document
\"\"\"

import os
import re
import argparse
from pathlib import Path

def get_chapter_files(chapters_dir):
    \"\"\"Récupère tous les fichiers de chapitres triés par numéro.\"\"\"
    chapter_files = []
    
    for file in os.listdir(chapters_dir):
        if file.endswith(".md") and file.startswith("chapitre-"):
            chapter_files.append(file)
    
    # Trier les fichiers par numéro de chapitre
    chapter_files.sort(key=lambda x: int(re.search(r'chapitre-(\d+)', x).group(1)))
    return chapter_files

def compile_book(project_dir, output_file="export/livre_complet.md"):
    \"\"\"Compile tous les chapitres en un seul document.\"\"\"
    project_dir = Path(project_dir)
    chapters_dir = project_dir / "chapitres"
    output_path = project_dir / output_file
    
    # Créer le répertoire de sortie si nécessaire
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Lire le fichier index pour les métadonnées
    index_path = project_dir / "index.md"
    title = "Livre"
    author = "Auteur"
    
    if index_path.exists():
        with open(index_path, "r", encoding="utf-8") as f:
            index_content = f.read()
            
            # Extraire le titre et l'auteur
            title_match = re.search(r'^# (.+)$', index_content, re.MULTILINE)
            if title_match:
                title = title_match.group(1)
            
            author_match = re.search(r'- Auteur: (.+)$', index_content, re.MULTILINE)
            if author_match:
                author = author_match.group(1)
    
    # Commencer le fichier compilé avec les métadonnées
    output_content = f\"\"\"---
title: {title}
author: {author}
date: {os.popen('date +"%d %B %Y"').read().strip()}
---

\"\"\"
    
    # Récupérer tous les fichiers de chapitres
    chapter_files = get_chapter_files(chapters_dir)
    
    if not chapter_files:
        # S'il n'y a pas de fichiers chapitre-XX, vérifier s'il y a un document complet
        if os.path.exists(chapters_dir / "document-complet.md"):
            with open(chapters_dir / "document-complet.md", "r", encoding="utf-8") as f:
                output_content += f.read()
    else:
        # Compiler tous les chapitres
        for chapter_file in chapter_files:
            with open(chapters_dir / chapter_file, "r", encoding="utf-8") as f:
                chapter_content = f.read()
                
                # Ajouter un saut de page avant chaque chapitre (pour la génération PDF)
                if chapter_file != chapter_files[0]:
                    output_content += "\\pagebreak\n\n"
                
                # Ajouter le contenu du chapitre
                output_content += chapter_content + "\n\n"
    
    # Écrire le fichier de sortie
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_content)
    
    print(f"Livre compilé avec succès: {output_path}")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile tous les chapitres en un seul document.")
    parser.add_argument("project_dir", default=".", nargs="?", help="Répertoire du projet (par défaut: répertoire courant)")
    parser.add_argument("-o", "--output", default="export/livre_complet.md", help="Chemin du fichier de sortie (par défaut: export/livre_complet.md)")
    
    args = parser.parse_args()
    
    output_path = compile_book(args.project_dir, args.output)
    print(f"Pour générer un PDF: pandoc -s {output_path} -o {str(output_path).replace('.md', '.pdf')} --pdf-engine=xelatex")
    print(f"Pour générer un EPUB: pandoc -s {output_path} -o {str(output_path).replace('.md', '.epub')} --epub-cover-image=media/cover.jpg")
""",

        "extract_for_claude.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Extrait une section pour révision avec Claude
\"\"\"

import os
import re
import argparse
import datetime

def extract_section(file_path, section_name=None, line_start=None, line_end=None):
    \"\"\"
    Extrait une section d'un fichier Markdown.
    Peut extraire par nom de section ou par plage de lignes.
    \"\"\"
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return None
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        lines = content.split("\\n")
    
    # Si une plage de lignes est spécifiée
    if line_start is not None and line_end is not None:
        line_start = int(line_start)
        line_end = int(line_end)
        
        if line_start < 1:
            line_start = 1
        if line_end > len(lines):
            line_end = len(lines)
        
        extracted_content = "\\n".join(lines[line_start-1:line_end])
        section_info = f"lignes {line_start}-{line_end} de {file_path}"
    
    # Sinon, si un nom de section est spécifié
    elif section_name:
        # Rechercher la section
        section_pattern = rf"^#+\s+{re.escape(section_name)}$"
        section_matches = [i for i, line in enumerate(lines) if re.match(section_pattern, line, re.IGNORECASE)]
        
        if not section_matches:
            print(f"Erreur: Section '{section_name}' non trouvée dans {file_path}.")
            return None
        
        section_start = section_matches[0]
        
        # Trouver où se termine la section (au prochain titre de même niveau ou à la fin)
        current_level = len(re.match(r'^(#+)', lines[section_start]).group(1))
        section_end = len(lines)
        
        for i in range(section_start + 1, len(lines)):
            header_match = re.match(r'^(#+)', lines[i])
            if header_match and len(header_match.group(1)) <= current_level:
                section_end = i
                break
        
        extracted_content = "\\n".join(lines[section_start:section_end])
        section_info = f"section '{section_name}' de {file_path}"
    
    # Si aucune option n'est spécifiée, prendre tout le contenu
    else:
        extracted_content = content
        section_info = f"contenu complet de {file_path}"
    
    # Créer un dossier pour les extractions
    claude_sessions_dir = os.path.dirname(os.path.abspath(file_path))
    if "chapitres" in claude_sessions_dir:
        # Remonter à la racine du projet
        project_root = os.path.dirname(os.path.dirname(claude_sessions_dir))
        claude_sessions_dir = os.path.join(project_root, "claude-sessions")
    else:
        claude_sessions_dir = os.path.join(os.path.dirname(os.path.abspath(file_path)), "claude-sessions")
    
    os.makedirs(claude_sessions_dir, exist_ok=True)
    
    # Créer un fichier contenant l'extraction et les instructions pour Claude
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"extraction-{os.path.basename(file_path).replace('.md', '')}-{timestamp}.md"
    output_path = os.path.join(claude_sessions_dir, filename)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f\"\"\"# Extraction pour Claude

## Instructions
Ce document contient {section_info}.
Voici les objectifs de révision:
- [Ajoutez vos objectifs de révision ici]
- 
- 

## Contenu à réviser

{extracted_content}

## Notes supplémentaires
[Ajoutez toute information contextuelle importante ici]

\"\"\")
    
    print(f"✓ Extraction créée: {output_path}")
    print("Modifiez ce fichier pour ajouter vos instructions spécifiques, puis importez-le dans Claude.")
    return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrait une section d'un fichier Markdown pour révision avec Claude.")
    parser.add_argument("file_path", help="Chemin du fichier à extraire")
    parser.add_argument("-s", "--section", help="Nom de la section à extraire")
    parser.add_argument("-l", "--lines", help="Plage de lignes à extraire (format: début-fin)")
    
    args = parser.parse_args()
    
    line_start = None
    line_end = None
    
    if args.lines:
        line_range = args.lines.split("-")
        if len(line_range) == 2:
            line_start = int(line_range[0])
            line_end = int(line_range[1])
    
    extract_section(args.file_path, args.section, line_start, line_end)
""",

        "fix_typography.py": """#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Corrige la typographie française dans un fichier Markdown
\"\"\"

import os
import re
import argparse

def fix_french_typography(text):
    \"\"\"Corrige la typographie française dans un texte.\"\"\"
    # Liste des transformations à appliquer
    transformations = [
        # Espaces insécables avant les signes doubles
        (r'(?<!\s)(:)', r' \1'),  # Avant les deux-points
        (r'(?<!\s)(;)', r' \1'),  # Avant le point-virgule
        (r'(?<!\s)(!)', r' \1'),  # Avant le point d'exclamation
        (r'(?<!\s)(\?)', r' \1'),  # Avant le point d'interrogation
        
        # Guillemets français
        (r'"([^"]*)"', r'« \1 »'),  # Guillemets français avec espaces insécables
        
        # Tirets pour les dialogues
        (r'^- ', r'— '),  # Tiret cadratin pour les dialogues
        
        # Correction des points de suspension
        (r'\.\.\.', r'…'),  # Remplacer trois points par le caractère points de suspension
        
        # Espaces insécables dans les nombres
        (r'(\d{1,3}) (\d{3})', r'\1 \2'),  # Espace insécable pour les milliers
    ]
    
    # Appliquer toutes les transformations
    for pattern, replacement in transformations:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    
    return text

def fix_file_typography(file_path, output_path=None, backup=True):
    \"\"\"Corrige la typographie française dans un fichier.\"\"\"
    if not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return
    
    # Lire le contenu du fichier
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Corriger la typographie
    corrected_content = fix_french_typography(content)
    
    # Créer une sauvegarde si demandé
    if backup:
        backup_path = f"{file_path}.bak"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Sauvegarde créée: {backup_path}")
    
    # Écrire le contenu corrigé
    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(corrected_content)
        print(f"✓ Fichier corrigé écrit: {output_path}")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(corrected_content)
        print(f"✓ Fichier corrigé: {file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corrige la typographie française dans un fichier Markdown.")
    parser.add_argument("file_path", help="Chemin du fichier à corriger")
    parser.add_argument("-o", "--output", help="Chemin du fichier de sortie (par défaut: remplace le fichier d'origine)")
    parser.add_argument("--no-backup", action="store_true", help="Ne pas créer de sauvegarde du fichier original")
    
    args = parser.parse_args()
    
    fix_file_typography(args.file_path, args.output, not args.no_backup)
"""
    }
    
    for filename, content in scripts.items():
        file_path = os.path.join(scripts_dir, filename)
        
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Rendre le script exécutable sur Unix
            if os.name != 'nt':  # Si pas Windows
                os.chmod(file_path, 0o755)
            
            print(f"✓ Script créé: {file_path}")
        else:
            print(f"! Script existant: {file_path}")


def main():
    parser = argparse.ArgumentParser(description="Initialise un projet littéraire et importe un document existant.")
    parser.add_argument("--root-dir", "-d", default=".", help="Répertoire racine du projet (par défaut: répertoire courant)")
    parser.add_argument("--document", "-f", help="Chemin du document à importer")
    parser.add_argument("--title", "-t", default="Mon Projet Littéraire", help="Titre du projet")
    parser.add_argument("--author", "-a", default="Auteur", help="Nom de l'auteur")
    parser.add_argument("--no-split", action="store_true", help="Ne pas diviser le document en chapitres")
    
    args = parser.parse_args()
    
    # Création de la structure de répertoires
    create_directory_structure(args.root_dir)
    
    # Création du fichier index
    create_index_file(args.root_dir, args.title, args.author)
    
    # Création des fichiers de templates
    create_template_files(args.root_dir)
    
    # Création des fichiers de structure
    create_structure_files(args.root_dir)
    
    # Création des scripts utilitaires
    create_simple_scripts(args.root_dir)
    
    # Importation du document s'il est spécifié
    if args.document:
        import_document(args.root_dir, args.document, args.title, args.author, not args.no_split)
    
    print("\n✓ Initialisation du projet terminée !")
    print


if __name__ == "__main__":
    main()
