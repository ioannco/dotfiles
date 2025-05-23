# User configuration

export GIT_EDITOR=nvim

function fish_prompt
    # Цвета:
    set_color -o blue    # user
    echo -n (whoami)

    set_color normal
    echo -n "@"

    set_color green      # hostname
    echo -n (hostname)

    set_color normal
    echo -n " "

    set_color yellow     # путь
    echo -n (prompt_pwd)

    set_color normal
    echo -n " "

    set_color magenta    # git ветка
    echo -n (fish_vcs_prompt)

    echo
    set_color brwhite
    echo -n "> "
    set_color normal
end


# Playbook servers
set -x PBOOK "tttttv@62.84.118.45"
function pb; ssh $PBOOK; end

# OSCOURSE
set -x ISP_PATH "/Users/ioannco/KERNEL/ispras-gcc/bin:/Users/ioannco/KERNEL/ispras-gdb/bin:/Users/ioannco/KERNEL/ispras-qemu/bin:/Users/ioannco/KERNEL/ispras-llvm/bin"

# ControlGPS servers
function crm; ssh ioannco@158.160.33.107; end
function trk; ssh ioannco@51.250.78.89; end
function crm-prod; ssh ioannco@51.250.64.81; end
function trk-prod; ssh ioannco@51.250.91.239; end

# My server
function home-server; ssh ioannco@46.138.247.234; end
fish_add_path /home/ioannco/cli-tools/bin
