#!/usr/bin/env python3

# imports 
import sys
import os
import shutil as sh
from pathlib import Path

# log func
def log(str):
    print(str, file=sys.stderr)

# move func
def mvsafe(src: Path, dst: Path):
    try:
        sh.move(src, dst)
    except FileNotFoundError:
        log(f'{src} not found, skipping')

# init paths
repo_dir = Path().absolute()
home_dir = Path.home()
p10k_dir = home_dir / 'powerlevel10k'

# clone p10k repo
if p10k_dir.exists():
    sh.rmtree(p10k_dir)
os.system('git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ~/powerlevel10k')

# backup old dotfiles
mvsafe(home_dir / '.zshrc', home_dir / '.zshrc.save')
mvsafe(home_dir / '.p10k.zsh', home_dir / '.p10k.zsh')

# copy new dotfiles
sh.copy(repo_dir / '.zshrc', home_dir / '.zshrc')
sh.copy(repo_dir / '.p10k.zsh', home_dir / '.p10k.zsh')

print('success!')
