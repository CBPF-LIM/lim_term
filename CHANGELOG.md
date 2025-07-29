# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
