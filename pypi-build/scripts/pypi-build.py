#!/usr/bin/python3
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
@click.option(
    "--options-str",
    type=str,
)
@click.argument(
    "package",
    type=str,
    required=True,
)
def main(optionsStr, package):
    """pi-topOS meta-exec."""
    click.echo(
        color.BOLD + color.GREEN + Figlet().renderText("pypi-build") + color.END
    )

    proc = subprocess.run(["pypi-download", package], capture_output=True)
    if proc.returncode != 0:
      click.echo("Failed to download source")
      return

    tarballFilename = str(proc.stdout).split(" ")[1].split("\\")[0]
    subprocess.run(["tar", "xvzf", tarballFilename])

    if os.environ.get('BUILD_DEPENDENCIES'):
      subprocess.run(["apt-get", "install", "-y"] + BUILD_DEPENDENCIES.split(" "))

    currentDir = os.getcwd()
    subDir = tarballFilename.replace(".tar.gz", "")
    for f in currentDir.rglob(f"{subDir}/*"):
        shutil.move(os.path.join(currentDir, subDir, f), currentDir)

    subprocess.run(["ls", currentDir], capture_output=True)
    patchFilePath = pathlib.Path(os.path.join(currentDir, "pypi-build", "patches", f"{package}.patch"))
    print(f"Looking for patch: {patchFilePath}")

    args=["python3", "setup.py", "--command-packages", "stdeb.command", "sdist_dsc"]

    if patchFilePath.exists():
      print(f"Patch found: {patchFilePath}")
      args.append(f"--stdeb-patch-file={patchFilePath}")

    for field in shlex.split(optionsStr):
      args.append(field)
      
    args.append("--dist-dir=./artifacts")
    args.append("bdist_deb")
    subprocess.run(args, capture_output=True)
