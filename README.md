# Lim Terminal - Serial Communication & Data Visualization

**README in:** [English](README.md) | [Português](docs/README_pt-br.md) | [Español](docs/README_es.md) | [Deutsch](docs/README_de.md) | [Français](docs/README_fr.md)

---

## Overview

Lim Terminal is a user-friendly application for serial communication and real-time data visualization. Connect to Arduino or other serial devices, collect data, and create dynamic graphs with professional visualization features. Available in 5 languages with automatic preferences saving.

![Lim Terminal Screenshot](docs/shot.png)

![Lim Terminal Screenshot](docs/shot_stacked.png)

## Features

### 🌍 **Multiple Languages**
- Available in English, Portuguese, Spanish, German, and French
- Change language from the menu (requires restart)
- All settings preserved when switching languages

### 📡 **Easy Serial Connection**
- Connect to real serial devices (Arduino, sensors, etc.)
- Built-in simulation mode for testing without hardware
- Automatic port detection with one-click refresh
- Full Arduino IDE baudrate compatibility (300-2000000 bps)

### 📊 **Professional Data Visualization**
- **Time Series Charts**: Plot up to 5 data columns simultaneously
- **Stacked Area Charts**: Compare data as absolute values or percentages
- **Customizable Appearance**: Choose colors, markers, and line types for each data series
- **Real-time Updates**: Configurable refresh rates (1-30 FPS)
- **Export**: Save graphs as high-quality PNG images
- **Interactive Controls**: Pause/resume data collection, zoom, and pan

### 💾 **Smart Data Management**
- **Manual Save/Load**: Export and import your data anytime
- **Automatic Backup**: Optional autosave with timestamped filenames
- **Data Safety**: Clear data with confirmation prompts
- **All Settings Saved**: Preferences automatically preserved between sessions

## Getting Started

### Requirements
- Python 3.8 or newer
- Internet connection for dependency installation

### Installation

#### Method 1: Direct Installation (Recommended)
```bash
# Install directly from GitHub
pip install git+https://github.com/CBPF-LIM/lim_term.git

# Run the application
limterm
```

#### Method 2: Development Installation
```bash
# Clone the repository
git clone https://github.com/CBPF-LIM/lim_term.git
cd lim_term

# Install using Poetry (recommended for development)
pip install poetry
poetry install
poetry run limterm


### First Steps
1. **Language**: Choose your language from the Language menu
2. **Connection**: Go to Configuration tab, select your serial port and baudrate
3. **Data**: Switch to Data tab to see incoming data
4. **Visualization**: Use Graph tab to create charts from your data

## How to Use

### Configuration Tab
- **Mode**: Choose "Hardware" for real devices, "Simulated" for testing
- **Port**: Select your serial port (click Refresh to update the list)
- **Baudrate**: Set the communication speed (match your device settings)
- **Connect**: Click to start receiving data

### Data Tab
- **View Data**: See incoming data in real-time table format
- **Save Data**: Export current data to a text file
- **Load Data**: Import previously saved data files
- **Clear Data**: Reset the current dataset (with confirmation)
- **Autosave**: Toggle automatic backup with timestamped filenames

### Graph Tab
- **Choose Columns**: Select X-axis and up to 5 Y-axis columns from your data
- **Chart Types**:
  - **Time Series**: Individual line/scatter plots for each data series
  - **Stacked Area**: Layered charts showing cumulative data or percentages
- **Customize**: Expand "Show Advanced Options" to change colors, markers, refresh rate
- **Export**: Save your graphs as PNG images
- **Control**: Pause/resume real-time updates anytime

### Language Menu
- **Switch Language**: Select from 5 available languages
- **Restart Required**: Application will prompt you to restart for language change
- **Settings Preserved**: All your preferences are kept when changing languages

## Data Format

Your serial device should send data in simple text format:

```
# Optional header line
timestamp voltage current temperature

# Data rows (space or tab separated)
1.0 3.3 0.125 25.4
2.0 3.2 0.130 25.6
3.0 3.4 0.122 25.2
```

**Supported formats:**
- Space or tab-separated columns
- Numbers in any column
- Optional header row (will be detected automatically)
- Real-time streaming or batch data loading

## Troubleshooting

**Connection Issues:**
- Make sure your device is connected and powered on
- Check that no other program is using the serial port
- Try different baudrates if data appears garbled
- Use Simulated mode to test the interface without hardware

**Data Problems:**
- Ensure data is space or tab-separated
- Check that numbers are in standard format (use . for decimals)
- Verify your device is sending data continuously
- Try saving and reloading data to check format

**Performance:**
- Lower the refresh rate if charts are slow
- Reduce the data window size for better performance
- Close other programs if the system becomes unresponsive

## Development

This application is built with Python and uses tkinter for the interface and matplotlib for graphs.

**For developers:**
- The codebase uses a modular architecture with separate components for GUI, data management, and visualization
- Translations are stored in YAML files in the `languages/` directory
- Configuration uses a hierarchical preference system saved in `config/prefs.yml`
- The chart refresh system is decoupled from data arrival for optimal performance

**Contributing:**
- Fork the repository and create a feature branch
- Test changes with multiple languages and data scenarios
- Submit pull requests with clear descriptions
- Focus areas: new languages, visualization types, protocol support

## License

Developed by CBPF-LIM (Brazilian Center for Research in Physics - Light and Matter Laboratory).

---

**Lim Terminal** - Professional serial communication and data visualization made simple.
