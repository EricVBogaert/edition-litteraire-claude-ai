---
id: TODO-<% Math.random().toString(36).substring(2, 7).toUpperCase() %>
titre: <% tp.system.prompt("Titre de la tâche") %>
statut: À faire
priorite: <% tp.system.prompt("Priorité (1-5, 1 étant la plus haute)", "3") %>
date_creation: <% tp.date.now("YYYY-MM-DD") %>
date_debut: <% tp.system.prompt("Date de début (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD")) %>
date_fin: <% tp.system.prompt("Date de fin prévue (YYYY-MM-DD)") %>
tags: tâche
---

# <% tp.frontmatter.titre %> [<% tp.frontmatter.id %>]

**Statut**: À faire
**Priorité**: <% tp.frontmatter.priorite %>/5
**Période**: <% tp.frontmatter.date_debut %> → <% tp.frontmatter.date_fin %>

## Description

<% tp.system.prompt("Description brève de la tâche") %>

## Sous-tâches

- [ ] 
- [ ] 
- [ ] 

## Intervenants assignés

- [[]]
- [[]]

## Ressources nécessaires

- 
- 

## Notes

