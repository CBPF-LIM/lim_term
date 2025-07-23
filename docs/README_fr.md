# LIM Serial - GUI de Communication Série et Visualisation de Données

**README en :** [English](/README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Aperçu

LIM Serial est une application GUI moderne et internationalisée pour la communication série et la visualisation de données en temps réel. Construite avec Python/Tkinter et matplotlib, elle fournit une interface conviviale pour se connecter aux appareils série, collecter des données et créer des graphiques dynamiques.

![Capture d'écran de LIM Serial](shot.png)

## Caractéristiques

### 🌍 **Internationalisation**
- **5 Langues** : Anglais, Portugais (Brésil), Espagnol, Allemand, Français
- **Changement en Temps Réel** : Changez la langue sans redémarrer
- **Préférences Persistantes** : Sélection de langue sauvegardée automatiquement
- **Traductions en YAML** : Facile à étendre avec de nouvelles langues

### 📡 **Communication Série**
- **Mode Matériel** : Connexion aux ports série réels
- **Mode Simulé** : Port virtuel intégré avec génération de données
- **Détection Automatique** : Découverte et actualisation automatique des ports
- **Débit Flexible** : Support de tous les débits standard
- **État en Temps Réel** : Informations de connexion avec retour visuel

### 📊 **Visualisation de Données**
- **Multiples Types de Graphiques** : Ligne et Dispersion
- **Traçage Multi-Séries** : Tracer jusqu'à 5 séries Y (Y1-Y5) simultanément
- **Configuration Individuelle des Séries** : Couleurs, marqueurs et types personnalisés par série
- **Mises à Jour en Temps Réel** : Traçage de données en direct avec actualisation configurable
- **Support de Légende** : Légende automatique pour les graphiques multi-séries
- **Apparence Personnalisable** : Plus de 20 couleurs, plus de 10 types de marqueurs
- **Contrôle des Axes** : Limites manuelles de l'axe Y et fenêtrage
- **Export PNG** : Sauvegardez les graphiques comme images haute qualité
- **Pause/Reprendre** : Contrôlez le flux de données sans déconnecter

### 💾 **Gestion des Données**
- **Sauvegarder/Charger** : Exporter et importer des données en format texte
- **Sauvegarde Automatique** : Sauvegarde automatique des données avec confirmation utilisateur
- **Fonction Effacer** : Réinitialiser les données avec invites de sécurité
- **Paramètres Persistants** : Toutes les préférences sauvegardées entre les sessions

### 🎨 **Interface Utilisateur**
- **Interface à Onglets** : Onglets organisés Configuration, Données et Graphique
- **Design Responsive** : Mise en page adaptative avec dimensionnement approprié des widgets
- **Retour Visuel** : Indicateurs d'état et informations de progression
- **Accessibilité** : Étiquetage clair et navigation intuitive

## Installation

### Prérequis
- Python 3.7+
- tkinter (généralement inclus avec Python)
- matplotlib
- pyserial
- PyYAML

### Installer les Dépendances
```bash
pip install matplotlib pyserial PyYAML
```

### Démarrage Rapide
```bash
# Cloner ou télécharger le projet
cd lim_serial

# Exécuter l'application
python lim_serial.py
```

## Guide d'Utilisation

### 1. Onglet Configuration
- **Sélection de Mode** : Choisissez entre mode Matériel ou Simulé
- **Sélection de Port** : Sélectionnez parmi les ports série disponibles (auto-actualisés)
- **Débit** : Configurez la vitesse de communication
- **Connecter/Déconnecter** : Établissez ou fermez la connexion série

### 2. Onglet Données
- **Affichage en Temps Réel** : Visualisez les données reçues en format tabulaire
- **Sauvegarder les Données** : Exportez le jeu de données actuel vers un fichier texte
- **Charger les Données** : Importez des données précédemment sauvegardées
- **Effacer les Données** : Réinitialisez le jeu de données actuel
- **Sauvegarde Automatique** : Sauvegarde automatique avec confirmation utilisateur

### 3. Onglet Graphique
- **Sélection de Colonnes** : Choisissez colonne X et jusqu'à 5 colonnes Y (Y1-Y5) pour le traçage
- **Support Multi-Séries** : Tracez plusieurs séries de données simultanément avec légende
- **Configuration Individuelle** : Définissez type de graphique, couleur et marqueur pour chaque série Y
- **Types de Graphiques** : Sélectionnez graphique Ligne ou Dispersion par série
- **Personnalisation** : Couleurs, marqueurs, limites d'axe, taille de fenêtre (défaut : 50 points)
- **Exporter** : Sauvegardez les graphiques comme images PNG
- **Pause/Reprendre** : Contrôlez les mises à jour en temps réel

### 4. Menu des Langues
- **Sélection de Langue** : Disponible dans la barre de menu principale
- **Changement en Temps Réel** : Les changements s'appliquent immédiatement
- **Persistant** : Préférence de langue sauvegardée automatiquement

## Format des Données

Les données série doivent être envoyées en colonnes séparées par des espaces :

```
# En-tête (optionnel)
timestamp voltage current temperature

# Lignes de données
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Caractéristiques :**
- Valeurs séparées par espace ou tabulation
- Détection automatique des colonnes
- Analyse de données numériques
- Support de ligne d'en-tête (ignorée lors du traçage)

## Architecture du Projet

### Gestion de Configuration
- **Préférences Utilisateur** : Stockées dans `config/prefs.yml`
- **Paramètres Spécifiques aux Onglets** : Organisés par section d'interface
- **Persistance de Langue** : Mémoire automatique de sélection de langue
- **Valeurs par Défaut Sûres** : Valeurs de repli pour toutes les préférences

### Système de Traduction
- **Basé sur YAML** : Fichiers de traduction lisibles dans `languages/`
- **Clés Hiérarchiques** : Organisées par composant UI et contexte
- **Support de Repli** : Les traductions manquantes reviennent à l'anglais
- **Mises à Jour en Temps Réel** : L'interface se met à jour immédiatement lors du changement de langue

## Développement

### Ajouter de Nouvelles Langues
1. Créez un nouveau fichier YAML dans le répertoire `languages/`
2. Suivez la structure des fichiers de langue existants
3. Testez toutes les chaînes d'interface
4. Soumettez une pull request

### Étendre la Fonctionnalité
- **Protocoles Série** : Étendez `SerialManager` pour des protocoles personnalisés
- **Types de Graphiques** : Ajoutez de nouveaux types de tracé dans `GraphManager`
- **Formats de Données** : Implémentez des analyseurs personnalisés dans `utils/`
- **Composants UI** : Créez de nouveaux onglets suivant les modèles existants

## Fichiers de Configuration

### Préférences Utilisateur (`config/prefs.yml`)
```yaml
language: fr
tabs:
  config:
    mode: Hardware
    port: "/dev/ttyUSB0"
    baudrate: "9600"
  graph:
    type: Line
    color: Blue
    marker: circle
    window_size: "100"
    x_column: "1"
    y_column: "2"
```

### Fichiers de Langue (`languages/*.yml`)
Fichiers de traduction structurés avec organisation hiérarchique par composant UI.

## Contribuer

1. Forkez le dépôt
2. Créez une branche de fonctionnalité
3. Effectuez vos changements
4. Testez complètement (surtout l'internationalisation)
5. Soumettez une pull request

### Domaines de Contribution
- Nouvelles traductions de langues
- Types de graphiques supplémentaires
- Protocoles série améliorés
- Améliorations UI/UX
- Améliorations de documentation

## Licence

Développé par CBPF-LIM (Centre Brésilien de Recherches Physiques - Laboratoire de Lumière et Matière).

## Support

Pour les problèmes, demandes de fonctionnalités ou questions :
- Vérifiez la documentation existante
- Examinez les fichiers de traduction pour les chaînes UI
- Testez avec différentes langues et configurations
- Rapportez les bugs avec des étapes de reproduction détaillées

---

**LIM Serial** - Communication série moderne simplifiée avec accessibilité internationale.
