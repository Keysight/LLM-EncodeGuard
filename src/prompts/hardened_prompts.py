"""
Hardened System Prompts and User Prompts

This module loads improved system prompts with additional security measures
to resist prompt injection and information extraction attacks.
"""

import yaml
from pathlib import Path
from typing import Optional

# Cache for loaded prompts
_PROMPTS_CACHE: Optional[list[dict]] = None


def _load_prompts() -> list[dict]:
    """Load hardened prompts from YAML file (with caching)"""
    global _PROMPTS_CACHE

    if _PROMPTS_CACHE is not None:
        return _PROMPTS_CACHE

    # Get path to YAML file
    current_dir = Path(__file__).parent
    yaml_path = current_dir.parent.parent / "dataset" / "hardened_prompts.yaml"

    if not yaml_path.exists():
        raise FileNotFoundError(f"Hardened prompts file not found: {yaml_path}")

    # Load YAML
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    _PROMPTS_CACHE = data['prompts']
    return _PROMPTS_CACHE


def _get_system_prompts() -> list[str]:
    """Extract system prompts from loaded data"""
    prompts = _load_prompts()
    return [p['system_prompt'] for p in prompts]


def _get_user_prompts() -> list[str]:
    """Extract user prompts from loaded data"""
    prompts = _load_prompts()
    return [p['user_prompt'] for p in prompts]


# Expose as module-level variables for backward compatibility
HARDENED_SYSTEM_PROMPTS = _get_system_prompts()
HARDENED_USER_PROMPTS = _get_user_prompts()


def get_hardened_prompt_pair(index: int) -> tuple[str, str]:
    """
    Get a hardened system prompt and corresponding user prompt by index.

    Args:
        index: Index of the prompt pair (0-based)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    if index < 0 or index >= len(HARDENED_SYSTEM_PROMPTS):
        raise IndexError(f"Prompt index {index} out of range (0-{len(HARDENED_SYSTEM_PROMPTS)-1})")

    return HARDENED_SYSTEM_PROMPTS[index], HARDENED_USER_PROMPTS[index]


def get_all_hardened_pairs() -> list[tuple[str, str]]:
    """
    Get all hardened system prompt and user prompt pairs.

    Returns:
        List of tuples (system_prompt, user_prompt)
    """
    return list(zip(HARDENED_SYSTEM_PROMPTS, HARDENED_USER_PROMPTS))
