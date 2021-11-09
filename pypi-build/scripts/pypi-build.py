#!/usr/bin/python3
import click
import os
import pathlib
import shlex
import shutil
import subprocess


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
    click.echo("Fixing permissions for current directory...")
    subprocess.run(["sudo", "chown", "-R", "nonroot:nonroot", "."])


    click.echo("Downloading source...")
    proc = subprocess.run(["pypi-download", package], capture_output=True)
    if proc.returncode != 0:
      click.echo("Failed to download source")
      click.echo(proc)
      return


    click.echo("Extracting source...")
    tarballFilename = str(proc.stdout).split(" ")[1].split("\\")[0]
    subprocess.run(["tar", "xzf", tarballFilename])


    click.echo("Moving source to top-level of repo...")
    currentDir = pathlib.Path(os.getcwd())
    subDir = tarballFilename.replace(".tar.gz", "")
    for f in currentDir.rglob(f"{subDir}/*"):
        try:
            shutil.move(os.path.join(currentDir, subDir, f), currentDir)
        except Exception:
            click.echo(f"WARNING: Unable to move {os.path.join(currentDir, subDir, f)} to {currentDir}...")


    click.echo("Removing tarball...")
    os.remove(tarballFilename)

    click.echo("Listing top-level of repo...")
    subprocess.run(["ls", "-l", currentDir])

    patchFilePath = pathlib.Path(os.path.join(currentDir, "pypi-build", "patches", f"{package}.patch"))
    print(f"Looking for patch: {patchFilePath}")

    args=["python3", "setup.py", "--command-packages", "stdeb.command", "sdist_dsc"]

    if patchFilePath.exists():
      print(f"Patch found: {patchFilePath}")
      for i in ["-p", str(patchFilePath), "-l", str(1)]:
        args.append(i)
      args.append("--ignore-source-changes")
      
    if options_str:
      for field in shlex.split(options_str):
        args.append(field)

    args.append("--dist-dir")
    args.append("./artifacts")

    args.append("bdist_deb")


    click.echo("Checking for build dependencies...")
    if os.environ.get('BUILD_DEPENDENCIES'):
      click.echo("Build dependencies found - installing...")
      subprocess.run(["sudo", "apt-get", "install", "-y"] + os.environ.get('BUILD_DEPENDENCIES').split(" "))


    click.echo(" ".join(args))

    subprocess.run(args)


if __name__ == "__main__":
    main(prog_name="pypi-build")  # pragma: no cover
