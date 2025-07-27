# Lim Terminal - Communication Série & Visualisation de Données

**README en :** [English](../README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Aperçu

Lim Terminal est une application conviviale pour la communication série et la visualisation de données en temps réel. Connectez-vous à Arduino ou d'autres appareils série, collectez des données et créez des graphiques dynamiques avec des fonctionnalités de visualisation professionnelles. Disponible en 5 langues avec sauvegarde automatique des préférences.

![Lim Terminal Screenshot](shot.png)

![Lim Terminal Screenshot](shot_stacked.png)

## Fonctionnalités

### 🌍 **Langues Multiples**
- Disponible en anglais, portugais, espagnol, allemand et français
- Changement de langue depuis le menu (redémarrage requis)
- Tous les paramètres conservés lors du changement de langue

### 📡 **Connexion Série Facile**
- Connexion aux appareils série réels (Arduino, capteurs, etc.)
- Mode simulation intégré pour tester sans matériel
- Détection automatique des ports avec actualisation en un clic
- Compatibilité complète avec les débits de l'IDE Arduino (300-2000000 bps)

### 📊 **Visualisation de Données Professionnelle**
- **Graphiques de Séries Temporelles** : Tracez jusqu'à 5 colonnes de données simultanément
- **Graphiques en Aires Empilées** : Comparez les données en valeurs absolues ou en pourcentages
- **Apparence Personnalisable** : Choisissez les couleurs, marqueurs et types de lignes pour chaque série de données
- **Mises à Jour en Temps Réel** : Taux de rafraîchissement configurables (1-30 FPS)
- **Export** : Sauvegardez les graphiques en images PNG haute qualité
- **Contrôles Interactifs** : Pausez/reprenez la collecte de données, zoomez et déplacez-vous

### 💾 **Gestion de Données Intelligente**
- **Sauvegarde/Chargement Manuel** : Exportez et importez vos données à tout moment
- **Sauvegarde Automatique** : Sauvegarde automatique optionnelle avec noms de fichiers horodatés
- **Sécurité des Données** : Effacez les données avec invites de confirmation
- **Tous les Paramètres Sauvegardés** : Les préférences sont automatiquement conservées entre les sessions

## Premiers Pas

### Prérequis
- Python 3.8 ou plus récent
- Connexion Internet pour l'installation des dépendances

### Installation

#### Méthode 1 : Installation Directe (Recommandée)
```bash
# Installer directement depuis GitHub
pip install git+https://github.com/CBPF-LIM/lim_term.git

# Exécuter l'application
limterm
```

#### Méthode 2 : Installation pour Développement
```bash
# Cloner le dépôt
git clone https://github.com/CBPF-LIM/lim_term.git
cd lim_term

# Installer avec Poetry (recommandé pour le développement)
pip install poetry
poetry install
poetry run limterm
```

### Exécutable Windows

Pour les utilisateurs Windows qui préfèrent ne pas installer Python :

1. **Téléchargement** : Obtenez le dernier `LimTerm.exe` depuis [GitHub Releases](https://github.com/CBPF-LIM/lim_term/releases)
2. **Exécution** : Double-cliquez sur l'exécutable - aucune installation requise
3. **Paramètres** : L'application crée un dossier `lim_config` pour vos préférences

**Configuration Système Requise :**
- Windows 10/11 (64-bit)
- Aucune installation Python nécessaire
- ~50-100 MB d'espace disque

### Premiers Pas
1. **Langue** : Choisissez votre langue dans le menu Langue
2. **Connexion** : Allez à l'onglet Configuration, sélectionnez votre port série et débit
3. **Données** : Passez à l'onglet Données pour voir les données entrantes
4. **Visualisation** : Utilisez l'onglet Graphique pour créer des graphiques à partir de vos données

## Utilisation

### Onglet Configuration
- **Mode** : Choisissez "Hardware" pour les appareils réels, "Simulated" pour les tests
- **Port** : Sélectionnez votre port série (cliquez sur Actualiser pour mettre à jour la liste)
- **Débit** : Définissez la vitesse de communication (correspondant aux paramètres de votre appareil)
- **Connecter** : Cliquez pour commencer à recevoir des données

### Onglet Données
- **Voir les Données** : Visualisez les données entrantes en format tableau temps réel
- **Sauvegarder les Données** : Exportez les données actuelles vers un fichier texte
- **Charger les Données** : Importez des fichiers de données précédemment sauvegardés
- **Effacer les Données** : Réinitialisez le jeu de données actuel (avec confirmation)
- **Sauvegarde Auto** : Activez/désactivez la sauvegarde automatique avec noms de fichiers horodatés

### Onglet Graphique
- **Choisir les Colonnes** : Sélectionnez l'axe X et jusqu'à 5 colonnes d'axe Y de vos données
- **Types de Graphiques** :
  - **Séries Temporelles** : Graphiques linéaires/nuages de points individuels pour chaque série de données
  - **Aires Empilées** : Graphiques en couches montrant des données cumulatives ou des pourcentages
- **Personnaliser** : Développez "Afficher les Options Avancées" pour changer couleurs, marqueurs, taux de rafraîchissement
- **Export** : Sauvegardez vos graphiques en images PNG
- **Contrôle** : Pausez/reprenez les mises à jour temps réel à tout moment

### Menu Langue
- **Changer de Langue** : Sélectionnez parmi 5 langues disponibles
- **Redémarrage Requis** : L'application vous invitera à redémarrer pour le changement de langue
- **Paramètres Conservés** : Toutes vos préférences sont gardées lors du changement de langue

## Format des Données

Votre appareil série doit envoyer des données en format texte simple :

```
# Ligne d'en-tête optionnelle
timestamp voltage current temperature

# Lignes de données (séparées par des espaces ou tabulations)
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Formats supportés :**
- Colonnes séparées par des espaces ou tabulations
- Nombres dans n'importe quelle colonne
- Ligne d'en-tête optionnelle (sera détectée automatiquement)
- Streaming temps réel ou chargement de données par lots

## Dépannage

**Problèmes de Connexion :**
- Assurez-vous que votre appareil est connecté et sous tension
- Vérifiez qu'aucun autre programme n'utilise le port série
- Essayez différents débits si les données apparaissent corrompues
- Utilisez le mode Simulé pour tester l'interface sans matériel

**Problèmes de Données :**
- Assurez-vous que les données sont séparées par des espaces ou tabulations
- Vérifiez que les nombres sont en format standard (utilisez . pour les décimales)
- Vérifiez que votre appareil envoie des données en continu
- Essayez de sauvegarder et recharger les données pour vérifier le format

**Performance :**
- Réduisez le taux de rafraîchissement si les graphiques sont lents
- Réduisez la taille de la fenêtre de données pour de meilleures performances
- Fermez d'autres programmes si le système devient non réactif

## Développement

Cette application est construite avec Python et utilise tkinter pour l'interface et matplotlib pour les graphiques.

**Pour les développeurs :**
- La base de code utilise une architecture modulaire avec des composants séparés pour l'interface utilisateur, la gestion des données et la visualisation
- Les traductions sont stockées dans des fichiers YAML dans le répertoire `languages/`
- La configuration utilise un système de préférences hiérarchique sauvegardé dans `config/prefs.yml`
- Le système de rafraîchissement des graphiques est découplé de l'arrivée des données pour une performance optimale

## Licence

Développé par CBPF-LIM (Centre Brésilien de Recherche en Physique - Laboratoire Lumière et Matière).

---

**Lim Terminal** - Communication série et visualisation de données professionnelles simplifiées.
