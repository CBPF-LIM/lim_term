# LIM Serial - GUI für Serielle Kommunikation und Datenvisualisierung

**README in:** [English](/README.md) | [Português](README_pt-br.md) | [Español](README_es.md) | [Deutsch](README_de.md) | [Français](README_fr.md)

---

## Überblick

LIM Serial ist eine moderne, internationalisierte GUI-Anwendung für serielle Kommunikation und Echtzeit-Datenvisualisierung. Mit Python/Tkinter und matplotlib gebaut, bietet sie eine benutzerfreundliche Oberfläche für die Verbindung zu seriellen Geräten, das Sammeln von Daten und die Erstellung dynamischer Grafiken.

![LIM Serial Screenshot](shot.png)

## Eigenschaften

### 🌍 **Internationalisierung**
- **5 Sprachen**: Englisch, Portugiesisch (Brasilien), Spanisch, Deutsch, Französisch
- **Echtzeit-Sprachwechsel**: Sprache wechseln ohne Neustart
- **Persistente Einstellungen**: Sprachauswahl automatisch gespeichert
- **YAML-basierte Übersetzungen**: Einfach erweiterbar mit neuen Sprachen

### 📡 **Serielle Kommunikation**
- **Hardware-Modus**: Verbindung zu echten seriellen Ports
- **Simulierter Modus**: Integrierter virtueller Port mit Datengenerierung
- **Automatische Erkennung**: Automatische Port-Erkennung und -Aktualisierung
- **Flexible Baudrate**: Unterstützung für alle Standard-Baudraten
- **Echtzeit-Status**: Verbindungsinformationen mit visueller Rückmeldung

### 📊 **Datenvisualisierung**
- **Mehrere Diagrammtypen**: Linien- und Streudiagramme
- **Multi-Serien-Plotting**: Bis zu 5 Y-Serien (Y1-Y5) gleichzeitig plotten
- **Individuelle Serienkonfiguration**: Benutzerdefinierte Farben, Markierungen und Typen pro Serie
- **Echtzeit-Updates**: Live-Datenplotting mit konfigurierbarer Aktualisierung
- **Legende-Unterstützung**: Automatische Legende für Multi-Serien-Diagramme
- **Anpassbares Erscheinungsbild**: Über 20 Farben, über 10 Markierungstypen
- **Achsenkontrolle**: Manuelle Y-Achsen-Grenzen und Fensterung
- **PNG-Export**: Speichern Sie Grafiken als hochqualitative Bilder
- **Pausieren/Fortsetzen**: Kontrolle des Datenflusses ohne Trennung

### 💾 **Datenmanagement**
- **Speichern/Laden**: Export und Import von Daten im Textformat
- **Automatisches Speichern**: Automatische Datensicherung mit Benutzerbestätigung
- **Löschfunktion**: Daten zurücksetzen mit Sicherheitsabfragen
- **Persistente Einstellungen**: Alle Einstellungen zwischen Sitzungen gespeichert

### 🎨 **Benutzeroberfläche**
- **Tab-Oberfläche**: Organisierte Konfiguration-, Daten- und Grafik-Tabs
- **Responsive Design**: Adaptives Layout mit angemessener Widget-Größe
- **Visueller Feedback**: Status-Indikatoren und Fortschrittsinformationen
- **Barrierefreiheit**: Klare Beschriftung und intuitive Navigation

## Installation

### Anforderungen
- Python 3.7+
- tkinter (normalerweise in Python enthalten)
- matplotlib
- pyserial
- PyYAML

### Abhängigkeiten installieren
```bash
pip install matplotlib pyserial PyYAML
```

### Schnellstart
```bash
# Projekt klonen oder herunterladen
cd lim_serial

# Anwendung ausführen
python lim_serial.py
```

## Nutzungsanleitung

### 1. Konfiguration-Tab
- **Modusauswahl**: Wählen zwischen Hardware- oder Simuliertem Modus
- **Port-Auswahl**: Auswahl aus verfügbaren seriellen Ports (auto-aktualisiert)
- **Baudrate**: Kommunikationsgeschwindigkeit einstellen
- **Verbinden/Trennen**: Serielle Verbindung herstellen oder schließen

### 2. Daten-Tab
- **Echtzeit-Anzeige**: Empfangene Daten in tabellarischer Form anzeigen
- **Daten speichern**: Aktuellen Datensatz in Textdatei exportieren
- **Daten laden**: Zuvor gespeicherte Daten importieren
- **Daten löschen**: Aktuellen Datensatz zurücksetzen
- **Automatisches Speichern**: Automatische Sicherung mit Benutzerbestätigung

### 3. Grafik-Tab
- **Spaltenauswahl**: X-Spalte und bis zu 5 Y-Spalten (Y1-Y5) für Darstellung wählen
- **Multi-Serien-Unterstützung**: Mehrere Datenserien gleichzeitig mit Legende darstellen
- **Individuelle Konfiguration**: Diagrammtyp, Farbe und Markierung für jede Y-Serie festlegen
- **Diagrammtypen**: Linien- oder Streudiagramm pro Serie auswählen
- **Anpassung**: Farben, Markierungen, Achsengrenzen, Fenstergröße (Standard: 50 Punkte)
- **Exportieren**: Grafiken als PNG-Bilder speichern
- **Pausieren/Fortsetzen**: Echtzeit-Updates kontrollieren

### 4. Sprachen-Menü
- **Sprachauswahl**: Verfügbar in der Hauptmenüleiste
- **Echtzeit-Wechsel**: Änderungen sofort angewendet
- **Persistent**: Spracheinstellung automatisch gespeichert

## Datenformat

Serielle Daten sollten in durch Leerzeichen getrennten Spalten gesendet werden:

```
# Kopfzeile (optional)
timestamp voltage current temperature

# Datenzeilen
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Eigenschaften:**
- Durch Leerzeichen oder Tab getrennte Werte
- Automatische Spaltenerkennung
- Numerische Datenanalyse
- Kopfzeilensupport (beim Plotten ignoriert)

## Projektarchitektur

### Konfigurationsverwaltung
- **Benutzereinstellungen**: Gespeichert in `config/prefs.yml`
- **Tab-spezifische Einstellungen**: Organisiert nach Oberflächenbereich
- **Sprach-Persistenz**: Automatisches Sprachauswahl-Gedächtnis
- **Sichere Standardwerte**: Fallback-Werte für alle Einstellungen

### Übersetzungssystem
- **YAML-basiert**: Menschenlesbare Übersetzungsdateien in `languages/`
- **Hierarchische Schlüssel**: Organisiert nach UI-Komponente und Kontext
- **Fallback-Unterstützung**: Fehlende Übersetzungen fallen zurück auf Englisch
- **Echtzeit-Updates**: Oberfläche aktualisiert sich sofort bei Sprachwechsel

## Entwicklung

### Neue Sprachen hinzufügen
1. Neue YAML-Datei im `languages/`-Verzeichnis erstellen
2. Struktur der vorhandenen Sprachdateien befolgen
3. Alle Oberflächenstrings testen
4. Pull Request einreichen

### Funktionalität erweitern
- **Serielle Protokolle**: `SerialManager` für benutzerdefinierte Protokolle erweitern
- **Diagrammtypen**: Neue Plot-Typen in `GraphManager` hinzufügen
- **Datenformate**: Benutzerdefinierte Parser in `utils/` implementieren
- **UI-Komponenten**: Neue Tabs nach vorhandenen Mustern erstellen

## Konfigurationsdateien

### Benutzereinstellungen (`config/prefs.yml`)
```yaml
language: de
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

### Sprachdateien (`languages/*.yml`)
Strukturierte Übersetzungsdateien mit hierarchischer Organisation nach UI-Komponente.

## Beitragen

1. Repository forken
2. Feature-Branch erstellen
3. Änderungen vornehmen
4. Gründlich testen (besonders Internationalisierung)
5. Pull Request einreichen

### Bereiche für Beiträge
- Neue Sprachübersetzungen
- Zusätzliche Diagrammtypen
- Erweiterte serielle Protokolle
- UI/UX-Verbesserungen
- Dokumentationsverbesserungen

## Lizenz

Entwickelt von CBPF-LIM (Brasilianisches Zentrum für Physikalische Forschung - Labor für Licht und Materie).

## Support

Für Probleme, Feature-Anfragen oder Fragen:
- Vorhandene Dokumentation prüfen
- Übersetzungsdateien für UI-Strings überprüfen
- Mit verschiedenen Sprachen und Konfigurationen testen
- Bugs mit detaillierten Reproduktionsschritten melden

---

**LIM Serial** - Moderne serielle Kommunikation einfach gemacht mit internationaler Zugänglichkeit.
