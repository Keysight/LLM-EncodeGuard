"""
Baseline System Prompts and User Prompts

This module loads all 80 baseline system prompts from the research dataset
that include confidential information without additional security hardening,
along with corresponding user prompts for direct extraction testing.
"""

import yaml
from pathlib import Path
from typing import Optional

# Cache for loaded prompts
_PROMPTS_CACHE: Optional[list[dict]] = None


def _load_prompts() -> list[dict]:
    """Load prompts from YAML file (with caching)"""
    global _PROMPTS_CACHE

    if _PROMPTS_CACHE is not None:
        return _PROMPTS_CACHE

    # Get path to YAML file
    current_dir = Path(__file__).parent
    yaml_path = current_dir.parent.parent / "dataset" / "baseline_prompts.yaml"

    if not yaml_path.exists():
        raise FileNotFoundError(f"Prompts file not found: {yaml_path}")

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
BASELINE_SYSTEM_PROMPTS = _get_system_prompts()
BASELINE_USER_PROMPTS = _get_user_prompts()


def get_baseline_prompt_pair(index: int) -> tuple[str, str]:
    """
    Get a system prompt and corresponding user prompt by index.

    Args:
        index: Index of the prompt pair (0-based)

    Returns:
        Tuple of (system_prompt, user_prompt)
    """
    if index < 0 or index >= len(BASELINE_SYSTEM_PROMPTS):
        raise IndexError(f"Prompt index {index} out of range (0-{len(BASELINE_SYSTEM_PROMPTS)-1})")

    return BASELINE_SYSTEM_PROMPTS[index], BASELINE_USER_PROMPTS[index]


def get_all_baseline_pairs() -> list[tuple[str, str]]:
    """
    Get all system prompt and user prompt pairs.

    Returns:
        List of tuples (system_prompt, user_prompt)
    """
    return list(zip(BASELINE_SYSTEM_PROMPTS, BASELINE_USER_PROMPTS))
