from pathlib import Path
import tomllib

CODEMEM_DIR = Path.home() / ".codememory"
DB_PATH = CODEMEM_DIR / "codemem.db"
CONFIG_PATH = CODEMEM_DIR / "config.toml"

IMPORTANT_KEYWORDS = {
    "auth", "jwt", "oauth", "token",
    "database", "schema", "api",
    "security", "permission",
}

def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise RuntimeError(
            "CodeMemory not initialized.\n"
            "Run: codemem init"
        )

    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)
