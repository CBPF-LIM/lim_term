"""
Language file synchronizer for limterm project.
Synchronizes all language files with en.yml structure while preserving existing translations.
"""

import os
import sys
import yaml
from pathlib import Path
from collections import OrderedDict


class LanguageSynchronizer:
    def __init__(self, languages_dir):
        self.languages_dir = Path(languages_dir)
        self.en_file = self.languages_dir / "en.yml"

        # Translation mappings for common terms
        self.translations = {
            'pt-br': {
                'Error': 'Erro',
                'Settings': 'Configurações',
                'Data': 'Dados',
                'Graph': 'Gráfico',
                'Show': 'Mostrar',
                'Hide': 'Ocultar',
                'Save': 'Salvar',
                'Load': 'Carregar',
                'Clear': 'Limpar',
                'Connect': 'Conectar',
                'Disconnect': 'Desconectar',
                'Mode': 'Modo',
                'Port': 'Porta',
                'Status': 'Status',
                'Configuration': 'Configuração',
                'Hardware': 'Hardware',
                'Synthetic': 'Sintético',
                'Capture': 'Captura',
                'Preview': 'Visualização',
                'File': 'Arquivo',
                'Enabled': 'Habilitado',
                'Disabled': 'Desabilitado',
                'Trigger': 'Gatilho',
                'Level': 'Nível',
                'Edge': 'Borda',
                'Column': 'Coluna',
                'Value': 'Valor',
                'Amplitude': 'Amplitude',
                'Samples': 'Amostras',
                'Time': 'Tempo',
                'Complete': 'Completo',
                'Colors': 'Cores',
                'Axis': 'Eixo',
                'Columns': 'Colunas',
                'Limits': 'Limites',
                'Application': 'Aplicação',
                'interrupted': 'interrompida',
                'operation': 'operação',
                'export': 'exportação',
                'import': 'importação',
                'write': 'escrita',
                'plot': 'gráfico',
                'main loop': 'loop principal',
                'mock serial': 'serial simulada',
                'realtime': 'tempo real',
                'final': 'final',
                'Simulate': 'Simular',
                'Generate': 'Gerar'
            },
            'fr': {
                'Error': 'Erreur',
                'Settings': 'Paramètres',
                'Data': 'Données',
                'Graph': 'Graphique',
                'Show': 'Afficher',
                'Hide': 'Masquer',
                'Save': 'Enregistrer',
                'Load': 'Charger',
                'Clear': 'Effacer',
                'Connect': 'Connecter',
                'Disconnect': 'Déconnecter',
                'Mode': 'Mode',
                'Port': 'Port',
                'Status': 'Statut',
                'Configuration': 'Configuration',
                'Hardware': 'Matériel',
                'Synthetic': 'Synthétique',
                'Capture': 'Capture',
                'Preview': 'Aperçu',
                'File': 'Fichier',
                'Enabled': 'Activé',
                'Disabled': 'Désactivé',
                'Trigger': 'Déclencheur',
                'Level': 'Niveau',
                'Edge': 'Front',
                'Column': 'Colonne',
                'Value': 'Valeur',
                'Amplitude': 'Amplitude',
                'Samples': 'Échantillons',
                'Time': 'Temps',
                'Complete': 'Complet',
                'Colors': 'Couleurs',
                'Axis': 'Axe',
                'Columns': 'Colonnes',
                'Limits': 'Limites',
                'Application': 'Application',
                'interrupted': 'interrompue',
                'operation': 'opération',
                'export': 'exportation',
                'import': 'importation',
                'write': 'écriture',
                'plot': 'graphique',
                'main loop': 'boucle principale',
                'mock serial': 'série simulée',
                'realtime': 'temps réel',
                'final': 'final',
                'Simulate': 'Simuler',
                'Generate': 'Générer'
            },
            'es': {
                'Error': 'Error',
                'Settings': 'Configuraciones',
                'Data': 'Datos',
                'Graph': 'Gráfico',
                'Show': 'Mostrar',
                'Hide': 'Ocultar',
                'Save': 'Guardar',
                'Load': 'Cargar',
                'Clear': 'Limpiar',
                'Connect': 'Conectar',
                'Disconnect': 'Desconectar',
                'Mode': 'Modo',
                'Port': 'Puerto',
                'Status': 'Estado',
                'Configuration': 'Configuración',
                'Hardware': 'Hardware',
                'Synthetic': 'Sintético',
                'Capture': 'Captura',
                'Preview': 'Vista previa',
                'File': 'Archivo',
                'Enabled': 'Habilitado',
                'Disabled': 'Deshabilitado',
                'Trigger': 'Disparador',
                'Level': 'Nivel',
                'Edge': 'Flanco',
                'Column': 'Columna',
                'Value': 'Valor',
                'Amplitude': 'Amplitud',
                'Samples': 'Muestras',
                'Time': 'Tiempo',
                'Complete': 'Completo',
                'Colors': 'Colores',
                'Axis': 'Eje',
                'Columns': 'Columnas',
                'Limits': 'Límites',
                'Application': 'Aplicación',
                'interrupted': 'interrumpida',
                'operation': 'operación',
                'export': 'exportación',
                'import': 'importación',
                'write': 'escritura',
                'plot': 'gráfico',
                'main loop': 'bucle principal',
                'mock serial': 'serie simulada',
                'realtime': 'tiempo real',
                'final': 'final'
            },
            'de': {
                'Error': 'Fehler',
                'Settings': 'Einstellungen',
                'Data': 'Daten',
                'Graph': 'Grafik',
                'Show': 'Anzeigen',
                'Hide': 'Ausblenden',
                'Save': 'Speichern',
                'Load': 'Laden',
                'Clear': 'Löschen',
                'Connect': 'Verbinden',
                'Disconnect': 'Trennen',
                'Mode': 'Modus',
                'Port': 'Port',
                'Status': 'Status',
                'Configuration': 'Konfiguration',
                'Hardware': 'Hardware',
                'Synthetic': 'Synthetisch',
                'Capture': 'Erfassung',
                'Preview': 'Vorschau',
                'File': 'Datei',
                'Enabled': 'Aktiviert',
                'Disabled': 'Deaktiviert',
                'Trigger': 'Trigger',
                'Level': 'Pegel',
                'Edge': 'Flanke',
                'Column': 'Spalte',
                'Value': 'Wert',
                'Amplitude': 'Amplitude',
                'Samples': 'Proben',
                'Time': 'Zeit',
                'Complete': 'Vollständig',
                'Colors': 'Farben',
                'Axis': 'Achse',
                'Columns': 'Spalten',
                'Limits': 'Grenzen',
                'Application': 'Anwendung',
                'interrupted': 'unterbrochen',
                'operation': 'Operation',
                'export': 'Export',
                'import': 'Import',
                'write': 'Schreiben',
                'plot': 'Diagramm',
                'main loop': 'Hauptschleife',
                'mock serial': 'simulierte serielle',
                'realtime': 'Echtzeit',
                'final': 'endgültig'
            }
        }

    def load_yaml_preserve_order(self, file_path):
        """Load YAML file preserving order."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def save_yaml_preserve_order(self, data, file_path):
        """Save YAML file with proper formatting."""
        try:
            # First, save normally
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True, indent=2, sort_keys=False)
            return True
        except Exception as e:
            print(f"Error saving {file_path}: {e}")
            return False

    def auto_translate(self, text, lang_code):
        """Attempt to auto-translate common terms."""
        if lang_code not in self.translations:
            return text

        trans_dict = self.translations[lang_code]

        # Try exact match first
        if text in trans_dict:
            return trans_dict[text]

        # Try partial matches for common patterns
        result = text
        for en_term, translated_term in trans_dict.items():
            if en_term.lower() in text.lower():
                result = result.replace(en_term, translated_term)

        return result

    def merge_structures(self, en_data, lang_data, lang_code, path=""):
        """Recursively merge English structure with existing language data."""
        if isinstance(en_data, dict):
            if lang_data is None:
                lang_data = {}

            result = {}
            for key, value in en_data.items():
                current_path = f"{path}.{key}" if path else key

                if key in lang_data:
                    # Key exists, recurse if it's a dict
                    if isinstance(value, dict) and isinstance(lang_data[key], dict):
                        result[key] = self.merge_structures(value, lang_data[key], lang_code, current_path)
                    else:
                        # Keep existing translation
                        result[key] = lang_data[key]
                else:
                    # Key doesn't exist, add with auto-translation if possible
                    if isinstance(value, dict):
                        result[key] = self.merge_structures(value, {}, lang_code, current_path)
                    else:
                        # Try to auto-translate
                        translated = self.auto_translate(value, lang_code)
                        result[key] = translated
                        print(f"  + Added {current_path}: '{translated}' (auto-translated from '{value}')")

            return result
        else:
            # Not a dict, return the value (should be preserved from lang_data)
            return lang_data if lang_data is not None else en_data

    def remove_extra_keys(self, en_data, lang_data, path=""):
        """Remove keys that don't exist in English structure."""
        if not isinstance(en_data, dict) or not isinstance(lang_data, dict):
            return lang_data

        result = {}
        for key, value in lang_data.items():
            current_path = f"{path}.{key}" if path else key

            if key in en_data:
                if isinstance(value, dict) and isinstance(en_data[key], dict):
                    result[key] = self.remove_extra_keys(en_data[key], value, current_path)
                else:
                    result[key] = value
            else:
                print(f"  - Removed extra key: {current_path}")

        return result

    def sync_language_file(self, lang_file, en_data):
        """Synchronize a single language file with English structure."""
        lang_code = lang_file.stem
        print(f"\n--- Synchronizing {lang_file.name} ---")

        # Load existing language data
        lang_data = self.load_yaml_preserve_order(lang_file)
        if lang_data is None:
            lang_data = {}

        print(f"  📖 Loaded {len(str(lang_data))} characters from existing file")

        # Remove extra keys first
        cleaned_data = self.remove_extra_keys(en_data, lang_data)

        # Merge with English structure
        merged_data = self.merge_structures(en_data, cleaned_data, lang_code)

        # Save updated file
        if self.save_yaml_preserve_order(merged_data, lang_file):
            print(f"✅ Successfully updated {lang_file.name}")
            return True
        else:
            print(f"❌ Failed to save {lang_file.name}")
            return False

    def sync_all(self):
        """Synchronize all language files with English structure."""
        print("🔄 Language File Synchronizer")
        print("=" * 50)

        # Load English reference
        if not self.en_file.exists():
            print(f"❌ Reference file {self.en_file} not found!")
            return False

        en_data = self.load_yaml_preserve_order(self.en_file)
        if en_data is None:
            print("❌ Failed to load English reference file!")
            return False

        print(f"📋 Using {self.en_file.name} as reference")

        # Find all language files
        lang_files = [f for f in self.languages_dir.glob("*.yml") if f.name != "en.yml"]

        if not lang_files:
            print("❌ No language files found to synchronize!")
            return False

        print(f"🌐 Found {len(lang_files)} language files to synchronize")

        # Synchronize each file
        success = True
        for lang_file in sorted(lang_files):
            if not self.sync_language_file(lang_file, en_data):
                success = False

        print("\n" + "=" * 50)
        if success:
            print("✅ All language files synchronized successfully!")
        else:
            print("❌ Some files failed to synchronize")

        return success


def main():
    print("🔄 Language File Synchronizer - Starting...")

    if len(sys.argv) != 2:
        print("Usage: python sync_languages.py <languages_directory>")
        sys.exit(1)

    languages_dir = sys.argv[1]

    if not os.path.exists(languages_dir):
        print(f"Error: Directory {languages_dir} does not exist!")
        sys.exit(1)

    synchronizer = LanguageSynchronizer(languages_dir)
    success = synchronizer.sync_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
