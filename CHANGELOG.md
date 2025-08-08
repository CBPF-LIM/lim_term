# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-08-08

### Added
- **Data Buffer Architecture**: Completely redesigned data handling with efficient ring buffer system
  - Optimized memory usage for large datasets
  - Real-time data preview with configurable display limits
  - Background data capture with minimal UI impact
- **Advanced Data Management**: Professional-grade data capture and analysis features
  - Live data timestamps with runtime tracking
  - Configurable automatic/manual filename modes for captures
  - Append/overwrite file modes for data logging
  - Pause/resume preview functionality for data analysis
- **Matplotlib Performance Optimizations**: Dramatically improved plotting performance
  - Disabled antialiasing and unnecessary rendering features
  - Optimized figure parameters and reduced DPI for faster updates
  - Enhanced refresh rates up to 30 FPS with minimal CPU usage
- **Real-Time Oscilloscope Enhancements**: Major improvements to oscilloscope functionality
  - Simplified update loop
  - Improved trigger detection with better edge handling
  - Visual distinction between current and old triggered data
- **Keyboard Navigation**: Added keyboard shortcuts for efficient workflow
  - `Ctrl+1-4` for quick tab switching
- **Menu System**: Complete application menu with language switching
  - Menu bar with organized options
  - Language switching directly from menu
  - Better integration with OS conventions
- **Internationalization Tools**: Development tools for translation management
  - YAML language file synchronization utilities (dev)
  - Translation validation and consistency checking (dev)
  - Automated language file maintenance (dev)

### Improved
- **User Interface**: Major redesign for better usability and performance
  - Collapsible settings panels across all tabs
  - Improved widget state management and visual feedback
  - Enhanced preference widgets with automatic save/load
  - Better tab activation handling for resource optimization
- **Data Visualization**: Enhanced chart rendering and interaction
  - Optimized rendering pipeline for smooth real-time updates
  - Improved stacked chart normalization options
  - Better color and marker management systems
- **Configuration Management**: Advanced settings persistence and organization
  - Better default value handling across all widgets

### Performance
- **Rendering Optimization**: Massive performance improvements for real-time visualization
  - Reduced matplotlib overhead by 60-80%
  - Optimized update frequencies with intelligent throttling
  - Memory leak prevention in chart rendering
- **Data Processing**: Efficient handling of high-frequency data streams
  - Optimized buffer management for continuous data capture
  - Reduced CPU usage during intensive data collection
  - Better memory management for long-running sessions

## [0.6.0] - 2025-08-06

### Added
- **Oscilloscope Mode**: Complete oscilloscope functionality with trigger system
  - Rising, falling, and both edge trigger modes
  - Continuous and single capture modes
  - Configurable trigger level and source column
  - Real-time waveform visualization with onion-skin effect
  - Capture window size control
  - Auto-save captured waveforms as PNG and TXT
- **Enhanced Visualization**: N-set ring buffer for overlapping waveform display

### Improved
- **Language Loading**: Moved i18n initialization before UI creation for consistent translations
- **Preference Widgets**: Enhanced PrefCombobox with proper value mapping for language independence

### Technical
- Added ring buffer architecture with bounds checking and age calculation
- Implemented comprehensive value mapping system for combo boxes
- Enhanced preference loading with automatic translation key resolution

## [0.5.0] - 2025-07-29

### Fixed
- **macOS Compatibility**: Fixed matplotlib backend issues on macOS by setting TkAgg explicitly
- **Build System**: Updated build configuration text for multi-platform support

### Technical
- Set matplotlib to use TkAgg backend for better cross-platform compatibility
- Enhanced build pipeline for consistent behavior across operating systems

## [0.4.0] - 2025-07-29

### Added
- Added "Available Math Functions" display in synthetic mode showing all available math functions
- Synthetic equations can reference other (in cascade) using a letter: n (index), a,b, c, d and e

### Improved
- **Enhanced Safety**: Replaced unsafe `eval()` with secure `asteval` library for equation evaluation
- **Graph Legends**: Changed legend position from random to "upper right"
- **Data Generation**: Now always includes index (n) as the first column in synthetic data
- **Math Functions**: All Python math functions are now directly available in equations without `math.` prefix

### Technical
- Migrated from `eval()` to `asteval.Interpreter()` for secure expression evaluation
- Enhanced equation parsing with proper variable scoping and error recovery
- Improved synthetic data output format and reliability

## [0.3.0] - 2025-07-28

### Added
- Added Syntheric mode.
- Synthetic mode lets you select data generation speed.
- Synthetic mode can have 5 equations to generate data

### Fixed
- Fixed translation bugs in mode selection or synthetic controls.
- FPS and equation widgets are always enabled/disabled correctly based on connection state.

## [0.2.0] - 2025-07-27

### Improved
- Settings now save automatically when you change them
- Your preferences are remembered correctly when switching languages
- Much faster and more responsive interface
- Cleaner, more organized user interface

### Fixed
- Settings now save properly and persist between sessions
- Graph options are correctly restored when reopening the app
- Removed unnecessary error messages that cluttered the interface
- Dropdown menus now work correctly in all languages

## [0.1.0] - 2024-12-XX

### Features
- Connect to Arduino, ESP32, and other serial devices
- Real-time data visualization with customizable charts
- Multi-language support: English, Spanish, Portuguese, French, German
- Export charts as PNG images
- Save and load data from text files
- Test your setups with built-in serial port simulation
- Works on Windows, Linux, and macOS

### Charts & Visualization
- Live updating graphs as data arrives
- Choose from line charts, scatter plots, and stacked visualizations
- Customize colors, markers, and line styles
- Adjustable refresh rates for smooth or fast updates
- Data windowing to focus on recent measurements
- Auto-scroll to follow the latest data

### Ease of Use
- Automatic serial port detection
- Your settings are saved and restored automatically
- Simple interface for selecting data columns to plot
- Clear data display with scrolling history
- Intuitive connection management
