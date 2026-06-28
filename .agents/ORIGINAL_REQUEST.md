# Original User Request

## 2026-06-17T14:32:46Z

Continuer le développement de l'application native Qt6 `gnu.in-cockpit`. L'objectif est d'implémenter l'authentification GitHub par PAT/App, d'étudier et d'intégrer des composants d'interface issus des autres projets du workspace (`gnu.in-gnosis-app`, `gnu.in-syster-app`), et de créer un script d'installation privé simple.

Working directory: ~/Projects/Gnu.in/gnu.in-cockpit
Integrity mode: development

## Requirements

### R1. Authentification GitHub Native (API Rest / PAT)
L'application doit utiliser l'API REST de GitHub via `PyGithub` ou `requests` avec un Personal Access Token (PAT) ou une authentification d'App, éliminant ainsi la dépendance au CLI `gh`.

### R2. Intégration de composants d'interface externes
Étudier les dépôts `gnu.in-gnosis-app` et `gnu.in-syster-app` dans le workspace, extraire des composants UI ou styles réutilisables, et les intégrer dans `gnu.in-cockpit` pour unifier le design.

### R3. Script d'installation local
Fournir un script d'installation simple (`install.sh`) dédié au déploiement privé de l'application sur le système, configurant automatiquement le `.desktop` et gérant les dépendances sans requérir `sudo` si possible (ex: `pipx` ou `pip install --user`).

## Acceptance Criteria

### Vérification de l'API GitHub
- [ ] L'agent a créé un script de test (ex: `tests/test_github_api.py`) prouvant que les appels à l'API GitHub (avec un faux PAT ou mock) fonctionnent sans utiliser `gh` dans un sous-processus.
- [ ] Le script de test s'exécute avec succès (exit code 0).

### Vérification de l'interface
- [ ] L'application se lance sans erreur (`python -m cockpit`).
- [ ] Le code source prouve qu'un composant ou style a été copié ou adapté depuis `gnu.in-gnosis-app` ou `gnu.in-syster-app`.

### Vérification de l'installation
- [ ] L'exécution de `install.sh` réussit avec le code de sortie 0.
- [ ] Le fichier `.desktop` est généré ou copié correctement au format standard.
