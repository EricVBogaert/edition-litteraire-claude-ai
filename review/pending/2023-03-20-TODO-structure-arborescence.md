---
id: TODO-STRCT
titre: Mise à jour de la structure d'arborescence du projet
statut: À faire
priorite: 1
date_creation: 2025-03-21
date_debut: 2025-03-22
date_fin: 2025-03-25
tags: tâche, structure
---

# Mise à jour de la structure d'arborescence du projet [TODO-STRCT]

**Statut**: À faire
**Priorité**: 1/5
**Période**: 2025-03-22 → 2025-03-25

## Description

Mettre à jour la structure d'arborescence du projet selon les recommandations du document `2025-03-20-structure-projet-revisee.md` pour améliorer l'organisation des fichiers et faciliter la gestion du contenu.

## Sous-tâches

- [ ] Créer le script d'initialisation pour les nouveaux dossiers (basé sur `setup_automation_structure.py`)
- [ ] Ajouter la création de nouveaux dossiers (personnages, lieux, concepts, références, styles)
- [ ] Définir le système de migration des fichiers existants vers la nouvelle structure
- [ ] Mettre à jour le document principal `guide-complet.md` pour refléter la nouvelle structure
- [ ] Tester le script sur un projet exemple pour vérifier la validité de la structure

## Intervenants assignés

- [[dev-principal]]
- [[architecte-contenu]]

## Ressources nécessaires

- Document de référence: `review/claude_suggestions/2025-03-20-structure-projet-revisee.md`
- Script existant: `setup_automation_structure.py`

## Notes

Cette tâche est fondamentale car elle affectera toutes les autres tâches du projet. Le script devra être suffisamment flexible pour permettre aux utilisateurs de choisir quels aspects de la structure ils souhaitent adopter. Une attention particulière doit être portée à la préservation des liens existants lors de la migration.
