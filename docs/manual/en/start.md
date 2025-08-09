<p align="center">
  <a href="index.md">Index</a> ·
  <a href="index.md">Prev</a> ·
  <a href="language.md">Next</a>
</p>

# Getting Started

Lim Terminal is a lightweight, cross‑platform desktop app to communicate with serial devices (Arduino/ESP32 and others) and visualize data in real time.

## Use cases:

- Validate sensors and embedded firmware quickly
- Log and analyze lab measurements
- Prototype dashboards for experiments or classroom demos

## Install:

- Standalones
  - Windows and macOS: [Download from Release page ](https://github.com/CBPF-LIM/lim_term/releases)
- Python - From source:
  - pip:
    - $ `pip3 install git+https://github.com/CBPF-LIM/lim_term.git`
    - $ `python3 -m limterm.main`
  - pipx - Install a python package in system
    - $ `pipx install git+https://github.com/CBPF-LIM/lim_term.git`
    - $ `pipx ensurepath`
    - $ `limterm`
  - make
    - $ `git clone https://github.com/CBPF-LIM/lim_term.git`
    - $ `cd lim_term`
    - $ `make setup`
    - $ `make run`

## Notes about OS security:

- Windows
  - SmartScreen: choose Run anyway to allow the unsigned binary
- macOS:
  - Execute in terminal, in the same folder you downloaded the binary:
  - `xattr -d com.apple.quarantine LimTerm-macOS`
  - `chmod +x LimTerm-macOS`

## Dev

stack: tkinter, matplotlib, pyserial, PyYAML, asteval, poetry, pyinstaller, GitHub Actions.

Uses a simplifyed i18n system and preference widgets wrapper for auto saving changes to file.

<p align="center">
  <a href="index.md">Index</a> ·
  <a href="index.md">Prev</a> ·
  <a href="language.md">Next</a>
</p>
