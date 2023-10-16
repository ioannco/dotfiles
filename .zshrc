# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

source ~/powerlevel10k/powerlevel10k.zsh-theme

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ControlGPS servers
alias crm='ssh ioannco@158.160.33.107'
alias trk='ssh ioannco@51.250.78.89'
alias crm-prod='ssh ioannco@51.250.64.81'
alias trk-prod='ssh ioannco@51.250.91.239'

# My server
alias home-server='ssh ioannco@46.138.247.234'

# Enable history
HISTFILE=~/.histfile
HISTSIZE=5000
SAVEHIST=5000
setopt appendhistory

# Playbook servers
export PBOOK="tttttv@62.84.118.45"
alias pb="ssh $PBOOK"

# OSCOURSE
export ISP_PATH="/Users/ioannco/KERNEL/ispras-gcc/bin:/Users/ioannco/KERNEL/ispras-gdb/bin:/Users/ioannco/KERNEL/ispras-qemu/bin:/Users/ioannco/KERNEL/ispras-llvm/bin"

