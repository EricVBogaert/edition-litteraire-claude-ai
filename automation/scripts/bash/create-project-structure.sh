#!/bin/bash
# Script pour créer l'arborescence du projet edition-litteraire-claude-ai
# Exécutez ce script dans le dossier où vous souhaitez créer la structure

# Définir le nom du dossier racine
ROOT_DIR="edition-litteraire-claude-ai"

# Créer le dossier racine s'il n'existe pas
mkdir -p $ROOT_DIR
cd $ROOT_DIR

# Créer les fichiers à la racine
touch README.md
touch CONTRIBUTING.md
touch LICENSE

# Créer la structure de dossiers et fichiers
mkdir -p docs
touch docs/guide-complet.md
touch docs/conceptes-cles.md
touch docs/faq.md
touch docs/glossaire.md
touch docs/ressources-externes.md

mkdir -p guides-demarrage
touch guides-demarrage/quick-start-windows.md
touch guides-demarrage/quick-start-mac.md
touch guides-demarrage/quick-start-linux.md
touch guides-demarrage/quick-start-linux-avance.md

mkdir -p templates/{roman,poesie,essai,documentation-technique}

mkdir -p exemples/{exemple-roman,exemple-poesie,exemple-essai}

mkdir -p outils/scripts/{python,bash,batch}
touch outils/scripts/python/compile.py
touch outils/scripts/python/extract_for_claude.py
touch outils/scripts/python/auto_typography.py
touch outils/scripts/bash/compile.sh
touch outils/scripts/bash/git-commands.sh
touch outils/scripts/batch/compile.bat
touch outils/scripts/batch/setup-env.bat

mkdir -p outils/plugins-obsidian/{obsidian-git-config,templates-litteraires}

mkdir -p outils/extensions-vscode/snippets
touch outils/extensions-vscode/settings.json

mkdir -p modules-avances/integration-grammalecte/src
touch modules-avances/integration-grammalecte/README.md
touch modules-avances/integration-grammalecte/setup.py

mkdir -p modules-avances/analyse-stylistique/src
touch modules-avances/analyse-stylistique/README.md

mkdir -p modules-avances/export-formats/{latex,indesign,web}

mkdir -p ressources/images
mkdir -p ressources/cheat-sheets
touch ressources/cheat-sheets/claude-ai-prompts.md
touch ressources/cheat-sheets/obsidian-shortcuts.md
touch ressources/cheat-sheets/git-commands.md
touch ressources/cheat-sheets/markdown-guide.md

mkdir -p ressources/bibliographie

# Rendre les scripts exécutables
chmod +x outils/scripts/bash/*.sh
chmod +x outils/scripts/batch/*.bat

echo "Structure du projet créée avec succès dans le dossier $ROOT_DIR"
echo "Vous pouvez maintenant commencer à remplir les fichiers avec du contenu"
