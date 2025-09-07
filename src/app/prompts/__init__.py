import os
from pathlib import Path

def load_prompt(prompt_name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompts_dir = Path(__file__).parent
    prompt_file = prompts_dir / f"{prompt_name}.md"
    
    if prompt_file.exists():
        return prompt_file.read_text().strip()
    else:
        raise FileNotFoundError(f"Prompt file {prompt_name}.md not found")
