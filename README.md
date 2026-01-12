# Anki IELTS Vocabulary Generator 📚

> 🎨 **Vibe Coding Project** - This project was built entirely through AI-assisted "vibe coding" - a collaborative coding session with AI where the focus is on shipping fast and having fun. Expect some rough edges, but it works!

A Python tool to automate the creation of IELTS vocabulary decks for Anki.
It reads vocabulary from a JSON file, automatically generates British English pronunciation audio (using Google TTS), and exports a formatted text file ready for Anki import.

## Features

- 🎧 **Auto-Audio:** Downloads pronunciation (mp3) directly to Anki's media folder.
- 🇬🇧 **British Accent:** Configured for IELTS standard (UK English).
- ⚡ **Smart Import:** Generates Anki-ready text files with correct headers.
- ⚙️ **Configurable:** Easy configuration via `config.json`.
- 🔍 **Auto-Detection:** Automatically finds Anki's media folder on Windows, macOS, and Linux.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/daFoggo/anki-vocabulary-import-generator.git
cd anki-vocabulary-import-generator
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Note Type in Anki (First time only)

Before importing, you need to create a custom Note Type in Anki:

#### Step 1: Create new Note Type

1. Open **Anki**
2. Go to **Tools → Manage Note Types** (or Ctrl+Shift+N)
3. Click **Add**
4. Select **Clone: Basic** → Click **OK**
5. Name it: `IELTS Advanced` → Click **OK**

#### Step 2: Add Fields

1. Select `IELTS Advanced` → Click **Fields...**
2. Rename existing fields:
   - `Front` → `Word`
   - `Back` → `IPA`
3. Click **Add** to create new fields (in order):

| #   | Field Name |
| --- | ---------- |
| 1   | Word       |
| 2   | IPA        |
| 3   | Audio      |
| 4   | Meaning    |
| 5   | Context    |
| 6   | Extra      |

4. Click **Save** → **Close**

#### Step 3: Configure Card Template

1. Select `IELTS Advanced` → Click **Cards...**
2. Replace the templates with:

**Front Template:**

```html
<div class="word">{{Word}}</div>
<div class="ipa">{{IPA}}</div>
{{Audio}}
```

**Back Template:**

```html
{{FrontSide}}
<hr />
<div class="meaning">{{Meaning}}</div>
<div class="context">{{Context}}</div>
<div class="extra">{{Extra}}</div>
```

**Styling:**

```css
.card {
  font-family: Arial, sans-serif;
  font-size: 18px;
  text-align: center;
  padding: 20px;
  line-height: 1.6;
}

.word {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 5px;
}

.ipa {
  font-size: 16px;
  color: gray;
  margin-bottom: 15px;
}

.meaning {
  text-align: left;
  margin-bottom: 15px;
}

.context {
  text-align: left;
  font-style: italic;
  margin-bottom: 10px;
}

.extra {
  text-align: left;
  font-size: 14px;
  color: #666;
}

hr {
  margin: 20px 0;
}
```

3. Click **Save** → **Close** → **Close**

## Usage

### 1. Add vocabulary data

Edit `data/vocab.json` with your vocabulary:

```json
[
  {
    "word": "Example",
    "ipa": "/ɪɡˈzæmpəl/",
    "meaning": "A thing characteristic of its kind.<br><i>(Ví dụ)</i>",
    "context": "This is an <b>example</b> sentence.",
    "extra": "Synonyms: instance, sample",
    "tags": "Topic_General IELTS_Noun"
  }
]
```

#### 💡 Pro Tip: Use AI to generate vocabulary data!

You can use ChatGPT, Claude, Gemini, or any AI to generate vocabulary in the correct JSON format. Just use this prompt:

```
Generate 20 IELTS vocabulary words about [TOPIC] in this JSON format:
[
  {
    "word": "vocabulary word",
    "ipa": "/IPA pronunciation/",
    "meaning": "English definition<br><i>(Vietnamese translation)</i>",
    "context": "Example sentence with <b>word</b> in bold.<br><i>(Vietnamese translation)</i>",
    "extra": "Synonyms: word1, word2",
    "tags": "Topic_[TOPIC] IELTS_[PartOfSpeech]"
  }
]
```

Then paste the AI-generated JSON directly into `data/vocab.json`!

### 2. Run the script

```bash
python main.py
```

### 3. Import to Anki

1. Open **Anki** → **File → Import**
2. Select `output/import_to_anki.txt`
3. Click **Import**

## Configuration

Edit `config.json` to customize:

| Option            | Description                                                   | Default                           |
| ----------------- | ------------------------------------------------------------- | --------------------------------- |
| `anki_media_path` | Path to Anki media folder. Set to `"auto"` for auto-detection | `"auto"`                          |
| `input_file`      | Path to vocabulary JSON file                                  | `"data/vocab.json"`               |
| `output_file`     | Path to output text file                                      | `"output/import_to_anki.txt"`     |
| `deck_name`       | Target deck name in Anki                                      | `"IELTS Preparation::Vocabulary"` |
| `note_type`       | Note type to use                                              | `"IELTS Advanced"`                |
| `tts_lang`        | Language code for TTS                                         | `"en"`                            |
| `tts_tld`         | TLD for accent (see table below)                              | `"co.uk"`                         |

### 🗣️ Accent Configuration

Change `tts_tld` in `config.json` to get different English accents:

| Accent           | `tts_tld` value |
| ---------------- | --------------- |
| 🇬🇧 British (UK)  | `"co.uk"`       |
| 🇺🇸 American (US) | `"com"`         |
| 🇦🇺 Australian    | `"com.au"`      |
| 🇮🇳 Indian        | `"co.in"`       |
| 🇨🇦 Canadian      | `"ca"`          |
| 🇮🇪 Irish         | `"ie"`          |
| 🇿🇦 South African | `"co.za"`       |
| 🇳🇿 New Zealand   | `"co.nz"`       |

**Example:** To use American accent, set:

```json
{
  "tts_tld": "com"
}
```

## Anki Media Path Detection

The script automatically finds Anki's media folder based on official locations:

| OS      | Default Path                                                     |
| ------- | ---------------------------------------------------------------- |
| Windows | `%APPDATA%\Anki2\{Profile}\collection.media`                     |
| macOS   | `~/Library/Application Support/Anki2/{Profile}/collection.media` |
| Linux   | `~/.local/share/Anki2/{Profile}/collection.media`                |

If auto-detection fails, audio files are saved to `output/media/` and you'll need to copy them manually to Anki's `collection.media` folder.

## Vocabulary JSON Format

Each vocabulary item supports the following fields:

| Field     | Description                             | Required |
| --------- | --------------------------------------- | -------- |
| `word`    | The vocabulary word or phrase           | ✅       |
| `ipa`     | IPA pronunciation                       | ❌       |
| `meaning` | Definition (supports HTML)              | ❌       |
| `context` | Example sentence (supports HTML)        | ❌       |
| `extra`   | Additional info (synonyms, notes, etc.) | ❌       |
| `tags`    | Space-separated Anki tags               | ❌       |

## License

MIT License
