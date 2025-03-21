en cours de propositions
# Création d'une bibliothèque Python pour utiliser Claude et LMStudio de façon transparente

Pour créer une bibliothèque Python qui permet d'utiliser de façon transparente à la fois l'API Claude d'Anthropic et LMStudio, ainsi que d'autre API IA potentiel

## Principes de conception

La bibliothèque **UnifiedLLM** que j'ai créée s'appuie sur les principes suivants :

1. **Interface unifiée** : Une seule interface pour interagir avec les deux systèmes
2. **Détection automatique** : Utilisation du fournisseur disponible si un seul est installé
3. **Conversion transparente** : Conversion automatique des messages et paramètres entre formats
4. **Flexibilité** : Possibilité de basculer entre fournisseurs à tout moment
5. **Dépendances optionnelles** : Les packages `anthropic` et `lmstudio` sont des dépendances optionnelles