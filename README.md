# dotfiles

My repo with vim and zsh config files

### dependencies
gcc, cmake, vim, zsh, lua, clang/llvm, nodejs, npm, python, jdk, go

## Installation
Currently working on manjaro linux

1.  Upgrade system
    
    ```bash
    sudo pacman -Syu 
    ```

1.  Install dependencies:
    
    ```bash
    sudo pacman gcc cmake vim zsh lua nodejs npm, python, jdk, go
    pamac build ncurses5-compat-libs
    ```

1.  Clone this repo and copy .vimrc to the home dir:
    
    ```bash
    git clone https://github.com/Fokz210/dotfiles
    cd dotfiles
    cp .vimrc ~/.vimrc
    ```
1.  Get VundleVim plugin manager:

    ```bash
    git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim
    ```
1.  Install plugins
    
    From command line:
    ```bash
    vim +PluginInstall +qall
    ```
    Or launch `vim` and type `:PluginInstall`
    
    Wait until installation is complete
    
1.  Compile YouCompleteMe plugin
    
    ```bash
    cd ~/.vim/bundle/YouCompleteMe
    ./install.py --all
    ```
1.  Compile color_coded plugin
    
    ```bash
    cd ~/.vim/bundle/color_coded
    rm -f CMakeCache.txt
    mkdir build && cd build
    cmake ..
    make && make install
    ```
    
    
