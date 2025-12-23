import yaml
from pathlib import Path
from typing import Optional


class BasePromptBuilder:

    def __init__(self):
        # Templates are in the same directory as this file
        self.templates_dir = Path(__file__).parent / "templates"

    def _load_template(self, template_name: str, default_template: str) -> str:
        # Try markdown first (.md extension)
        md_path = self.templates_dir / template_name.replace('.yaml', '.md')
        if md_path.exists():
            return md_path.read_text()

        # Fallback to YAML format
        yaml_path = self.templates_dir / template_name
        if yaml_path.exists():
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
            return data.get('template', default_template)

        return default_template

    def _substitute_variables(self, template: str, **variables) -> str:
        result = template
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        return result
