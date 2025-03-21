# Comparaison des frameworks GUI basés sur le web pour Python

| Framework | Indice d'adoption (1-10) | Projets notables | Forces | Faiblesses | Maturité |
|-----------|--------------------------|-----------------|--------|------------|----------|
| pywebview | 7 | Wooey, Justpy, divers outils d'entreprise | Léger, utilise le moteur web natif, API Python <-> JS simple | Documentation parfois limitée, moins riche en fonctionnalités que Qt | Mature (v4.0+) |
| Eel | 6 | Anchorpoint, Streamlit (avant migration), diverses applications desktop | Très simple à utiliser, exposition directe des fonctions Python à JS | Moins flexible pour les applications complexes, moins actif récemment | Mature |
| CEF Python | 5 | BlenderCAM, MusicBrainz Picard, applications desktop complexes | Contrôle précis du moteur Chromium, capacités avancées | Complexe, plus lourd, courbe d'apprentissage importante | Très mature |
| Electron-Python | 4 | Graviton Editor, certaines applications fintech | Écosystème JavaScript riche, outils de développement avancés | Très lourd en ressources, complexité d'intégration | Mature |
| Tauri + Python | 3 | Projets en développement, tendance émergente | Extrêmement léger, sécurisé, performant | Écosystème jeune pour l'intégration avec Python, documentation limitée | Emergent |
| Tkinter WebView | 2 | Projets académiques, outils internes d'entreprise | Simple, standard dans Python, stable | Limitations fonctionnelles, aspect daté | Très mature |
| DearPyGui | 5 | Outils de visualisation scientifique, jeux indépendants | Performant, moderne sans dépendre du web | Écosystème plus limité, moins de widgets complexes | En développement actif |
| PyQt/PySide WebEngineView | 8 | Anki, Orange3, applications scientifiques/industrielles | Très complet, professionnel, stable | Lourd, licence commerciale pour certains usages, complexe | Très mature |

## Notes sur l'indice d'adoption

L'indice d'adoption (1-10) reflète:
- Le nombre de projets open-source utilisant la technologie
- L'activité de la communauté (GitHub stars, contributions)
- L'utilisation dans des projets commerciaux
- La tendance d'adoption sur les 2 dernières années
- La présence dans les discussions communautaires (Stack Overflow, forums Python)
