# Refactor Analysis (step 3)

Scope: limterm/gui/{preference_widgets.py,config_tab.py,osc_tab.py,data_tab.py,graph_tab.py}

Key issues observed:

1) File length and complexity
- GraphTab (~900+ lines) and DataTab (~580 lines) mix UI construction, state, data parsing, plotting, and persistence logic in one class.
- Deeply nested UI building code reduces readability and testability.

2) Duplication / DRY violations
- Repeated color lists and marker lists/mappings in GraphTab; these also exist as constants in config.py.
- Duplicate directory-creation logic for captures in DataTab.
- Timestamp formatting logic duplicated across preview & save paths.

3) Unused code / imports
- GraphTab imported DEFAULT_Y_COLUMN but did not use it.
- DataTab contained a private method _save_buffer_to_file that is never called.

4) Tight coupling and cross-cutting concerns
- GUI code interleaved with data formatting (timestamp injection) and file I/O (capture/save) without clear abstraction boundaries.
- Localized strings lookup (t(...)) scattered across mapping builders, making testing harder.

5) Magic values and constants
- Literal strings like "lim_captures" appear in multiple places.
- Marker-to-matplotlib mapping duplicated instead of reusing MARKER_MAPPING from config.

6) State handling
- Parallel preview update functions (_refresh_preview and _update_preview) with similar responsibilities but differing behaviors (offset vs tail) increase maintenance cost.

7) Minor style/consistency
- Some methods are lengthy and do many things; early returns and helpers can simplify.

Initial recommendations:
- Centralize UI mappings (colors/markers) in a small helper module that reads values from config and translates with i18n.
- Extract generic formatting (timestamps) and directory management.
- Remove unused imports/methods.
- Use shared constants (e.g., CAPTURE_DIR) in config.
- Consider splitting GraphTab into subcomponents (series config, global settings, plot control) in future iterations.
