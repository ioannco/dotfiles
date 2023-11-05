#!/usr/bin/env python3

# imports 
import sys
import os
import shutil as sh
from pathlib import Path
import shutil

args = sys.argv

# log func
def log(str):
    print(str, file=sys.stderr)

# move func
def mvsafe(src: Path, dst: Path):
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        log(f'{src} not found, skipping')

def include(fetaure, options):
    return fetaure in options or 'all' in options

def install(options):
    # init paths
    repo_dir = Path().absolute()
    home_dir = Path.home()
    p10k_dir = home_dir / 'powerlevel10k'

    if os.path.exists(home_dir/'.oh-my-zsh'):
        mvsafe(home_dir/'.oh-my-zsh', home_dir/'.oh-my-zsh.save')

    # clone repos 
    os.system('curl -L https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh | sh')
    os.system('git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions')
    os.system('git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting')

    # backup old dotfiles
    mvsafe(home_dir / '.zshrc', home_dir / '.zshrc.save')
    mvsafe(home_dir / '.p10k.zsh', home_dir / '.p10k.zsh')

    # copy new dotfiles
    sh.copy(repo_dir / '.zshrc', home_dir / '.zshrc')
    sh.copy(repo_dir / '.p10k.zsh', home_dir / '.p10k.zsh')

    # optional features
    # crm aliases
    if include('crm-aliases', options):
        print("Crm-aliases")
        sh.copy(repo_dir / '.crm_aliases', home_dir / '.crm_aliases')
        with open(home_dir / '.zshrc', 'a+') as zshrc:
            zshrc.write("# CRM aliases (optional)\n")
            zshrc.write("source ~/.crm_aliases\n")
            zshrc.write("\n")
        
    # brew
    if include('brew', options):
        print("Brew")
        os.system('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
        with open(home_dir / '.zshrc', 'a+') as zshrc:
            zshrc.write("# Brew (optional)\n")
            zshrc.write("eval $(/opt/homebrew/bin/brew shellenv)\n")
            zshrc.write("\n")

    # vscode
    if include('code', options):
        print("VSCode alias")
        with open(home_dir / '.zshrc', 'a+') as zshrc:
            zshrc.write("# VSCode(optional)\n")
            zshrc.write("export vscode='Visual Studio Code'\n")
            zshrc.write("alias code='open -a $vscode'\n")
            zshrc.write("\n")

    print('Success!')

def clean():
    home_dir = Path.home()

    if os.path.exists(home_dir / '.zshrc'):
        os.remove(home_dir / '.zshrc')

    if os.path.exists(home_dir / '.crm_aliases'):
        os.remove(home_dir / '.crm_aliases')

    if os.path.exists(home_dir / '.oh-my-zsh'):
        shutil.rmtree(home_dir / '.oh-my-zsh')

def print_help():
    print()
    print("ioannco dotfiles installation manager")
    print()
    print("-h --help          print help")
    print("install [options]  install dotfiles with certain options")
    print("clean              remove old dotfiles")
    print()
    print("options: ")
    print("    brew           include brew into the installation")
    print("    crm-aliases    include ControlGps crm aliases")
    print("    code           include MacOS vscode open alias")
    print("    all            install all options")

if __name__ == '__main__':
    args = sys.argv
    if '-h' in args or '--help' in args:
        print_help()
    elif 'install' in args:
        args.remove('install')
        install(args)
    elif 'clean' in args:
        clean()
    else:
        print_help()