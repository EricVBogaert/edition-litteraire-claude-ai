---
id: TODO-REVW
titre: Intégration du système de révision avec Claude
statut: À faire
priorite: 2
date_creation: 2025-03-21
date_debut: 2025-03-26
date_fin: 2025-03-30
tags: tâche, révision, claude
---

# Intégration du système de révision avec Claude [TODO-REVW]

**Statut**: À faire
**Priorité**: 2/5
**Période**: 2025-03-26 → 2025-03-30

## Description

Mettre en place un système de révision collaborative utilisant le dossier `review/` existant, intégrant les suggestions de Claude et facilitant leur incorporation dans le projet.

## Sous-tâches

- [ ] Créer un template simple pour les demandes de révision
- [ ] Développer un script minimal pour soumettre du contenu à Claude (`claude_api.py`)
- [ ] Mettre en place le système de gestion des états des révisions (pending, in_progress, completed)
- [ ] Créer une documentation utilisateur pour le workflow de révision
- [ ] Développer un exemple d'intégration GitHub Actions (optionnel)

## Intervenants assignés

- [[dev-principal]]
- [[redacteur-principal]]

## Ressources nécessaires

- Document de référence: `review/claude_suggestions/2025-03-20-structure-scripts-automation-001.md`
- Dossier existant: `review/`
- Template pour les demandes: format décrit dans le document de référence

## Notes

Le système doit fonctionner aussi bien en local (sans GitHub Actions) qu'avec GitHub pour les utilisateurs plus avancés. Les templates doivent être minimalistes mais contenir les métadonnées essentielles pour le suivi. Le script `claude_api.py` doit gérer correctement les clés API de manière sécurisée.
