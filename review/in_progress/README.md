Dans l'architecture événementielle:

Les composants communiquent en émettant et en recevant des événements.

 Cela permet un découplage fort entre les différentes parties du système
 
 Car chaque composant peut fonctionner indépendamment et réagir aux événements sans connaître la source exacte de ces événements
 
 Cette approche est similaire au modèle de Windows 3.11, où les applications communiquaient via une boucle de message centrale, traitant des événements comme les clics de souris, les frappes au clavier, etc...

Le traitement de ces évènements peut être fait par plusieurs parties du systèmes:
Tel que un monitoring des *Token* utilise d'une API externe.
 Un monitoring du fonctionnement du traitement des évènements.
 Un syslog genre unix, avec des vue  vers un rsyslog
 Une interaction avec un API IA
Le traitement de RPC (RPCJson et ou REST API)

Directive:
FastAPI sera préféré a Flask. La combinaison pywebview + Flask + Webix devenant pywebview + FastAPI + Webix + UnifiedLLM(module a développer)
