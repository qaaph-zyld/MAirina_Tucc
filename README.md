# RimerSR - Serbian Rhyme Suggester

**RimerSR** is an offline Serbian rhyme suggester that works with both Latin and Cyrillic input. It provides both a beautiful Streamlit UI and a command-line interface for finding rhymes in Serbian.

## Features

- ✅ **Offline operation** after initial dictionary download
- ✅ **Latin & Cyrillic support** - Input in either script
- ✅ **Streamlit UI** - Beautiful, modern interface
- ✅ **CLI interface** - For terminal usage
- ✅ **Fast** - Cached dictionary and index building
- ✅ **Open source** - 100% open-source dependencies

## Requirements

- Python 3.10 or higher
- Windows PowerShell (for setup scripts)
- Internet connection (for initial dictionary download only)

## Quick Start (Windows PowerShell)

1. **Clone or download this repository**

2. **Run the setup script:**
   ```powershell
   .\scripts\setup.ps1
   ```
   This will:
   - Create a Python virtual environment
   - Install all dependencies
   - Download the Serbian Hunspell dictionary

3. **Run the application:**
   ```powershell
   .\scripts\run.ps1
   ```
   This will start the Streamlit UI in your browser.

## Usage

### Streamlit UI

After running `.\scripts\run.ps1`, the web interface will open automatically. You can:

- **Single word tab:** Find rhymes for one word at a time
- **Paste lyrics tab:** Paste multiple lines and get rhymes for the last word of each line

**Controls:**
- **Rhyme tightness:** 1-3 syllables from the end to match
- **Max results:** How many rhymes to display (10-200)
- **Show Cyrillic:** Toggle to see both Latin and Cyrillic outputs

### CLI Interface

Activate the virtual environment first:
```powershell
.venv\Scripts\Activate.ps1
```

**Find rhymes for a single word:**
```powershell
python cli.py ljubav --syllables 2 --max 50
```

**Find rhymes for words in a file:**
```powershell
python cli.py --file lyrics.txt --syllables 2 --max 50
```

**Show Cyrillic output:**
```powershell
python cli.py word --cyrillic
```

**Use a custom dictionary:**
```powershell
python cli.py word --dict "path\to\custom.dic"
```

## Running in VS Code / Windsurf

1. Open the integrated terminal (`` Ctrl+` ``)
2. Run the setup script:
   ```powershell
   .\scripts\setup.ps1
   ```
3. Run the app:
   ```powershell
   .\scripts\run.ps1
   ```

The Streamlit app will open in your default browser automatically.

## Project Structure

```
rimer-sr/
├── app.py                  # Streamlit UI application
├── cli.py                  # Command-line interface
├── rhyme_engine.py         # Core rhyme matching logic
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .vscode/
│   ├── settings.json       # VS Code configuration
│   └── launch.json         # Debug configuration
├── scripts/
│   ├── setup.ps1           # Initial setup script
│   ├── run.ps1             # Run Streamlit app
│   └── fetch_dict.ps1      # Download dictionary
├── data/                   # Dictionary files (created by setup)
│   └── dict/
│       ├── sr-Latn.dic     # Latin dictionary
│       └── sr.dic          # Cyrillic dictionary
└── tests/
    └── test_rhyme_engine.py # Unit tests
```

## How It Works

1. **Normalization:** Input is transliterated to Latin (if Cyrillic) and normalized
2. **Digraph handling:** Serbian digraphs (nj, lj, dž) are treated as single sounds
3. **Rhyme key:** The algorithm extracts N syllables from the end of each word
4. **Indexing:** All dictionary words are indexed by their rhyme key
5. **Matching:** Words with the same rhyme key are returned, sorted by length similarity

## Running Tests

```powershell
.venv\Scripts\Activate.ps1
python -m unittest tests\test_rhyme_engine.py
```

## Environment Variables

- `RIMER_DICT_PATH`: Override the default dictionary path

Example:
```powershell
$env:RIMER_DICT_PATH="C:\custom\path\sr-Latn.dic"
streamlit run app.py
```

## Licenses and Attribution

This project uses:

- **Serbian Hunspell Dictionary** - [hunspell-sr](https://github.com/grakic/hunspell-sr)
  - Tri-licensed: GPL/LGPL/MPL with CC BY-SA option
  - Source: devbase.net
  
- **SrbAI** - [Serbian-AI-Society/SrbAI](https://github.com/Serbian-AI-Society/SrbAI)
  - License: MIT
  - Used for Cyrillic ↔ Latin transliteration

- **Streamlit** - [streamlit.io](https://streamlit.io/)
  - License: Apache 2.0
  - Web UI framework

## Troubleshooting

**Dictionary not found error:**
- Run `.\scripts\fetch_dict.ps1` manually
- Check that `data\dict\sr-Latn.dic` exists

**Virtual environment issues:**
- Delete `.venv` folder and run `.\scripts\setup.ps1` again

**Streamlit won't start:**
- Make sure the virtual environment is activated
- Try: `.venv\Scripts\Activate.ps1` then `streamlit run app.py`

## Contributing

This is an open-source project. Contributions are welcome!

## Support

For issues, please check:
1. Dictionary is downloaded (`data\dict\sr-Latn.dic` exists)
2. Virtual environment is activated
3. All requirements are installed

---

**Built with ❤️ for the Serbian language community**
