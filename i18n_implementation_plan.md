# I18n Implementation Plan

## Overview
Convert the LIM Serial project from hardcoded Portuguese strings to a full internationalization system using YAML files.

## Implementation Steps

### Phase 1: Infrastructure Setup
- [x] Create `languages/` folder structure
- [x] Create base i18n system using PyYAML
- [x] Create language manager class
- [x] Create config system for language persistence

### Phase 2: Language Files Creation
- [x] Create `en.yml` (canonical/reference language)
- [x] Extract all Portuguese strings from codebase
- [x] Organize strings by modules/contexts
- [x] Create `pt-br.yml` (Portuguese Brazil)
- [x] Create `es.yml` (Spanish)
- [x] Create `fr.yml` (French)
- [x] Create `de.yml` (German)

### Phase 3: Code Integration
- [ ] Update main_window.py to use i18n
- [ ] Update config_tab.py to use i18n
- [ ] Update data_tab.py to use i18n
- [ ] Update graph_tab.py to use i18n
- [ ] Update core modules to use i18n
- [ ] Update utils modules to use i18n

### Phase 4: Language Selection UI
- [ ] Add language menu to main interface
- [ ] Implement language switching functionality
- [ ] Save language preference to config
- [ ] Load saved language on startup

### Phase 5: Testing & Validation
- [ ] Test all languages
- [ ] Verify all strings are translated
- [ ] Test language switching
- [ ] Test config persistence

## File Structure
```
/languages/
  ├── en.yml (canonical)
  ├── pt-br.yml
  ├── es.yml
  ├── fr.yml
  └── de.yml
/lim_serial/
  ├── i18n/
  │   ├── __init__.py
  │   ├── language_manager.py
  │   └── config_manager.py
  └── config/
      └── user_config.yml
```

## Translation Keys Structure
```yaml
language:
  name: "English"
  code: "en"

ui:
  main_window:
    title: "LIM Serial - GUI"
  tabs:
    configuration: "Configuration"
    data: "Data"
    graph: "Graph"
  buttons:
    connect: "Connect"
    disconnect: "Disconnect"
    save: "Save"
    load: "Load"
    clear: "Clear"
    update_graph: "Update Graph"
    pause: "Pause"
    resume: "Resume"
```

## Notes
- Default language: English (en.yml)
- Fallback system: if key missing in selected language, use English
- Config file: `config/user_config.yml`
- Easy human-editable YAML format
- Modular organization by UI sections
