import argparse
import os
import re
import shutil
import sys
from pathlib import Path


def parse_arguments() -> None:
    parser = argparse.ArgumentParser(
        description="""\
Utility tool to add a .vscode folder with the configuration files to ease work with \
isaac sim.
This will add .vscode to your current working directory. """
    )
    parser.parse_args()


def main() -> None:
    parse_arguments()
    if "ISAACSIM_PATH" not in os.environ:
        print("Define `ISAACSIM_PATH` variable before running this script")
        sys.exit(1)

    # There are currently 3 ways of installing isaacsim
    # - Downloading and running binaries
    # - Compiling repo
    # - Installing python package from pypi
    #
    # Currently only the second option is supported (but it wouldn't be hard to also support
    # the 1st one).
    # To check that we are in the second case, we check for the presence of the `_build`
    # folder in the `ISAAC_SIM` path
    build_path = (
        Path(os.environ["ISAACSIM_PATH"]) / "_build/linux-x86_64/release"
    ).resolve()
    if not build_path.exists():
        print(
            "Only supported isaac sim install type is locally compiled.\n If you want to support more installation type, consider contributing to this script ;)"
        )
        sys.exit(1)

    dot_vscode_path = Path.cwd() / ".vscode"
    if dot_vscode_path.exists():
        print(f"{dot_vscode_path} already exists in the current directory.")
        sys.exit(1)

    shutil.copytree(build_path / ".vscode", dot_vscode_path)
    for file_path in dot_vscode_path.iterdir():
        content = file_path.read_text()
        content = content.replace("${workspaceFolder}", str(build_path))

        if file_path.name == "settings.json":
            # cannot use json library because the file has comments
            def replace_each_line(match: re.Match[str]) -> str:
                return match.group(1) + re.sub(
                    r'"([^"]+?)"', rf'"{str(build_path)}/\1"', match.group(2)
                )

            content = re.sub(
                r'("python\.analysis\.extraPaths"\s*:\s*)(\[.*?\])',
                replace_each_line,
                content,
                flags=re.DOTALL,
            )

            # TODO: Add ros path

        file_path.write_text(content)


if __name__ == "__main__":
    main()
