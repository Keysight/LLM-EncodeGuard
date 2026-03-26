"""Prompt Database Module"""

from .baseline_prompts import (
    BASELINE_SYSTEM_PROMPTS,
    BASELINE_USER_PROMPTS,
    get_baseline_prompt_pair,
    get_all_baseline_pairs
)
from .hardened_prompts import (
    HARDENED_SYSTEM_PROMPTS,
    HARDENED_USER_PROMPTS,
    get_hardened_prompt_pair,
    get_all_hardened_pairs
)

__all__ = [
    'BASELINE_SYSTEM_PROMPTS',
    'BASELINE_USER_PROMPTS',
    'get_baseline_prompt_pair',
    'get_all_baseline_pairs',
    'HARDENED_SYSTEM_PROMPTS',
    'HARDENED_USER_PROMPTS',
    'get_hardened_prompt_pair',
    'get_all_hardened_pairs',
]
