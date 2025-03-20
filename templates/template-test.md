---
nom: <% tp.system.prompt("Nom de l'intervenant") %>
role: <% tp.system.prompt("Rôle principal (Auteur, Développeur, Analyste, Relecteur, etc.)") %>
id: <% tp.file.title.toLowerCase().replace(/\s+/g, "-") %>
expertise: <% tp.system.prompt("Domaines d'expertise séparés par des virgules") %>
disponibilite: <% tp.system.prompt("Disponibilité (heures/semaine ou période spécifique)") %>
contact: <% tp.system.prompt("Email ou autre moyen de contact") %>
date_creation: <% tp.date.now("YYYY-MM-DD") %>
tags: intervenant, <% tp.system.prompt("Rôle principal").toLowerCase() %>, <% tp.system.prompt("Tags additionnels séparés par des virgules (optionnel)", "") %>
---

# <% tp.frontmatter.nom %>

## Profil

**Rôle**: <% tp.frontmatter.role %>
**Expertise**: <% tp.frontmatter.expertise %>
**Disponibilité**: <% tp.frontmatter.disponibilite %>
**Contact**: <% tp.frontmatter.contact %>

## Compétences spécifiques

### Compétences techniques
- <% tp.system.prompt("Compétence technique 1") %>
- <% tp.system.prompt("Compétence technique 2") %>
- <% tp.system.prompt("Compétence technique 3 (optionnel)", "") %>

### Compétences éditoriales
- <% tp.system.prompt("Compétence éditoriale 1") %>
- <% tp.system.prompt("Compétence éditoriale 2") %>
- <% tp.system.prompt("Compétence éditoriale 3 (optionnel)", "") %>

### Outils maîtrisés
- <% tp.system.prompt("Outil 1") %>
- <% tp.system.prompt("Outil 2") %>
- <% tp.system.prompt("Outil 3 (optionnel)", "") %>

## Tâches assignées

```dataview
TABLE statut, date_debut, date_fin, priorite
FROM #tâche
WHERE contains(intervenants, "<% tp.frontmatter.id %>")
SORT priorite ASC, date_debut ASC
```

## Historique des contributions

```dataview
TABLE date_completion as "Date", type as "Type"
FROM #contribution 
WHERE contains(contributeurs, "<% tp.frontmatter.nom %>")
SORT date_completion DESC
```

## Notes additionnelles
<% tp.system.prompt("Notes supplémentaires sur cet intervenant (optionnel)", "") %>


