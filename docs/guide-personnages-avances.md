# Guide de gestion avancée des personnages avec Obsidian et Templater

Ce guide vous explique comment créer, gérer et exploiter efficacement les fiches de personnages avancées dans votre projet littéraire, en utilisant Obsidian et le plugin Templater.

## Table des matières

1. [Création du template personnage avancé](#1-création-du-template-personnage-avancé)
2. [Utilisation du template avec Templater](#2-utilisation-du-template-avec-templater)
3. [Référencement des personnages dans vos notes](#3-référencement-des-personnages-dans-vos-notes)
4. [Exploitation des métadonnées de personnage](#4-exploitation-des-métadonnées-de-personnage)
5. [Calculs automatiques basés sur les dates](#5-calculs-automatiques-basés-sur-les-dates)
6. [Intégration avec le reste du projet littéraire](#6-intégration-avec-le-reste-du-projet-littéraire)

## 1. Création du template personnage avancé

Commençons par créer un template personnage avancé qui combine les éléments essentiels recommandés dans le guide complet, tout en incluant des fonctionnalités avancées offertes par Templater.

Créez un fichier `personnage-avance.md` dans votre dossier `templates/`:

```markdown
---
nom: <% tp.system.prompt("Nom du personnage") %>
citation: <% tp.system.prompt("Citation caractéristique") %>
naissance: <% tp.system.prompt("Date de naissance (YYYY-MM-DD)", "1990-01-01") %>
---

# <% tp.frontmatter.nom %>

*"<% tp.frontmatter.citation %>"*

## Caractéristiques
- **Âge de base**: <% 
  // Calcul de l'âge de base à la date actuelle
  let dateNaissance = new Date(tp.frontmatter.naissance);
  let dateActuelle = new Date();
  let age = dateActuelle.getFullYear() - dateNaissance.getFullYear();
  
  // Ajustement si l'anniversaire n'est pas encore passé cette année
  let moisActuel = dateActuelle.getMonth();
  let moisNaissance = dateNaissance.getMonth();
  
  if (moisActuel < moisNaissance || (moisActuel === moisNaissance && dateActuelle.getDate() < dateNaissance.getDate())) {
    age--;
  }
  
  age + " ans";
%>
- **Date de naissance**: <% tp.frontmatter.naissance %>
- **Apparence**: <% tp.system.prompt("Description physique") %>
- **Traits de caractère**: <% tp.system.prompt("Principaux traits de caractère") %>

## Contexte
- **Origine**: <% tp.system.prompt("Origine géographique et sociale") %>
- **Famille**: <% tp.system.prompt("Situation familiale") %>
- **Occupation**: <% tp.system.prompt("Métier ou occupation") %>

## Arc narratif
- **Motivation**: <% tp.system.prompt("Motivation principale") %>
- **Conflit**: <% tp.system.prompt("Conflit central") %>
- **Évolution**: <% tp.system.prompt("Arc d'évolution") %>

## Apparitions
<!-- Les liens vers les chapitres où le personnage apparaît seront ajoutés ici -->

## Notes complémentaires
<% tp.system.prompt("Notes additionnelles (facultatif)", "") %>

<!-- Ne pas modifier cette section, elle est utilisée pour les calculs dynamiques -->
<% await tp.file.move("/structure/personnages/" + tp.frontmatter.nom.toLowerCase().replace(/\s+/g, "-")) %>
```

Ce template combine plusieurs éléments importants :

1. **Métadonnées YAML** au début du document pour stocker les informations clés (nom, citation, date de naissance)
2. **Prompts interactifs** pour guider la création
3. **Calcul automatique de l'âge** basé sur la date de naissance
4. **Structure de base** conforme aux recommandations du guide
5. **Déplacement automatique** du fichier dans le dossier approprié

## 2. Utilisation du template avec Templater

Pour utiliser ce template et créer une nouvelle fiche de personnage :

1. **Préparation** : Assurez-vous que Templater est correctement installé et configuré
   
   a. Dans Paramètres > Templater, définissez le dossier de templates à `templates/`
   
   b. Activez l'option "Trigger Templater on new file creation" si vous le souhaitez

2. **Création d'un nouveau personnage** :

   a. **Méthode 1 - Via la palette de commandes** :
      - Appuyez sur `Ctrl+P` (ou `Cmd+P` sur Mac) pour ouvrir la palette de commandes
      - Tapez "Templater: Open Insert Template modal"
      - Sélectionnez "personnage-avance.md"
      
   b. **Méthode 2 - Via un raccourci clavier** :
      - Si vous avez défini un raccourci dans les paramètres de Templater, utilisez-le
      - Sélectionnez "personnage-avance.md" dans la liste des templates

3. **Répondre aux prompts** :
   
   - Templater vous demandera successivement :
     - Le nom du personnage
     - Sa citation caractéristique
     - Sa date de naissance (au format YYYY-MM-DD)
     - Etc.

4. **Fichier généré** :
   
   Le template créera automatiquement un fichier dans `/structure/personnages/` avec le nom du personnage transformé en format compatible URL (minuscules, espaces remplacés par des tirets).

## 3. Référencement des personnages dans vos notes

Une fois la fiche du personnage créée, vous pouvez y faire référence dans vos autres notes de plusieurs façons :

### a. Référence simple

Utilisez la syntaxe standard d'Obsidian pour les liens internes :

```markdown
[[nom-du-personnage]]
```

Par exemple :
```markdown
Dans cette scène, [[jean-dupont]] découvre la vérité sur son passé.
```

### b. Référence avec texte alternatif

Pour une meilleure lisibilité de votre texte :

```markdown
[[nom-du-personnage|texte à afficher]]
```

Par exemple :
```markdown
[[jean-dupont|Jean]] se tourna vers la fenêtre, les mains tremblantes.
```

### c. Référence avec incorporation

Pour inclure directement certaines informations du personnage :

```markdown
![[nom-du-personnage#Section spécifique]]
```

Par exemple :
```markdown
Rappel des motivations du personnage :
![[jean-dupont#Arc narratif]]
```

## 4. Exploitation des métadonnées de personnage

Les métadonnées YAML au début de chaque fiche personnage permettent d'accéder facilement à des informations clés :

### a. Accès direct aux métadonnées (avec le plugin Dataview)

```markdown
La citation caractéristique de Jean est : `= this.citation` où "this" fait référence au personnage dont la fiche est ouverte.
```

### b. Création d'une galerie de citations

Avec le plugin Dataview, vous pouvez créer une note "citations.md" qui collecte automatiquement toutes les citations de vos personnages :

```markdown
# Citations des personnages

```dataview
TABLE nom as "Personnage", citation as "Citation"
FROM "structure/personnages"
WHERE citation
SORT nom ASC
```
```

### c. Référence directe à la citation d'un personnage

Avec Templater, vous pouvez créer un lien qui incorpore directement la citation :

```markdown
<% 
// Dans un nouveau template (par exemple citation-personnage.md)
let personnage = tp.system.prompt("Nom du personnage");
let fichierPersonnage = app.metadataCache.getFirstLinkpathDest(personnage, "");
let metadata = app.metadataCache.getFileCache(fichierPersonnage)?.frontmatter;
if (metadata && metadata.citation) {
  tR += `*"${metadata.citation}"* — [[${personnage}]]`;
} else {
  tR += `Citation introuvable pour [[${personnage}]]`;
}
%>
```

## 5. Calculs automatiques basés sur les dates

Voici comment calculer automatiquement l'âge d'un personnage à une date donnée dans votre récit :

### a. Template pour le calcul d'âge

Créez un template `calcul-age.md` :

```markdown
<% 
// Template pour calculer l'âge d'un personnage à une date spécifique
let personnage = tp.system.prompt("Nom du personnage");
let dateEvt = tp.system.prompt("Date de l'événement (YYYY-MM-DD)");

// Accès au fichier du personnage
let fichierPersonnage = app.metadataCache.getFirstLinkpathDest(personnage, "");
if (!fichierPersonnage) {
  tR += `Personnage [[${personnage}]] introuvable`;
  return;
}

// Récupération des métadonnées
let metadata = app.metadataCache.getFileCache(fichierPersonnage)?.frontmatter;
if (!metadata || !metadata.naissance) {
  tR += `Date de naissance non trouvée pour [[${personnage}]]`;
  return;
}

// Calcul de l'âge
let dateNaissance = new Date(metadata.naissance);
let dateEvenement = new Date(dateEvt);
let age = dateEvenement.getFullYear() - dateNaissance.getFullYear();

// Ajustement si l'anniversaire n'est pas encore passé
let moisEvt = dateEvenement.getMonth();
let moisNaissance = dateNaissance.getMonth();
if (moisEvt < moisNaissance || (moisEvt === moisNaissance && dateEvenement.getDate() < dateNaissance.getDate())) {
  age--;
}

tR += `À la date du ${dateEvt}, [[${personnage}]] avait ${age} ans.`;
%>
```

### b. Utilisation dans vos chapitres

Dans un chapitre ou une scène :

1. Placez le curseur où vous voulez insérer l'âge
2. Ouvrez la palette de commandes (Ctrl+P / Cmd+P)
3. Sélectionnez "Templater: Open Insert Template modal"
4. Choisissez "calcul-age.md"
5. Entrez le nom du personnage et la date de l'événement

### c. Création d'une ligne temporelle

Vous pouvez créer une note `chronologie.md` qui utilise Dataview pour générer automatiquement une chronologie avec l'âge des personnages à différentes dates :

```markdown
# Chronologie des événements

## Événements majeurs

| Date | Événement | Âges des personnages |
| ---- | --------- | -------------------- |
| 2020-06-15 | Découverte du manuscrit | <% tp.file.include("[[calcul-age]]", { personnage: "jean-dupont", dateEvt: "2020-06-15" }) %>, <% tp.file.include("[[calcul-age]]", { personnage: "marie-durand", dateEvt: "2020-06-15" }) %> |
| 2022-01-10 | Confrontation finale | <% tp.file.include("[[calcul-age]]", { personnage: "jean-dupont", dateEvt: "2022-01-10" }) %>, <% tp.file.include("[[calcul-age]]", { personnage: "marie-durand", dateEvt: "2022-01-10" }) %> |
```

## 6. Intégration avec le reste du projet littéraire

Pour intégrer ce système de gestion des personnages avec le reste de votre projet :

### a. Création de listes dynamiques de personnages

Dans vos notes de chapitre, vous pouvez automatiquement générer une liste des personnages présents :

```markdown
# Chapitre 3 : La Révélation

## Personnages présents
- [[jean-dupont]]
- [[marie-durand]]
- [[albert-schmidt]]

## Contenu
...
```

Puis dans votre note d'index, utilisez Dataview pour lister les chapitres où apparaît chaque personnage :

```markdown
# Apparitions des personnages

```dataview
TABLE WITHOUT ID file.link AS "Chapitre"
FROM "chapitres"
WHERE contains(file.content, "[[jean-dupont]]")
SORT file.name ASC
```
```

### b. Vue graphique des relations

La vue graphe d'Obsidian vous montrera automatiquement les connexions entre personnages et chapitres. Pour améliorer cette visualisation :

1. Ouvrez la vue graphe (icône dans la barre latérale)
2. Dans les paramètres du graphe, créez un groupe pour les fichiers du dossier "structure/personnages" avec une couleur distinctive
3. Créez un autre groupe pour les fichiers du dossier "chapitres"

Cette configuration visuelle vous permettra de voir immédiatement quels personnages sont les plus centraux dans votre récit.

### c. Préparation pour l'exportation

Pour garantir que votre système fonctionne bien lors de l'exportation vers d'autres formats, ajoutez ces lignes à votre script `compile_book.py` :

```python
def process_character_references(text):
    """Convertit les références aux personnages en format approprié pour l'exportation."""
    # Conversion des liens [[personnage]] en texte formaté
    pattern_links = r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]'
    
    def link_replacer(match):
        target = match.group(1)
        display = match.group(2) if match.group(2) else target
        # Pour HTML: return f'<span class="character-reference">{display}</span>'
        # Pour ePub/PDF: on garde simplement le texte d'affichage
        return display
    
    return re.sub(pattern_links, link_replacer, text)

# Puis dans la fonction de compilation:
output_content = process_character_references(output_content)
```

---

Ce guide vous donne les bases pour créer et gérer un système avancé de fiches de personnages dans Obsidian, en utilisant Templater pour automatiser les tâches répétitives et Dataview pour exploiter pleinement les métadonnées. Adaptez les templates et scripts à vos besoins spécifiques, et n'hésitez pas à explorer d'autres plugins qui pourraient enrichir encore votre workflow d'écriture.
