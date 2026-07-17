#!/usr/bin/env python3

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path
import shutil as sh


# log func
def log(msg):
    print(msg, file=sys.stderr)


def info(msg):
    print(msg)


# move func
def mvsafe(src: Path, dst: Path):
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        info(f'{src} not found, skipping')


def feature_supported(feature, system):
    if feature == 'brew':
        return system in ('Darwin', 'Linux')
    if feature == 'code':
        return system == 'Darwin'
    if feature == 'nvim':
        return True
    if feature == 'tmux':
        return True
    return False


def include(feature, options, system):
    if feature in options:
        return True
    if 'all' in options:
        return feature_supported(feature, system)
    return False


def supported_features_for_system(system):
    features = ['brew', 'code', 'nvim', 'tmux']
    return [feature for feature in features if feature_supported(feature, system)]


def write_to_config(config_path, content):
    info(f"Appending to {config_path}")
    with open(config_path, 'a+') as config_file:
        config_file.write(content)


def run(cmd, *, shell=False):
    if isinstance(cmd, (list, tuple)):
        display_cmd = " ".join(cmd)
    else:
        display_cmd = cmd
    info(f"+ {display_cmd}")
    subprocess.run(cmd, check=True, shell=shell)


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
    preferred_paths = [
        '/opt/homebrew/bin/brew',
        '/usr/local/bin/brew',
        '/home/linuxbrew/.linuxbrew/bin/brew',
    ]
    for path in preferred_paths:
        if os.path.exists(path):
            return path
    return sh.which('brew')

def install_shell(install_shell_flag, shell):
    if install_shell_flag:
        system = platform.system()
        if system == 'Linux':
            distro = get_linux_distro_id()
            if distro == 'ubuntu':
                info(f"Installing {shell} using apt...")
                run(['sudo', 'apt', 'install', '-y', shell])
            elif distro == 'arch':
                info(f"Installing {shell} using pacman...")
                run(['sudo', 'pacman', '-S', '--noconfirm', shell])
            else:
                log("Unsupported Linux distribution for shell installation.")
        elif system == 'Darwin':  # macOS
            info(f"Installing {shell} using brew...")
            brew_path = get_brew_path()
            if brew_path:
                run([brew_path, 'install', shell])
            else:
                log("Homebrew not found.")
        else:
            log("Unsupported OS for shell installation.")
    else:
        info("Shell installation skipped.")


def install(options, shell, install_shell_flag):
    # init paths
    repo_dir = Path().absolute()
    home_dir = Path.home()
    system = platform.system()
    if 'all' in options:
        features = supported_features_for_system(system)
        info(f"All mode: enabling {', '.join(features)}")

    # Install the shell if requested
    install_shell(install_shell_flag, shell)

    # Only clone oh-my-zsh if the selected shell is zsh
    if shell == 'zsh':
        omz_dir = home_dir / '.oh-my-zsh'

        # clone oh-my-zsh
        if omz_dir.exists():
            info("oh-my-zsh already installed, skipping install.")
        else:
            run(
                'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
                shell=True,
            )

        # clone plugins
        zsh_custom = Path(os.environ.get('ZSH_CUSTOM', str(omz_dir / 'custom')))
        plugins_dir = zsh_custom / 'plugins'
        autosuggest_dir = plugins_dir / 'zsh-autosuggestions'
        syntax_dir = plugins_dir / 'zsh-syntax-highlighting'
        if not autosuggest_dir.exists():
            run(
                'git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions',
                shell=True,
            )
        else:
            info("zsh-autosuggestions already installed, skipping clone.")
        if not syntax_dir.exists():
            run(
                'git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting',
                shell=True,
            )
        else:
            info("zsh-syntax-highlighting already installed, skipping clone.")

        # backup old dotfiles
        info("Backing up existing zsh configs if present.")
        mvsafe(home_dir / '.zshrc', home_dir / '.zshrc.save')
        mvsafe(home_dir / '.p10k.zsh', home_dir / '.p10k.zsh.save')

        # copy new dotfiles
        info("Installing zsh configs.")
        sh.copy(repo_dir / '.zshrc', home_dir / '.zshrc')
        sh.copy(repo_dir / '.p10k.zsh', home_dir / '.p10k.zsh')
        config_path = home_dir / '.zshrc'

        # Warning to change shell
        info("Please change your default shell to zsh using the command:")
        info("chsh -s $(which zsh)")

    elif shell == 'fish':
        info("Installing fish config.")
        config_dir = home_dir / '.config' / 'fish'
        config_dir.mkdir(parents=True, exist_ok=True)
        sh.copy(repo_dir / 'config.fish', config_dir / 'config.fish')
        config_path = config_dir / 'config.fish'

        # Warning to change shell
        info("Please change your default shell to fish using the command:")
        info("chsh -s $(which fish)")

    # optional features
    if include('brew', options, system):
        if system not in ('Darwin', 'Linux'):
            log("Brew option is only supported on macOS and Linux for this script.")
        else:
            info("Brew")
            if system == 'Linux':
                default_brew_path = '/home/linuxbrew/.linuxbrew/bin/brew'
            else:
                default_brew_path = '/opt/homebrew/bin/brew'
            brew_path = get_brew_path()
            if brew_path:
                info("Homebrew already installed, skipping install.")
            else:
                run(
                    '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                    shell=True,
                )
                brew_path = get_brew_path()
            brew_path = brew_path or default_brew_path
            brew_content = "# Brew (optional)\n"
            if shell == 'zsh':
                brew_content += f"eval $({brew_path} shellenv)\n\n"
            elif shell == 'fish':
                brew_content += f"status --is-interactive; and eval ({brew_path} shellenv)\n\n"
            write_to_config(config_path, brew_content)

    if include('code', options, system):
        if system != 'Darwin':
            log("VSCode alias option is only supported on macOS for this script.")
        else:
            info("VSCode alias")
            code_content = "# VSCode (optional)\n"
            code_content += "export vscode='Visual Studio Code'\n"
            code_content += "alias code='open -a $vscode'\n\n"
            write_to_config(config_path, code_content)

    if include('nvim', options, system):
        info('Neovim')
        config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(home_dir / '.config'))).expanduser()
        nvim_dir = config_home / 'nvim'
        if nvim_dir.exists():
            info("Neovim config already exists, skipping clone.")
        else:
            run(
                'git clone https://github.com/ioannco/nvim-config.git "${XDG_CONFIG_HOME:-$HOME/.config}"/nvim',
                shell=True,
            )

    if include('tmux', options, system):
        info('tmux')
        info("Backing up existing tmux config if present.")
        mvsafe(home_dir / '.tmux.conf', home_dir / '.tmux.conf.save')
        info("Installing tmux config.")
        sh.copy(repo_dir / '.tmux.conf', home_dir / '.tmux.conf')

    info('Success!')


def clean():
    home_dir = Path.home()

    if (home_dir / '.zshrc').exists():
        os.remove(home_dir / '.zshrc')

    if (home_dir / '.crm_aliases').exists():
        os.remove(home_dir / '.crm_aliases')

    if (home_dir / '.oh-my-zsh').exists():
        sh.rmtree(home_dir / '.oh-my-zsh')


def list_features():
    system = platform.system()
    features = supported_features_for_system(system)
    info(f"Supported features for {system}: {', '.join(features)}")


def main():
    parser = argparse.ArgumentParser(
        description="Ioannco dotfiles installation manager")
    subparsers = parser.add_subparsers(dest='command')

    # install command
    install_parser = subparsers.add_parser(
        'install', help='install dotfiles with certain options')
    install_parser.add_argument(
        'options', nargs='*', choices=['brew', 'code', 'nvim', 'tmux', 'all'], help='options for installation')
    install_parser.add_argument(
        '--shell', choices=['zsh', 'fish'], required=True, help='choose shell for configuration')
    install_parser.add_argument(
        '--install-shell', action='store_true', help='install shell if not present')

    # clean command
    subparsers.add_parser('clean', help='remove old dotfiles')
    subparsers.add_parser('list-features', help='list supported features for the system')

    args = parser.parse_args()

    if args.command == 'install':
        install(args.options, args.shell, args.install_shell)
    elif args.command == 'clean':
        clean()
    elif args.command == 'list-features':
        list_features()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
