# User configuration

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
