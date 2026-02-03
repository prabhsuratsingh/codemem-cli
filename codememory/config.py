from pathlib import Path

CODEMEM_DIR = Path.home() / ".codememory"
DB_PATH = CODEMEM_DIR / "codemem.db"

IMPORTANT_KEYWORDS = {
    "auth", "jwt", "oauth", "token",
    "database", "schema", "api",
    "security", "permission"
}
