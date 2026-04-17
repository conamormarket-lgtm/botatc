import json
import os

CONFIG_FILE = 'bots_config.json'

def _load_config():
    if not os.path.exists(CONFIG_FILE):
        prompt_base = "Eres María, la asistente virtual de Wala..."
        try:
            if os.path.exists('guia_respuestas.md'):
                with open('guia_respuestas.md', 'r', encoding='utf-8') as mf:
                    prompt_base = mf.read()
        except:
            pass
            
        default_data = {
            "bots": {
                "bot_wala": {
                    "name": "Wala Principal",
                    "is_active": True,
                    "prompt": prompt_base
                }
            },
            "lines_mapping": {
                "principal": "bot_wala"
            }
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
        return default_data
        
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_bot_for_line(line_id: str) -> str | None:
    """Devuelve el ID del bot asignado a una línea, o None si atiende un humano."""
    config = _load_config()
    return config.get("lines_mapping", {}).get(line_id)

def set_bot_for_line(line_id: str, bot_id: str | None):
    config = _load_config()
    if "lines_mapping" not in config:
        config["lines_mapping"] = {}
    config["lines_mapping"][line_id] = bot_id
    _save_config(config)

def is_bot_active(bot_id: str) -> bool:
    config = _load_config()
    bot = config.get("bots", {}).get(bot_id)
    if bot:
        return bot.get("is_active", False)
    return False

def set_bot_active(bot_id: str, active: bool):
    config = _load_config()
    if bot_id in config.get("bots", {}):
        config["bots"][bot_id]["is_active"] = active
        _save_config(config)

def get_bot_prompt(bot_id: str) -> str:
    config = _load_config()
    bot = config.get("bots", {}).get(bot_id)
    if bot:
        return bot.get("prompt", "")
    return ""

def get_all_bots():
    return _load_config().get("bots", {})
