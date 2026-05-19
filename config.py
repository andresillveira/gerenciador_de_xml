import os
import json
from typing import Dict, Any

CONFIG_DIR = os.path.expanduser("~/.gerenciador_xml")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "xml_directory": "",
    "theme": "Sistema"  # "Sistema", "Claro", "Escuro"
}

def load_config() -> Dict[str, Any]:
    """Carrega as configurações locais do arquivo JSON ou retorna os padrões."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
        
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # Garante que todas as chaves padrão existem
            for k, v in DEFAULT_CONFIG.items():
                if k not in config:
                    config[k] = v
            return config
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return DEFAULT_CONFIG

def save_config(config: Dict[str, Any]):
    """Grava as configurações locais em arquivo JSON."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Erro ao gravar configurações: {e}")

def get_xml_directory() -> str:
    return load_config().get("xml_directory", "")

def set_xml_directory(path: str):
    config = load_config()
    config["xml_directory"] = path
    save_config(config)

def get_theme_preference() -> str:
    return load_config().get("theme", "Sistema")

def set_theme_preference(theme: str):
    config = load_config()
    config["theme"] = theme
    save_config(config)
