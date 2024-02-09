#!/usr/bin/python3
import click
import os
import pathlib
import shlex
import shutil
import subprocess
import toml


def build_using_poetry(pyproject_file):
    parent = pyproject_file.parent
    print(f"Building using poetry in {pyproject_file.resolve()}...")

    # Modify toml to create setup.py when building
    with open(pyproject_file.resolve(), "r") as f:
        config = toml.load(f)
    if "tool" not in config:
        config["tool"] = {}
    if "poetry" not in config["tool"]:
        config["tool"]["poetry"] = {}
    config["tool"]["poetry"]["build"] = {"generate-setup-file": True}
    with open(pyproject_file.resolve(), "w") as f:
        toml.dump(config, f)

    # Build
    poetry_build = ["poetry", "build", "-f", "sdist"]
    click.echo(" ".join(poetry_build))
    proc = subprocess.run(poetry_build, cwd=parent)

    if proc.returncode != 0:
        raise Exception("Failed to build using poetry")
        return ""

    # Get path to tarball
    tarball_filename = subprocess.run(["ls", "-1", "dist"], capture_output=True, text=True, cwd=parent).stdout.strip()
    tarball = os.path.join(parent, "dist", tarball_filename)

    subprocess.run(["ls", "-l", tarball])

    return tarball


def extract_tarball(file, folder):
    if pathlib.Path(folder).exists():
        print(f"Removing existing folder {folder}")
        shutil.rmtree(folder)
    subprocess.run(["tar", "xzf", file])
    click.echo(f"Extracted folder: {folder}")
    subprocess.run(["ls", "-l", folder])


def handle_non_setuptools_package(extracted_folder):
    pyproject_file = pathlib.Path(os.path.join(extracted_folder, "pyproject.toml"))
    if pyproject_file.exists():
        print("pyproject.toml found!")

        new_tarball = build_using_poetry(pyproject_file)
        if new_tarball != "":
            # move tarball to root of repo and cleanup
            dst = os.path.join(os.getcwd(), new_tarball.split("/")[-1])
            shutil.move(pathlib.Path(new_tarball).resolve(), dst)
            shutil.rmtree(extracted_folder)
            return dst

    # Create setup.py to allow stdeb to build
    # XXX: some packages can't read the toml/cfg file on build, creating
    # a package as UNKNOWN. This is captured in https://github.com/pypa/setuptools/issues/3269
    print("Creating setup.py")
    with open(os.path.join(extracted_folder, "setup.py"), "w") as f:
        f.write("import setuptools; setuptools.setup()")

    return ""


@click.command()
###############################
# Command OR sourced function #
###############################
@click.option(
    "--path-to-tarball",
    type=str,
    default="",
)
@click.argument(
    "package",
    type=str,
    required=True,
)
@click.option(
    "--options-str",
    type=str,
)
def main(options_str, package, path_to_tarball):
    """pi-topOS meta-exec."""
    _main(options_str, package, path_to_tarball)


def _main(options_str, package, path_to_tarball):
    click.echo(f"Building {package}...")

    click.echo("Fixing permissions for current directory...")
    subprocess.run(["sudo", "chown", "-R", "nonroot:nonroot", "."])
    currentDir = pathlib.Path(os.getcwd())

    if len(path_to_tarball) == 0:
        click.echo("Downloading source...")
        proc = subprocess.run(["pypi-download", package], capture_output=True)
        if proc.returncode != 0:
            click.echo("Failed to download source")
            click.echo(proc)
            return
        tarball_filename = str(proc.stdout).split(" ")[1].split("\\")[0]
        return _main(options_str, package, os.path.join(currentDir, tarball_filename))
    elif not pathlib.Path(path_to_tarball).exists():
        click.echo(f"Tarball not found at {path_to_tarball}!")
        return

    click.echo(f"Using tarball at {path_to_tarball}, extracting...")
    extracted_folder = path_to_tarball.replace(".tar.gz", "").split("/")[-1]
    extract_tarball(path_to_tarball, extracted_folder)

    if not pathlib.Path(os.path.join(extracted_folder, "setup.py")).exists():
        click.echo("setup.py not found!")
        path_to_tarball = handle_non_setuptools_package(extracted_folder)
        if pathlib.Path(path_to_tarball).exists():
            return _main(options_str, package, path_to_tarball)

    if pathlib.Path(path_to_tarball).is_file():
        pathlib.Path(path_to_tarball).unlink(missing_ok=True)

    click.echo("Moving source to top-level of repo")
    for f in currentDir.rglob(f"{extracted_folder}/*"):
        click.echo(f"Moving {f} to {currentDir}...")
        try:
            shutil.move(f, currentDir)
        except Exception as e:
            # README.md in source will cause issues
            # TODO: handle this in another directory..?
            click.echo(
                f"WARNING: Unable to move {os.path.join(currentDir, extracted_folder, f)} to {currentDir}..."
            )
            click.echo(f"{e}")

    args = ["python3", "setup.py", "--command-packages", "stdeb.command", "sdist_dsc"]
    patch_file_path = pathlib.Path(
        os.path.join(currentDir, "pypi-build", "patches", f"{package}.patch")
    )
    click.echo(f"Looking for patch: {patch_file_path}")
    if patch_file_path.exists():
        print(f"Patch found: {patch_file_path}")
        args.append("--ignore-source-changes")

        with open(patch_file_path, "rb") as f:
            patchData = f.read()

        subprocess.run(["patch", "-p1"], input=patchData)

    click.echo("Listing top-level of repo...")
    subprocess.run(["ls", "-l", currentDir])

    if options_str:
        for field in shlex.split(options_str):
            args.append(field)

    args.append("--dist-dir")
    args.append("./artifacts")

    args.append("bdist_deb")

    click.echo("Checking for build dependencies...")
    if os.environ.get("BUILD_DEPENDENCIES"):
        click.echo("Build dependencies found - installing...")
        subprocess.run(
            ["sudo", "apt-get", "install", "-y"]
            + os.environ.get("BUILD_DEPENDENCIES").split(" ")
        )

    click.echo(" ".join(args))

    subprocess.run(args)


if __name__ == "__main__":
    main(prog_name="pypi-build")  # pragma: no cover
