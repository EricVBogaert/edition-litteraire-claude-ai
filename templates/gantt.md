---
titre: <% tp.system.prompt("Titre du diagramme de Gantt") %>
date_debut: <% tp.system.prompt("Date de début du projet (YYYY-MM-DD)", tp.date.now("YYYY-MM-DD")) %>
date_fin: <% tp.system.prompt("Date de fin du projet (YYYY-MM-DD)") %>
tags: gantt, planification
---

# <% tp.frontmatter.titre %>

**Période**: <% tp.frontmatter.date_debut %> → <% tp.frontmatter.date_fin %>

## Diagramme de Gantt

```mermaid
gantt
    title <% tp.frontmatter.titre %>
    dateFormat YYYY-MM-DD
    axisFormat %d/%m
    todayMarker on
    
    section Phase 1
    Tâche 1 :TODO-AAAAA, 2025-03-20, 3d
    Tâche 2 :TODO-BBBBB, after TODO-AAAAA, 5d
    
    section Phase 2
    Tâche 3 :TODO-CCCCC, after TODO-BBBBB, 4d
    Tâche 4 :TODO-DDDDD, 2025-03-26, 3d
```

## Liste des tâches

| ID | Tâche | Dates | Intervenants |
|---|---|---|---|
| TODO-AAAAA | Tâche 1 | 2025-03-20 → 2025-03-23 | [[nom-intervenant]] |
| TODO-BBBBB | Tâche 2 | 2025-03-23 → 2025-03-28 | [[nom-intervenant]] |
| TODO-CCCCC | Tâche 3 | 2025-03-28 → 2025-04-01 | [[nom-intervenant]] |
| TODO-DDDDD | Tâche 4 | 2025-03-26 → 2025-03-29 | [[nom-intervenant]] |

## Notes de planification

