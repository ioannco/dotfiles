#!/usr/bin/env python3

# imports 
import os
import shutil as sh
from pathlib import Path
import argparse
import platform
import subprocess
import sys  # Добавлен импорт sys

# log func
def log(msg):
    print(msg, file=sys.stderr)

# move func
def mvsafe(src: Path, dst: Path):
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        log(f'{src} not found, skipping')

def include(feature, options):
    return feature in options or 'all' in options

def write_to_config(config_path, content):
    with open(config_path, 'a+') as config_file:
        config_file.write(content)

def install_shell(install_shell_flag, shell):
    if install_shell_flag:
        system = platform.system()
        if system == 'Linux':
            try:
                with open('/etc/os-release') as f:
                    for line in f:
                        if line.startswith('ID='):
                            distro = line.strip().split('=')[1].replace('"', '')
                            break
                if distro == 'ubuntu':
                    log(f"Installing {shell} using apt...")
                    subprocess.run(['sudo', 'apt', 'install', '-y', shell], check=True)
                elif distro == 'arch':
                    log(f"Installing {shell} using pacman...")
                    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', shell], check=True)
                else:
                    log("Unsupported Linux distribution for shell installation.")
            except FileNotFoundError:
                log("Unable to determine Linux distribution.")
        elif system == 'Darwin':  # macOS
            log(f"Installing {shell} using brew...")
            brew_path = '/opt/homebrew/bin/brew'  # Путь к brew
            subprocess.run([brew_path, 'install', shell], check=True)
        else:
            log("Unsupported OS for shell installation.")
    else:
        log("Shell installation skipped.")

def install(options, shell, install_shell_flag):
    # init paths
    repo_dir = Path().absolute()
    home_dir = Path.home()

    # Install the shell if requested
    install_shell(install_shell_flag, shell)

    # Only clone oh-my-zsh if the selected shell is zsh
    if shell == 'zsh':
        if os.path.exists(home_dir / '.oh-my-zsh'):
            mvsafe(home_dir / '.oh-my-zsh', home_dir / '.oh-my-zsh.save')

        # clone oh-my-zsh
        os.system('sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"')

        # clone plugins
        os.system('git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions')
        os.system('git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting')

        # backup old dotfiles
        mvsafe(home_dir / '.zshrc', home_dir / '.zshrc.save')
        mvsafe(home_dir / '.p10k.zsh', home_dir / '.p10k.zsh')

        # copy new dotfiles
        sh.copy(repo_dir / '.zshrc', home_dir / '.zshrc')
        sh.copy(repo_dir / '.p10k.zsh', home_dir / '.p10k.zsh')
        config_path = home_dir / '.zshrc'
        
        # Warning to change shell
        log("Please change your default shell to zsh using the command:")
        log("chsh -s $(which zsh)")

    elif shell == 'fish':
        config_dir = home_dir / '.config' / 'fish'
        config_dir.mkdir(parents=True, exist_ok=True)
        sh.copy(repo_dir / 'config.fish', config_dir / 'config.fish')
        config_path = config_dir / 'config.fish'
        
        # Warning to change shell
        log("Please change your default shell to fish using the command:")
        log("chsh -s $(which fish)")

    # optional features
    if include('brew', options):
        print("Brew")
        os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        brew_content = "# Brew (optional)\n"
        if shell == 'zsh':
            brew_content += "eval $(/opt/homebrew/bin/brew shellenv)\n\n"
        elif shell == 'fish':
            brew_content += "status --is-interactive; and eval (/opt/homebrew/bin/brew shellenv)\n\n"
        write_to_config(config_path, brew_content)

    if include('code', options):
        print("VSCode alias")
        code_content = "# VSCode (optional)\n"
        code_content += "export vscode='Visual Studio Code'\n"
        code_content += "alias code='open -a $vscode'\n\n"
        write_to_config(config_path, code_content)

    print('Success!')

def clean():
    home_dir = Path.home()

    if os.path.exists(home_dir / '.zshrc'):
        os.remove(home_dir / '.zshrc')

    if os.path.exists(home_dir / '.crm_aliases'):
        os.remove(home_dir / '.crm_aliases')

    if os.path.exists(home_dir / '.oh-my-zsh'):
        sh.rmtree(home_dir / '.oh-my-zsh')

def main():
    parser = argparse.ArgumentParser(description="Ioannco dotfiles installation manager")
    subparsers = parser.add_subparsers(dest='command')

    # install command
    install_parser = subparsers.add_parser('install', help='install dotfiles with certain options')
    install_parser.add_argument('options', nargs='*', choices=['brew', 'code', 'all'], help='options for installation')
    install_parser.add_argument('--shell', choices=['zsh', 'fish'], required=True, help='choose shell for configuration')
    install_parser.add_argument('--install-shell', action='store_true', help='install shell if not present')

    # clean command
    subparsers.add_parser('clean', help='remove old dotfiles')

    args = parser.parse_args()

    if args.command == 'install':
        install(args.options, args.shell, args.install_shell)
    elif args.command == 'clean':
        clean()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
