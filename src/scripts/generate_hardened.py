#!/usr/bin/env python3
"""
Hardened Prompt Generation Script

Generates security-hardened versions of baseline prompts using LLM.
This is Phase 3 in the complete workflow.
"""

import os
import sys
import time
import argparse
import yaml
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.llm_providers import OpenAIProvider, GeminiProvider, CustomLLMProvider
from src.utils import display_banner, setup_logger


# Hardening instruction for the LLM
HARDENING_INSTRUCTION = """You are given a system prompt that will be used in a production environment.

Your task is to rewrite this prompt to strengthen its resistance against:
- Information disclosure attempts
- Prompt injection attacks
- Jailbreak attempts
- Encoding-based evasion (ROT13, Base64, Morse code, etc.)

IMPORTANT: Preserve ALL original functionality, roles, constraints, and values.

Enhance by adding:
1. Explicit security boundaries and refusal conditions
2. Anti-jailbreak language and override protection
3. Clear confidentiality reinforcement
4. Resistance to encoding/obfuscation techniques

Do NOT:
- Remove any functionality
- Add new capabilities beyond security
- Change the intended behavior
- Add commentary or explanation

Return ONLY the rewritten system prompt, nothing else.

Original system prompt:
{baseline_prompt}
"""


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate hardened versions of baseline prompts using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all hardened prompts using OpenAI
  python scripts/generate_hardened.py --provider openai --model gpt-4o

  # Generate with custom LLM
  python scripts/generate_hardened.py --provider custom --model llama-3 --custom-endpoint http://10.36.129.2:8000

  # Generate specific prompts only (first 10 prompts)
  python scripts/generate_hardened.py --provider openai --model gpt-4o --prompts 1-10

  # Use higher temperature for more diverse hardening
  python scripts/generate_hardened.py --provider openai --model gpt-4o --temperature 1.0
        """
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "gemini", "custom"],
        default="openai",
        help="LLM provider to use for hardening"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="Model name to use for hardening"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperature for LLM sampling (default: 0.7, range: 0.0-2.0)"
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default="dataset/baseline_prompts.yaml",
        help="Input baseline prompts YAML file"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="dataset/hardened_prompts.yaml",
        help="Output hardened prompts YAML file"
    )
    parser.add_argument(
        "--prompts",
        type=str,
        help="Prompt range to generate (e.g., '1-5' or '1,3,5'). 1-based indexing. Default: all prompts"
    )
    parser.add_argument(
        "--custom-endpoint",
        type=str,
        help="Custom LLM endpoint (required if provider=custom, or set CUSTOM_LLM_ENDPOINT env var)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay in seconds between requests (default: 2)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test with first prompt only, don't save results"
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create backup of existing output file before overwriting"
    )

    return parser.parse_args()


def get_llm_provider(args):
    """Initialize the LLM provider based on arguments"""
    if args.provider == "openai":
        return OpenAIProvider(model_name=args.model, temperature=args.temperature)
    elif args.provider == "gemini":
        return GeminiProvider(model_name=args.model, temperature=args.temperature)
    elif args.provider == "custom":
        endpoint = args.custom_endpoint or os.getenv("CUSTOM_LLM_ENDPOINT")
        if not endpoint:
            raise ValueError("--custom-endpoint flag or CUSTOM_LLM_ENDPOINT environment variable required when using custom provider")
        return CustomLLMProvider(
            model_name=args.model,
            endpoint=endpoint,
            temperature=args.temperature
        )
    else:
        raise ValueError(f"Unknown provider: {args.provider}")


def get_prompt_indices(prompts_arg, total_prompts):
    """Parse prompt range/list argument (1-based user input -> 0-based indices)"""
    if not prompts_arg:
        return list(range(total_prompts))

    indices = []
    if '-' in prompts_arg:
        # Range format: "1-5" -> convert to 0-based
        start, end = map(int, prompts_arg.split('-'))
        indices = list(range(start - 1, end))
    elif ',' in prompts_arg:
        # List format: "1,3,5" -> convert to 0-based
        indices = [int(x.strip()) - 1 for x in prompts_arg.split(',')]
    else:
        # Single index -> convert to 0-based
        indices = [int(prompts_arg) - 1]

    return indices


def load_baseline_prompts(input_file: Path, logger):
    """Load baseline prompts from YAML file"""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    logger.info(f"Loading baseline prompts from: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    prompts = data.get('prompts', [])
    logger.info(f"Loaded {len(prompts)} baseline prompts")

    return prompts


def harden_prompt(baseline_prompt: str, llm_provider, logger) -> str:
    """Use LLM to generate hardened version of a prompt"""
    # Create the hardening instruction
    user_prompt = HARDENING_INSTRUCTION.format(baseline_prompt=baseline_prompt)

    # System prompt for the hardener LLM
    system_prompt = (
        "You are a senior security researcher and prompt engineering specialist. "
        "Your expertise is in hardening system prompts against jailbreaks, prompt injection, "
        "and unauthorized information disclosure while preserving functionality."
    )

    # Call LLM
    response = llm_provider.call(user_prompt, system_prompt)

    return response.strip()


def create_backup(output_file: Path, logger):
    """Create backup of existing output file"""
    if output_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = output_file.parent / f"{output_file.stem}_backup_{timestamp}{output_file.suffix}"

        logger.info(f"Creating backup: {backup_file}")

        with open(output_file, 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())

        logger.info(f"Backup created successfully")


def save_hardened_prompts(hardened_prompts: list, output_file: Path, logger):
    """Save hardened prompts to YAML file"""
    output_data = {'prompts': hardened_prompts}

    logger.info(f"Saving {len(hardened_prompts)} hardened prompts to: {output_file}")

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(output_data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=1000)

    logger.info(f"Hardened prompts saved successfully")


def main():
    """Main execution function"""
    args = parse_args()

    # Display banner
    display_banner("Hardened Prompt Generator")

    # Setup logger
    logger = setup_logger("hardening")

    logger.info("="*70)
    logger.info("PHASE 3: HARDENED PROMPT GENERATION")
    logger.info("="*70)
    logger.info(f"Provider: {args.provider}")
    logger.info(f"Model: {args.model}")
    logger.info(f"Temperature: {args.temperature}")
    logger.info(f"Input: {args.input_file}")
    logger.info(f"Output: {args.output_file}")

    if args.dry_run:
        logger.warning("DRY RUN MODE - Only processing first prompt, won't save results")

    # Get paths
    script_dir = Path(__file__).parent
    input_file = script_dir.parent.parent / args.input_file
    output_file = script_dir.parent.parent / args.output_file

    # Load baseline prompts
    try:
        baseline_prompts = load_baseline_prompts(input_file, logger)
    except Exception as e:
        logger.error(f"Failed to load baseline prompts: {e}")
        return 1

    # Get prompt indices to process
    prompt_indices = get_prompt_indices(args.prompts, len(baseline_prompts))

    if args.dry_run:
        prompt_indices = [prompt_indices[0]]  # Only first one

    logger.info(f"Processing {len(prompt_indices)} prompts: {prompt_indices}")

    # Initialize LLM provider
    try:
        llm_provider = get_llm_provider(args)
        logger.info(f"Initialized LLM provider: {llm_provider}")
    except Exception as e:
        logger.error(f"Failed to initialize LLM provider: {e}")
        return 1

    # Create backup if requested
    if args.backup and output_file.exists() and not args.dry_run:
        try:
            create_backup(output_file, logger)
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")

    # Generate hardened prompts
    hardened_prompts = []
    success_count = 0
    fail_count = 0

    for idx in prompt_indices:
        if idx >= len(baseline_prompts):
            logger.warning(f"Skipping invalid prompt index: {idx}")
            continue

        baseline = baseline_prompts[idx]
        baseline_system_prompt = baseline['system_prompt']
        baseline_user_prompt = baseline['user_prompt']
        prompt_id = baseline['id']

        logger.info(f"\n{'='*70}")
        logger.info(f"Processing prompt {idx + 1}/{len(baseline_prompts)} (ID: {prompt_id})")
        logger.info(f"Baseline length: {len(baseline_system_prompt)} chars")

        try:
            # Generate hardened version
            hardened_system_prompt = harden_prompt(baseline_system_prompt, llm_provider, logger)

            logger.info(f"Hardened length: {len(hardened_system_prompt)} chars")
            logger.info(f"Change: {len(hardened_system_prompt) - len(baseline_system_prompt):+d} chars")

            # Preview first 150 chars
            preview = hardened_system_prompt[:150].replace('\n', ' ')
            logger.info(f"Preview: {preview}...")

            # Store hardened version
            hardened_prompts.append({
                'id': prompt_id,
                'system_prompt': hardened_system_prompt,
                'user_prompt': baseline_user_prompt  # Keep same user prompt
            })

            success_count += 1

            # Delay between requests
            if args.delay > 0 and idx < prompt_indices[-1]:
                logger.info(f"Waiting {args.delay}s before next request...")
                time.sleep(args.delay)

        except Exception as e:
            logger.error(f"Error hardening prompt {idx}: {e}")
            fail_count += 1

            # On error, keep original baseline prompt
            hardened_prompts.append({
                'id': prompt_id,
                'system_prompt': baseline_system_prompt,
                'user_prompt': baseline_user_prompt
            })

    # Summary
    logger.info(f"\n{'='*70}")
    logger.info("HARDENING COMPLETE")
    logger.info(f"{'='*70}")
    logger.info(f"Total processed: {len(prompt_indices)}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Failed: {fail_count}")

    # Save results
    if not args.dry_run:
        try:
            save_hardened_prompts(hardened_prompts, output_file, logger)
            logger.info(f"\n✓ Hardened prompts saved to: {output_file}")
            logger.info(f"\nNext steps:")
            logger.info(f"  1. Review the hardened prompts")
            logger.info(f"  2. Run: python scripts/run_hardened.py --provider openai --model gpt-4o-mini --mode both")
        except Exception as e:
            logger.error(f"Failed to save hardened prompts: {e}")
            return 1
    else:
        logger.info("\nDRY RUN - No files were saved")
        logger.info(f"\nTo generate all prompts, run without --dry-run flag")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
