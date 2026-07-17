#!/usr/bin/env python3
"""Ioannco dotfiles installer.

Symlinks the tracked config files into your home directory (so edits in this
repo take effect immediately) and sets up a handful of optional features.

Examples:
    ./install.py install                 # auto-detect shell, install everything
    ./install.py install --shell fish    # force fish instead of the detected shell
    ./install.py install tmux vim        # only these features (plus core config)
    ./install.py install --install-shell # also install the shell package itself
    ./install.py list                    # show supported features
    ./install.py clean                   # remove installed symlinks, restore backups
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
import shutil as sh

REPO_DIR = Path(__file__).resolve().parent
HOME = Path.home()

OPTIONAL_FEATURES = ['brew', 'code', 'nvim', 'tmux', 'vim']


# --- logging ---------------------------------------------------------------

def log(msg):
    print(msg, file=sys.stderr)


def info(msg):
    print(msg)


# --- shell helpers ---------------------------------------------------------

def run(cmd, *, shell=False):
    display = cmd if isinstance(cmd, str) else " ".join(cmd)
    info(f"+ {display}")
    subprocess.run(cmd, check=True, shell=shell)


def remove(path: Path):
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        sh.rmtree(path)


def backup(path: Path):
    """Move an existing real file/dir aside to `<name>.save`."""
    dest = path.parent / (path.name + '.save')
    if dest.exists() or dest.is_symlink():
        remove(dest)  # drop a previous backup
    info(f"Backing up {path} -> {dest}")
    sh.move(str(path), str(dest))


def link(src: Path, dst: Path):
    """Symlink `dst` -> `src`, backing up any real file already at `dst`."""
    src = src.resolve()
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink():
        if dst.resolve() == src:
            info(f"{dst} already linked, skipping.")
            return
        dst.unlink()  # replace a stale/foreign symlink
    elif dst.exists():
        backup(dst)
    dst.symlink_to(src)
    info(f"Linked {dst} -> {src}")


# --- detection -------------------------------------------------------------

def detect_shell():
    name = Path(os.environ.get('SHELL', '')).name
    return name if name in ('zsh', 'fish') else 'zsh'


def get_linux_distro_id():
    try:
        with open('/etc/os-release') as f:
            for line in f:
                if line.startswith('ID='):
                    return line.strip().split('=')[1].replace('"', '')
    except FileNotFoundError:
        return None
    return None


def get_brew_path():
    for path in (
        '/opt/homebrew/bin/brew',
        '/usr/local/bin/brew',
        '/home/linuxbrew/.linuxbrew/bin/brew',
    ):
        if os.path.exists(path):
            return path
    return sh.which('brew')


def feature_supported(feature, system):
    support = {
        'brew': system in ('Darwin', 'Linux'),
        'code': system == 'Darwin',
        'nvim': True,
        'tmux': True,
        'vim': True,
    }
    return support.get(feature, False)


def supported_features(system):
    return [f for f in OPTIONAL_FEATURES if feature_supported(f, system)]


# --- shell package / config ------------------------------------------------

def install_shell_package(shell, system):
    if system == 'Linux':
        distro = get_linux_distro_id()
        if distro == 'ubuntu':
            run(['sudo', 'apt', 'install', '-y', shell])
        elif distro == 'arch':
            run(['sudo', 'pacman', '-S', '--noconfirm', shell])
        else:
            log(f"Unsupported Linux distro for installing {shell}; do it manually.")
    elif system == 'Darwin':
        brew_path = get_brew_path()
        if brew_path:
            run([brew_path, 'install', shell])
        else:
            log("Homebrew not found; install it first or pass the brew feature.")
    else:
        log(f"Unsupported OS for installing {shell}.")


def install_oh_my_zsh():
    omz_dir = HOME / '.oh-my-zsh'
    if omz_dir.exists():
        info("oh-my-zsh already installed.")
    else:
        run('sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
            shell=True)

    zsh_custom = Path(os.environ.get('ZSH_CUSTOM', str(omz_dir / 'custom')))
    plugins = {
        'zsh-autosuggestions': 'https://github.com/zsh-users/zsh-autosuggestions',
        'zsh-syntax-highlighting': 'https://github.com/zsh-users/zsh-syntax-highlighting.git',
    }
    for name, url in plugins.items():
        dest = zsh_custom / 'plugins' / name
        if dest.exists():
            info(f"{name} already installed.")
        else:
            run(['git', 'clone', url, str(dest)])


def install_shell_config(shell):
    if shell == 'zsh':
        install_oh_my_zsh()
        link(REPO_DIR / '.zshrc', HOME / '.zshrc')
        link(REPO_DIR / '.p10k.zsh', HOME / '.p10k.zsh')
        info("To make zsh your default shell: chsh -s $(which zsh)")
    elif shell == 'fish':
        link(REPO_DIR / 'config.fish', HOME / '.config' / 'fish' / 'config.fish')
        info("To make fish your default shell: chsh -s $(which fish)")


def local_config_path(shell):
    if shell == 'fish':
        return HOME / '.config' / 'fish' / 'local.fish'
    return HOME / '.zshrc.local'


# --- optional features -----------------------------------------------------

def ensure_brew(system):
    brew_path = get_brew_path()
    if brew_path:
        info("Homebrew already installed.")
        return brew_path
    info("Installing Homebrew...")
    run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        shell=True)
    default = '/home/linuxbrew/.linuxbrew/bin/brew' if system == 'Linux' else '/opt/homebrew/bin/brew'
    return get_brew_path() or default


def install_nvim():
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(HOME / '.config'))).expanduser()
    nvim_dir = config_home / 'nvim'
    if nvim_dir.exists():
        info("Neovim config already exists, skipping clone.")
    else:
        run(['git', 'clone', 'https://github.com/ioannco/nvim-config.git', str(nvim_dir)])


def build_local_config(features, shell, system):
    """Machine-specific snippets that shouldn't live in the tracked config."""
    lines = []
    if 'brew' in features:
        brew_path = ensure_brew(system)
        lines.append("# Homebrew")
        if shell == 'fish':
            lines.append(f"status --is-interactive; and eval ({brew_path} shellenv)")
        else:
            lines.append(f'eval "$({brew_path} shellenv)"')
        lines.append("")
    if 'code' in features:
        lines.append("# VSCode CLI alias")
        lines.append("alias code 'open -a \"Visual Studio Code\"'" if shell == 'fish'
                     else "alias code='open -a \"Visual Studio Code\"'")
        lines.append("")
    return lines


def write_local_config(shell, lines):
    path = local_config_path(shell)
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "# Generated by the dotfiles installer. Machine-specific, do not track.\n\n"
    path.write_text(header + "\n".join(lines).rstrip() + "\n")
    info(f"Wrote machine-specific config to {path}")


# --- commands --------------------------------------------------------------

def resolve_features(requested, system):
    if not requested or 'all' in requested:
        chosen = supported_features(system)
        info(f"Installing all supported features: {', '.join(chosen)}")
        return chosen
    chosen = []
    for feature in requested:
        if feature_supported(feature, system):
            chosen.append(feature)
        else:
            log(f"Skipping '{feature}': not supported on {system}.")
    return chosen


def install(requested_features, shell, install_shell_flag):
    system = platform.system()
    shell = shell or detect_shell()
    features = resolve_features(requested_features, system)
    info(f"Shell: {shell}  |  OS: {system}")

    if install_shell_flag:
        install_shell_package(shell, system)

    install_shell_config(shell)

    if 'tmux' in features:
        info('tmux')
        link(REPO_DIR / '.tmux.conf', HOME / '.tmux.conf')
    if 'vim' in features:
        info('vim')
        link(REPO_DIR / '.vimrc', HOME / '.vimrc')
    if 'nvim' in features:
        info('Neovim')
        install_nvim()

    local_lines = build_local_config(features, shell, system)
    if local_lines:
        write_local_config(shell, local_lines)

    info('Success!')


def clean():
    """Remove symlinks that point back into this repo and restore backups."""
    targets = [
        HOME / '.zshrc',
        HOME / '.p10k.zsh',
        HOME / '.vimrc',
        HOME / '.tmux.conf',
        HOME / '.config' / 'fish' / 'config.fish',
    ]
    for path in targets:
        if path.is_symlink() and str(path.resolve()).startswith(str(REPO_DIR)):
            path.unlink()
            info(f"Removed {path}")
            saved = path.parent / (path.name + '.save')
            if saved.exists():
                sh.move(str(saved), str(path))
                info(f"Restored {path} from backup")

    for generated in (HOME / '.zshrc.local', HOME / '.config' / 'fish' / 'local.fish'):
        if generated.exists():
            generated.unlink()
            info(f"Removed {generated}")


def list_features():
    system = platform.system()
    info(f"Detected shell: {detect_shell()}")
    info(f"Supported features on {system}: {', '.join(supported_features(system))}")


# --- CLI -------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Ioannco dotfiles installer.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Examples:')[1] if 'Examples:' in __doc__ else None,
    )
    sub = parser.add_subparsers(dest='command')

    install_parser = sub.add_parser('install', help='symlink dotfiles and set up features')
    install_parser.add_argument(
        'features', nargs='*', choices=OPTIONAL_FEATURES + ['all'],
        help='features to install (default: all supported for your OS)')
    install_parser.add_argument(
        '--shell', choices=['zsh', 'fish'], default=None,
        help='shell to configure (default: auto-detect from $SHELL)')
    install_parser.add_argument(
        '--install-shell', action='store_true',
        help='also install the shell package itself')

    sub.add_parser('clean', help='remove installed symlinks and restore backups')
    sub.add_parser('list', help='list supported features for this system')

    args = parser.parse_args()

    if args.command == 'install':
        install(args.features, args.shell, args.install_shell)
    elif args.command == 'clean':
        clean()
    elif args.command == 'list':
        list_features()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
