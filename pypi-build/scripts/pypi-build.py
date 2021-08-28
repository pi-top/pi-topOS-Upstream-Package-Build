#!/usr/bin/python3
import click
import os
import subprocess
import shlex
import pathlib
import shutil
import os


@click.command()
###############################
# Command OR sourced function #
###############################
@click.argument(
    "package",
    type=str,
    required=True,
)
@click.option(
    "--options-str",
    type=str,
)
def main(options_str, package):
    """pi-topOS meta-exec."""
    click.echo("Downloading source...")
    proc = subprocess.run(["pypi-download", package], capture_output=True)
    if proc.returncode != 0:
      click.echo("Failed to download source")
      return

    click.echo("Extracting source...")
    tarballFilename = str(proc.stdout).split(" ")[1].split("\\")[0]
    subprocess.run(["tar", "xzf", tarballFilename])

    click.echo("Checking for build dependencies...")
    if os.environ.get('BUILD_DEPENDENCIES'):
      click.echo("Build dependencies found - installing...")
      subprocess.run(["apt-get", "install", "-y"] + BUILD_DEPENDENCIES.split(" "))

    click.echo("Moving source to top-level of repo...")
    currentDir = pathlib.Path(os.getcwd())
    subDir = tarballFilename.replace(".tar.gz", "")
    for f in currentDir.rglob(f"{subDir}/*"):
        shutil.move(os.path.join(currentDir, subDir, f), currentDir)

    click.echo("Moving source to top-level of repo...")
    subprocess.run(["ls", currentDir])

    patchFilePath = pathlib.Path(os.path.join(currentDir, "pypi-build", "patches", f"{package}.patch"))
    print(f"Looking for patch: {patchFilePath}")

    args=["python3", "setup.py", "--command-packages", "stdeb.command", "sdist_dsc"]

    if patchFilePath.exists():
      print(f"Patch found: {patchFilePath}")
      args.append("-p")
      args.append(str(patchFilePath))

    for field in shlex.split(options_str):
      args.append(field)
      
    args.append("--dist-dir")
    args.append("./artifacts")

    args.append("bdist_deb")

    click.echo(args)

    subprocess.run(args)


if __name__ == "__main__":
    main(prog_name="pypi-build")  # pragma: no cover
