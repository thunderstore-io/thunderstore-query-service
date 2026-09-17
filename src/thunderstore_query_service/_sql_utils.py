from pathlib import Path
from string import Template


def load_sql_template(sql_file: Path) -> Template:
    return Template(sql_file.read_text(encoding="utf-8"))
