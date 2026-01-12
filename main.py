import json
import csv
import os
import time
import platform
import shutil
from pathlib import Path
from gtts import gTTS

# --- TERMINAL COLORS (Optional) ---
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def get_anki_media_path(custom_path):
    """
    Automatically detect the Anki Media folder path based on the operating system.
    
    Anki stores user data in these locations (according to official docs):
    - Windows: %APPDATA%/Anki2/{ProfileName}/collection.media
    - macOS: ~/Library/Application Support/Anki2/{ProfileName}/collection.media
    - Linux: ~/.local/share/Anki2/{ProfileName}/collection.media
            or $XDG_DATA_HOME/Anki2/{ProfileName}/collection.media
            or ~/.var/app/net.ankiweb.Anki/data/Anki2/{ProfileName} (Flatpak)
    
    Each profile folder contains:
    - collection.anki2 (database)
    - collection.media (media folder)
    - backups (backup folder)
    """
    # 1. If user has configured a custom path
    if custom_path and custom_path.lower() != "auto":
        if os.path.exists(custom_path):
            return custom_path
        else:
            print(f"{Colors.WARNING}⚠️  Warning: Path in config does not exist: {custom_path}{Colors.ENDC}")
            return None

    # 2. Auto-detect based on OS
    system = platform.system()
    user_home = Path.home()
    anki_base_paths = []

    if system == "Windows":
        roaming = os.getenv('APPDATA')
        if roaming:
            anki_base_paths = [os.path.join(roaming, "Anki2")]
    elif system == "Darwin":  # macOS
        anki_base_paths = [user_home / "Library/Application Support/Anki2"]
    elif system == "Linux":
        # Check XDG_DATA_HOME first
        xdg_data_home = os.getenv('XDG_DATA_HOME')
        if xdg_data_home:
            anki_base_paths.append(Path(xdg_data_home) / "Anki2")
        # Standard Linux paths
        anki_base_paths.extend([
            user_home / ".local/share/Anki2",
            user_home / ".var/app/net.ankiweb.Anki/data/Anki2"  # Flatpak
        ])

    # 3. Search for profiles within Anki2 folder
    for base_path in anki_base_paths:
        if os.path.exists(base_path):
            # Find all valid profile folders (those containing collection.media)
            try:
                for profile_name in os.listdir(base_path):
                    profile_path = os.path.join(base_path, profile_name)
                    media_path = os.path.join(profile_path, "collection.media")
                    
                    # Skip non-directories and system files
                    if not os.path.isdir(profile_path):
                        continue
                    if profile_name.startswith('.') or profile_name == 'addons21':
                        continue
                    
                    if os.path.exists(media_path):
                        return media_path
            except PermissionError:
                continue
    
    return None


def main():
    print(f"{Colors.HEADER}=== ANKI IELTS GENERATOR START ==={Colors.ENDC}")

    # 1. Load Config
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"{Colors.FAIL}❌ Error: Config file '{config_path}' not found{Colors.ENDC}")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # 2. Determine audio save location
    anki_path = get_anki_media_path(config.get("anki_media_path"))
    
    save_to_local = False
    if anki_path:
        media_save_path = anki_path
        print(f"{Colors.OKGREEN}✅ Found Anki Media Folder:{Colors.ENDC} {media_save_path}")
    else:
        # Fallback: Save to project's output folder
        save_to_local = True
        media_save_path = os.path.join("output", "media")
        os.makedirs(media_save_path, exist_ok=True)
        print(f"{Colors.WARNING}⚠️  Anki not found. Audio will be saved to:{Colors.ENDC} {media_save_path}")

    # 3. Read input data
    input_file = config.get("input_file", "data/vocab.json")
    if not os.path.exists(input_file):
        print(f"{Colors.FAIL}❌ Error: Data file not found at '{input_file}'{Colors.ENDC}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        vocab_list = json.load(f)

    # 4. Main processing
    export_data = []
    print(f"\n🚀 Processing {len(vocab_list)} vocabulary items...\n")

    for index, item in enumerate(vocab_list, 1):
        word = item.get('word', '').strip()
        if not word: continue

        # Create safe filename (remove special characters)
        safe_filename = "".join([c if c.isalnum() else "_" for c in word]).lower() + ".mp3"
        full_audio_path = os.path.join(media_save_path, safe_filename)
        
        # Download audio (if not already exists)
        status_icon = "⏭️ "
        if not os.path.exists(full_audio_path):
            try:
                # Call Google TTS API
                tts = gTTS(
                    text=word, 
                    lang=config.get("tts_lang", "en"), 
                    tld=config.get("tts_tld", "co.uk")
                )
                tts.save(full_audio_path)
                status_icon = "⬇️ "
                time.sleep(0.3)  # Polite delay to avoid rate limiting
            except Exception as e:
                print(f"   {Colors.FAIL}❌ Failed to download '{word}': {e}{Colors.ENDC}")
                status_icon = "❌ "
        
        print(f"   [{index}/{len(vocab_list)}] {status_icon} {word}")

        # Prepare data for export file
        anki_sound_tag = f"[sound:{safe_filename}]"
        row = [
            word,
            item.get('ipa', ''),
            anki_sound_tag,
            item.get('meaning', ''),
            item.get('context', ''),
            item.get('extra', ''),
            item.get('tags', '')
        ]
        export_data.append(row)

    # 5. Export TXT file
    output_file = config.get("output_file", "output/import_to_anki.txt")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, mode='w', encoding='utf-8', newline='') as file:
        # Write Anki-standard headers
        file.write("#separator:Tab\n")
        file.write("#html:true\n")
        file.write(f"#notetype:{config.get('note_type', 'Basic')}\n")
        file.write(f"#deck:{config.get('deck_name', 'Default')}\n")
        file.write("#tags column:7\n")
        
        writer = csv.writer(file, delimiter='\t')
        writer.writerows(export_data)

    print(f"\n{Colors.HEADER}=== COMPLETE ==={Colors.ENDC}")
    print(f"📄 Import file created at: {Colors.OKBLUE}{output_file}{Colors.ENDC}")
    
    if save_to_local:
        print(f"{Colors.WARNING}⚠️  IMPORTANT: You need to manually copy all files from 'output/media' to Anki's 'collection.media' folder before importing!{Colors.ENDC}")
    else:
        print(f"{Colors.OKGREEN}✨ Audio files have been automatically added to Anki. Just import the text file and you're done!{Colors.ENDC}")


if __name__ == "__main__":
    main()