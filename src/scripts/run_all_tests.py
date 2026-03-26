#!/usr/bin/env python3
"""
Master Test Runner Script

Runs the complete test suite in sequence:
1. Baseline Testing (direct extraction)
2. Attack Testing (with evasion techniques)
3. Hardened Baseline Testing
4. Hardened Attack Testing

All individual scripts remain operational and can be run independently.
"""

import os
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.utils import display_banner, setup_logger


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run complete LLM security test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: Test ALL providers and models from config
  python run_all_tests.py

  # Test single specific model
  python run_all_tests.py --provider openai --model gpt-4o-mini

  # Test all models for one provider
  python run_all_tests.py --provider openai

  # Test specific prompts only (first 10 prompts)
  python run_all_tests.py --provider openai --model gpt-4o-mini --prompts 1-10

  # Custom techniques and temperature
  python run_all_tests.py --provider gemini --model gemini-2.0-flash-001 --techniques "rot13,base64" --temperature 0.5

  # Skip specific test phases
  python run_all_tests.py --provider openai --model gpt-4o-mini --skip-baseline --skip-hardened-attack
        """
    )

    # Provider selection
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "gemini", "custom", "grok"],
        help="LLM provider to test (default: all providers from config)"
    )

    # Model selection
    parser.add_argument(
        "--model",
        type=str,
        help="Model name to test (required if --all-models not used)"
    )
    parser.add_argument(
        "--all-models",
        action="store_true",
        help="Test all models for the specified provider from config/llm_models.yaml"
    )
    parser.add_argument(
        "--all-providers",
        action="store_true",
        help="Test all models from all providers in config/llm_models.yaml (ignores --provider)"
    )

    # Test configuration
    parser.add_argument(
        "--prompts",
        type=str,
        help="Prompt range to test (e.g., '1-5' or '1,3,5'). 1-based indexing. Default: all 80 prompts"
    )
    parser.add_argument(
        "--techniques",
        type=str,
        help="Comma-separated list of attack techniques. Default: all 13 techniques"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Temperature for LLM sampling (default: 0.0)"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=0,
        help="Delay in seconds between requests (default: 0)"
    )

    # Output configuration
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Base output directory for results (default: outputs)"
    )

    # Test phase control
    parser.add_argument(
        "--skip-baseline",
        action="store_true",
        help="Skip baseline testing phase"
    )
    parser.add_argument(
        "--skip-attack",
        action="store_true",
        help="Skip attack testing phase"
    )
    parser.add_argument(
        "--generate-hardened",
        action="store_true",
        help="Generate hardened prompts using LLM before testing (Phase 3)"
    )
    parser.add_argument(
        "--hardening-model",
        type=str,
        default="gpt-4o",
        help="Model to use for hardening generation (default: gpt-4o)"
    )
    parser.add_argument(
        "--skip-hardened-baseline",
        action="store_true",
        help="Skip hardened baseline testing phase"
    )
    parser.add_argument(
        "--skip-hardened-attack",
        action="store_true",
        help="Skip hardened attack testing phase"
    )

    # Hardened prompt mode
    parser.add_argument(
        "--hardened-mode",
        type=str,
        choices=["all", "even", "odd"],
        default="all",
        help="Which hardened prompts to test (default: all)"
    )

    # Custom endpoint
    parser.add_argument(
        "--custom-endpoint",
        type=str,
        help="Custom LLM endpoint (required if provider=custom, or set CUSTOM_LLM_ENDPOINT env var)"
    )

    # Configuration files
    parser.add_argument(
        "--models-config",
        type=str,
        default="config/llm_models.yaml",
        help="Path to LLM models configuration file"
    )

    return parser.parse_args()


def run_phase(phase_name: str, command: str, logger):
    """
    Run a test phase using subprocess.

    Args:
        phase_name: Name of the test phase
        command: Command to execute
        logger: Logger instance

    Returns:
        True if successful, False otherwise
    """
    import subprocess

    logger.info(f"\n{'='*80}")
    logger.info(f"PHASE: {phase_name}")
    logger.info(f"{'='*80}")
    logger.info(f"Command: {command}\n")

    start_time = time.time()

    try:
        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )

        elapsed = time.time() - start_time
        logger.info(f"\n✓ {phase_name} completed successfully in {elapsed:.1f}s")
        return True

    except subprocess.CalledProcessError as e:
        elapsed = time.time() - start_time
        logger.error(f"\n✗ {phase_name} failed after {elapsed:.1f}s")
        logger.error(f"Error: {e}")
        return False


def build_command(script_name: str, args, phase_specific_args: dict = None) -> str:
    """
    Build command line for a test script.

    Args:
        script_name: Name of the script to run
        args: Parsed command line arguments
        phase_specific_args: Additional phase-specific arguments

    Returns:
        Command string
    """
    script_path = Path(__file__).parent / script_name

    cmd_parts = [
        sys.executable,
        str(script_path),
        f"--provider {args.provider}"
    ]

    # Model selection
    if args.all_models:
        cmd_parts.append("--all-models")
    else:
        cmd_parts.append(f"--model {args.model}")

    # Optional arguments
    if args.prompts:
        cmd_parts.append(f"--prompts '{args.prompts}'")

    if args.techniques and "attack" in script_name:
        cmd_parts.append(f"--techniques '{args.techniques}'")

    if args.temperature != 0.0:
        cmd_parts.append(f"--temperature {args.temperature}")

    if args.delay > 0:
        cmd_parts.append(f"--delay {args.delay}")

    if args.custom_endpoint:
        cmd_parts.append(f"--custom-endpoint '{args.custom_endpoint}'")

    if args.models_config != "config/llm_models.yaml":
        cmd_parts.append(f"--models-config '{args.models_config}'")

    # Add phase-specific arguments
    if phase_specific_args:
        for key, value in phase_specific_args.items():
            if value is True:
                cmd_parts.append(f"--{key}")
            elif value is not None:
                cmd_parts.append(f"--{key} {value}")

    return " ".join(cmd_parts)


def main():
    """Main execution function"""
    args = parse_args()

    # Display banner
    display_banner("LLM-EncodeGuard")

    # Setup logger
    logger = setup_logger("test_suite")

    # Determine which providers and models to test
    providers_and_models = []

    # Default behavior: if no provider/model specified, test all
    if not args.provider and not args.model and not args.all_models and not args.all_providers:
        args.all_providers = True

    if args.all_providers or (not args.provider and not args.model):
        # Load all providers and their models from config
        try:
            config_path = Path(__file__).parent.parent / args.models_config
            with open(config_path, 'r') as f:
                import yaml
                all_models_config = yaml.safe_load(f)

            for provider, models in all_models_config.items():
                if models:  # Skip if no models for this provider
                    # Handle dict format (custom provider with endpoints) vs list format
                    if isinstance(models, dict):
                        for model, endpoint in models.items():
                            providers_and_models.append((provider, model, endpoint))
                    else:
                        for model in models:
                            providers_and_models.append((provider, model, None))

            logger.info(f"Running complete test suite for ALL providers and models")
            logger.info(f"Total: {len(providers_and_models)} models across {len(all_models_config)} providers")

        except Exception as e:
            logger.error(f"Failed to load models from config: {e}")
            return 1

    elif args.all_models or (args.provider and not args.model):
        # Load all models for specified provider
        if not args.provider:
            logger.error("Error: --provider required when using --all-models")
            return 1

        try:
            config_path = Path(__file__).parent.parent / args.models_config
            with open(config_path, 'r') as f:
                import yaml
                all_models_config = yaml.safe_load(f)

            if args.provider not in all_models_config:
                logger.error(f"Provider '{args.provider}' not found in config")
                return 1

            models = all_models_config[args.provider]
            if not models:
                logger.error(f"No models found for provider '{args.provider}'")
                return 1

            # Handle dict format (custom provider with endpoints) vs list format
            if isinstance(models, dict):
                for model, endpoint in models.items():
                    providers_and_models.append((args.provider, model, endpoint))
            else:
                for model in models:
                    providers_and_models.append((args.provider, model, None))

            logger.info(f"Running complete test suite for ALL {args.provider} models")
            logger.info(f"Total: {len(providers_and_models)} models")

        except Exception as e:
            logger.error(f"Failed to load models from config: {e}")
            return 1
    elif args.provider and args.model:
        # Single specific model
        providers_and_models.append((args.provider, args.model, None))
        logger.info(f"Running complete test suite for model: {args.provider}/{args.model}")
    else:
        logger.error("Error: Invalid combination of arguments")
        return 1

    # Test configuration summary
    logger.info(f"\nTest Configuration:")
    if args.all_providers:
        logger.info(f"  Providers: All from config")
        logger.info(f"  Models: All from config ({len(providers_and_models)} total)")
    elif args.provider:
        logger.info(f"  Provider: {args.provider}")
        if args.model:
            logger.info(f"  Model: {args.model}")
        else:
            logger.info(f"  Models: All {args.provider} models ({len(providers_and_models)} total)")
    logger.info(f"  Prompts: {args.prompts if args.prompts else 'All (80)'}")
    logger.info(f"  Techniques: {args.techniques if args.techniques else 'All (13)'}")
    logger.info(f"  Temperature: {args.temperature}")
    logger.info(f"  Output Directory: {args.output_dir}")

    # Test phases
    phases_to_run = []

    if not args.skip_baseline:
        phases_to_run.append(("Baseline Testing", "run_baseline.py", {
            "output-dir": f"{args.output_dir}/baseline"
        }))

    if not args.skip_attack:
        phases_to_run.append(("Attack Testing (Evasion)", "run_attack.py", {
            "output-dir": f"{args.output_dir}/attack"
        }))

    # Phase 3: Generate hardened prompts (optional)
    if args.generate_hardened:
        phases_to_run.append(("Generate Hardened Prompts", "generate_hardened.py", {
            "provider": args.provider,
            "model": args.hardening_model,
            "temperature": "0.7"
        }))

    if not args.skip_hardened_baseline:
        phases_to_run.append(("Hardened Baseline Testing", "run_hardened.py", {
            "output-dir": f"{args.output_dir}/hardened_baseline",
            "mode": "baseline"
        }))

    if not args.skip_hardened_attack:
        phases_to_run.append(("Hardened Attack Testing", "run_hardened.py", {
            "output-dir": f"{args.output_dir}/hardened_attack",
            "mode": "attack"
        }))

    if not phases_to_run:
        logger.error("Error: All test phases are skipped. Nothing to run.")
        return 1

    logger.info(f"\nTest Phases: {len(phases_to_run)}")
    for i, (name, _, _) in enumerate(phases_to_run, 1):
        logger.info(f"  {i}. {name}")

    # Confirmation
    logger.info(f"\n{'='*80}")
    logger.info("Starting test execution...")
    logger.info(f"{'='*80}\n")

    # Track results
    all_results = []
    overall_start = time.time()

    # Run tests for each provider/model combination
    for provider_idx, model_info in enumerate(providers_and_models, 1):
        provider, model, endpoint = model_info
        logger.info(f"\n{'='*80}")
        logger.info(f"TESTING MODEL {provider_idx}/{len(providers_and_models)}: {provider}/{model}")
        logger.info(f"{'='*80}\n")

        # Temporarily override provider, model, and endpoint for this iteration
        original_provider = args.provider
        original_model = args.model
        original_endpoint = args.custom_endpoint
        args.provider = provider
        args.model = model
        if endpoint:
            args.custom_endpoint = endpoint

        results_for_model = []

        # Run each phase for this model
        for phase_name, script_name, phase_args in phases_to_run:
            command = build_command(script_name, args, phase_args)
            success = run_phase(f"{phase_name} [{provider}/{model}]", command, logger)

            results_for_model.append({
                "provider": provider,
                "model": model,
                "phase": phase_name,
                "success": success
            })

            # Brief pause between phases
            if success:
                time.sleep(2)

        all_results.extend(results_for_model)

        # Restore original values
        args.provider = original_provider
        args.model = original_model
        args.custom_endpoint = original_endpoint

        # Brief pause between models
        if provider_idx < len(providers_and_models):
            logger.info(f"\nCompleted {provider}/{model}. Moving to next model...\n")
            time.sleep(3)

    # Overall summary
    overall_elapsed = time.time() - overall_start

    logger.info(f"\n{'='*80}")
    logger.info("TEST SUITE COMPLETE")
    logger.info(f"{'='*80}")

    # Results summary
    logger.info(f"\nResults Summary:")
    successful = sum(1 for r in all_results if r["success"])
    total = len(all_results)

    # Group by provider/model
    current_model = None
    for result in all_results:
        model_key = f"{result['provider']}/{result['model']}"
        if model_key != current_model:
            logger.info(f"\n  [{model_key}]")
            current_model = model_key

        status = "✓ PASS" if result["success"] else "✗ FAIL"
        logger.info(f"    {status}: {result['phase']}")

    logger.info(f"\nTotal: {successful}/{total} phases passed")
    logger.info(f"Execution Time: {overall_elapsed:.1f}s ({overall_elapsed/60:.1f} minutes)")

    # Output location
    logger.info(f"\nResults saved in: {args.output_dir}/")
    logger.info(f"  - {args.output_dir}/baseline/")
    logger.info(f"  - {args.output_dir}/attack/")
    logger.info(f"  - {args.output_dir}/hardened_baseline/")
    logger.info(f"  - {args.output_dir}/hardened_attack/")

    # Exit code
    return 0 if successful == total else 1


if __name__ == "__main__":
    sys.exit(main())
