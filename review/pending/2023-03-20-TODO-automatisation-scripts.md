---
id: TODO-AUTO
titre: Développement du système d'automatisation
statut: À faire
priorite: 1
date_creation: 2025-03-21
date_debut: 2025-03-22
date_fin: 2025-03-29
tags: tâche, automatisation, scripts
---

# Développement du système d'automatisation [TODO-AUTO]

**Statut**: À faire
**Priorité**: 1/5
**Période**: 2025-03-22 → 2025-03-29

## Description

Mettre en place le système d'automatisation proposé dans `2025-03-20-structure-scripts-automation-001.md` pour faciliter les workflows d'édition, de compilation et d'intégration avec Claude, en suivant une approche minimaliste mais fonctionnelle.

## Sous-tâches

- [ ] Finaliser le script `setup_automation_structure.py` pour initialiser la structure d'automatisation
- [ ] Développer le script `compile.py` pour l'assemblage des chapitres en différents formats
- [ ] Créer le script `extract_for_claude.py` pour faciliter la soumission de contenu à Claude
- [ ] Développer un script Bash minimal `git_workflow.sh` pour les opérations Git courantes
- [ ] Mettre en place les fichiers de configuration nécessaires (paths.json, etc.)
- [ ] Créer une documentation simple pour l'utilisation des scripts

## Intervenants assignés

- [[dev-principal]]
- [[specialiste-integration]]

## Ressources nécessaires

- Document de référence: `review/claude_suggestions/2025-03-20-structure-scripts-automation-001.md`
- Script initial: `setup_automation_structure.py`

## Notes

L'approche doit rester minimaliste et robuste. Chaque script doit fonctionner de manière indépendante et être bien documenté. Privilégier des scripts autonomes plutôt qu'un système complexe intégré. Les utilisateurs doivent pouvoir choisir quels scripts ils souhaitent utiliser sans être obligés d'adopter l'ensemble du système.
