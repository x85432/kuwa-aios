import argparse
import subprocess
import os
import sys
from pathlib import Path
from typing import List

# Define source files and output paths based on platform (relative to project root).
platforms = ["windows", "windows-cu118", "windows-ipex-llm", "docker", "docker-cu118"]
common_sources = [
    "src/executor/pyproject.toml",
    "src/kernel/pyproject.toml",
    "src/library/client/pyproject.toml",
    "src/library/rag/pyproject.toml",
    "src/executor/agent/requirements.in",
    "src/executor/docqa/requirements.in",
    "src/executor/image_generation/requirements.in",
    "src/executor/speech_recognition/requirements.in",
    "src/executor/uploader/requirements.in",
    "src/bot/text-to-cad/requirements.in",
    "src/toolchain/requirements.in",
    "src/tools/requirements.in",
    # "src/executor/mcp/requirements.in",
    # "src/executor/requirements.in",
    # "src/kernel/requirements.in",
    # "src/library/rag/requirements.in",
]  # Shared dependency across platforms
platform_sources = {
    "windows": ["windows/src/version_patch/cpu/windows/src/requirements.in"],
    "windows-cu118": [
        "windows/src/version_patch/11.8/windows/src/requirements.in",
    ],
    "windows-ipex-llm": [
        "windows/src/version_patch/ipex-llm/windows/src/requirements.in",
    ],
    "docker": [],
    "docker-cu118": [],
}
output_paths = {
    "windows": "windows/src/version_patch/cpu/windows/src/requirements.txt.lock",
    "windows-cu118": "windows/src/version_patch/11.8/windows/src/requirements.txt.lock",
    "windows-ipex-llm": "windows/src/version_patch/ipex-llm/windows/src/requirements.txt.lock",
    "docker": "/dev/null",
    "docker-cu118": "/dev/null",
}
cmd_opts = ["--color", "always", "--annotation-style=line"]


def compile_requirements(
    platform: str, extra_dependencies: List | None = None, dry_run: bool = False
):
    """
    Compiles requirements.txt using uv pip compile based on the specified platform.

    Args:
        platform (str): The target platform (Windows, Windows-CUDA, Docker, Docker-CUDA).
    """

    if platform not in platform_sources:
        print(f"Error: Invalid platform: {platform}")
        sys.exit(1)

    source_files = common_sources + platform_sources[platform]
    if extra_dependencies is not None:
        source_files += extra_dependencies
    output_file = str(Path(output_paths[platform]))

    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the uv pip compile command
    source_files = [str(Path(s)) for s in source_files]
    command = [
        "uv",
        "pip",
        "compile",
        *source_files,
        "-o",
        output_file,
        *cmd_opts,
    ]  # Use -o for output file.

    print(f"Compiling requirements for {platform} using command: {' '.join(command)}")

    if dry_run:
        print("Dry run specified. Exiting.")
        return

    try:
        # Execute the command
        result = subprocess.run(
            command, capture_output=True, text=True, check=True
        )  # check=True raises an exception on non-zero exit code.
        print(result.stdout)

        print(f"Successfully compiled requirements to {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error during compilation:")
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: uv is not installed or not in your PATH.")
        print("Please install uv: pip install uv")
        sys.exit(1)


def main():
    """
    Main function to parse arguments and call the compilation function.
    """
    parser = argparse.ArgumentParser(
        description="Lock Python environment and compile to requirements.txt using uv pip compile."
    )
    all_platform_placeholder = "all"
    parser.add_argument(
        "--platform",
        choices=[all_platform_placeholder, *platforms],
        default=all_platform_placeholder,
        const=all_platform_placeholder,
        nargs="?",
        help="Target platform for compilation.",
    )
    parser.add_argument(
        "extra_dependencies",
        nargs="*",
        # default=[],
        help="Extract dependencies to add.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the command but not execute it.",
    )

    args = parser.parse_args()

    target_platforms = [args.platform]
    if args.platform == all_platform_placeholder:
        target_platforms = platforms.copy()
    for platform in target_platforms:
        compile_requirements(
            platform, extra_dependencies=args.extra_dependencies, dry_run=args.dry_run
        )


if __name__ == "__main__":
    # Set current working directory to project root
    os.chdir(os.path.dirname(os.path.abspath(Path(__file__).parent.parent)))
    print(f"Current working directory: {os.getcwd()}")
    main()
