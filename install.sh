#!/bin/sh
set -e
set -o pipefail
export DEBIAN_FRONTEND=noninteractive
#
# This script is meant for quick & easy install via:
#   'curl -sSL https://finding-ray.gitlab.io/install.sh | sh'
# or:
#   'wget -qO- https://finding-ray.gitlab.io/install.sh | sh'
#

# System Config
DOCKER_IMAGE=""
PKG_MANAGER=""
ARCH=""
OS=""

# Variable Functions
sh_c=""

# Colors
# Only run `tput` if session is interactive and TTY is assigned
RED=$(tty -s && tput setaf 1)
YELLOW=$(tty -s && tput setaf 3)
CYAN=$(tty -s && tput setaf 6)
NORMAL=$(tty -s && tput sgr0)


#
## Utility Functions
#

_banner()
{
    printf "${CYAN}"
    echo '            __  _ __        __  __                '
    echo ' ___ ____  / /_(_) /____ __/ /_/ /  ___ _______ _ '
    echo "/ _ \`/ _ \\/ __/ /  '_/ // / __/   \\/ -_) __/ _ \`/ "
    echo '\_,_/_//_/\__/_/_/\_\\_, /\__/_//_/\__/_/  \_,_/  '
    echo '                    /___/                         '
    printf "${NORMAL}"
}

_greeting()
{
    _banner
    echo '' 
    echo '' 
    echo 'This script will install the antikythera program. It will'
    echo 'attempt to detect your system configuration to install and'
    echo 'configure a antiktyhera for your environment. This script'
    echo 'will install the program globally on the system for all users.'
    echo '' 
    echo '' 
    echo 'If that is not what you want press CTRL+C to exit,' 
    echo -n 'otherwise you may safely ignore this message.  '

    local -a frames=( '/' '-' '\' '|' )
    for x in `seq 1 15`; do 
        echo -ne "${frames[i++ % ${#frames[@]}]}"
        sleep 1
        echo -ne "\b"
    done

    echo ''
}

_error()
{
    printf "${RED}[*] Error: ${NORMAL}$1"
    echo ""
}

_warning()
{
    printf "${YELLOW}[*] Error: ${NORMAL}$1"
    echo ""
}

_info()
{
    printf "${CYAN}[*] Info: ${NORMAL}$1"
    echo ""
}

## Print a horizontal rule
_rule ()
{
    printf -v _hr "%*s" $(tput cols) && echo ${_hr// /${1--}}
}


command_exists()
{
    command -v "$@" > /dev/null 2>&1
}


#
## System Detection
#

found_os()
{
    local pkg_manager=$1
    shift
    grep -qis "$*" /etc/issue && PKG_MANAGER="$pkg_manager"
}

# Rudimentary OS detection
check_pkgmanager()
{
    found_os PACMAN "Arch Linux" && return
    found_os DPKG   "Debian GNU/Linux" && return
    found_os DPKG   "Ubuntu" && return
    found_os YUM    "CentOS" && return
    found_os YUM    "Red Hat" && return
    found_os YUM    "Fedora" && return
    found_os ZYPPER "SUSE" && return

    [[ -z "$PKG_MANAGER" ]] || return
    _warning "Can't detect OS from /etc/issue... attempting fallback"

    if [[ -x "/usr/bin/pacman" ]]; then
        grep -q "$FUNCNAME" '/usr/bin/pacman' >/dev/null 2>&1
        [[ $? -ge 1 ]] && PKG_MANAGER="PACMAN" && return
    fi

    [[ -x "/usr/bin/apt-get" ]]     && PKG_MANAGER="DPKG" && return
    [[ -x "/usr/bin/yum" ]]         && PKG_MANAGER="YUM" && return
    [[ -x "/opt/local/bin/port" ]]  && PKG_MANAGER="MACPORTS" && return
    command -v brew >/dev/null      && PKG_MANAGER="HOMEBREW" && return
    [[ -x "/usr/bin/emerge" ]]      && PKG_MANAGER="PORTAGE" && return
    [[ -x "/usr/bin/zypper" ]]      && PKG_MANAGER="ZYPPER" && return

    if [[ -z "$PKG_MANAGER" ]]; then
        local message=(
        "[*] Error: No supported package manager installed on this system"
        "[*] Supported: apt, yum"
        )
        printf '%s\n' "${message[@]}"
        exit 1
    fi
}


check_distro()
{
    check_pkgmanager # attempt package manager detection
    _info "Found Package Manager "$PKG_MANAGER""
    if [ -f /.dockerenv ]; then
        # We are inside a docker container!
        # Might not have lsb_release in a minimal install.
        DOCKER_IMAGE=true
        if ! command_exists lsb_release; then
            # TODO: support other package managers
            # install lsb_release
            _info "Command lsb_release not found attempting install"
            $sh_c 'sleep 3; apt-get --yes -qq update'
            case "$PKG_MANAGER" in
                DPKG)
                    ( set -x; $sh_c 'sleep 3; apt-get --force-yes -qq --show-progress install lsb-release' ) \
                ;;
                YUM)
                    ( set -x; $sh_c 'sleep 3; yum --assumeyes -qq redhat-lsb' ) \
                ;;
                *)
                    local message=(
                    "[*] Error: Unable to install lsb_release command"
                    "[*] Supported: apt, yum"
                    )
                    printf '%s\n' "${message[@]}"
                    exit 1
                ;;
            esac
            _info "Command lsb_release successfully installed"
        fi
    fi

    if command_exists lsb_release; then
        lsb_dist="$(lsb_release -si)"
    fi
    if [ -z "$lsb_dist" ] && [ -r /etc/lsb-release ]; then
        lsb_dist="$(. /etc/lsb-release && echo "$DISTRIB_ID")"
    fi
    [ -z "$lsb_dist" ] && [ -r /etc/debian_version ] && lsb_dist='debian'
    [ -z "$lsb_dist" ] && [ -r /etc/fedora-release ] && lsb_dist='fedora'
    [ -z "$lsb_dist" ] && [ -r /etc/centos-release] && lsb_dist='centos'
    [ -z "$lsb_dist" ] && [ -r /etc/redhat-release] && lsb_dist='redhat'
    if [ -z "$lsb_dist" ] && [ -r /etc/os-release]; then
        lsb_dist=$(. /etc/os-release && echo "$ID")
    fi

    OS="$(echo "$lsb_dist" | tr '[:upper:]' '[:lower:]')"
}

#
## Dependencies
#

# add missing ffmpeg repository
# it is no longer in debian default repos
# and it is a kivy dependency
prepare_ffmpeg()
{
    _info "Configuring ffmpeg for insatll"

    ffmpeg_repo='deb http://www.deb-multimedia.org jessie main non-free'
    ffmpeg_src='deb-src http://www.deb-multimedia.org jessie main non-free'

    if ! grep -q -F "$ffmpeg_repo" /etc/apt/sources.list; then
        $sh_c "sleep 3; echo 'deb http://www.deb-multimedia.org jessie main non-free' >> /etc/apt/sources.list" \
        && _info "Added repository: $ffmpeg_repo"
    fi

    if ! grep -q -F "$ffmpeg_src" /etc/apt/sources.list; then
        $sh_c "sleep 3; echo 'deb-src http://www.deb-multimedia.org jessie main non-free' >> /etc/apt/sources.list" \
        && _info "Added repository: $ffmpeg_src"
    fi

    if [ "$DOCKER_IMAGE" = true ]; then
        cat /etc/apt/sources.list
    fi

    $sh_c 'sleep 3; apt-get --yes -qq update' \
        && ( set -x; $sh_c 'sleep 3; apt-get --force-yes -qq install deb-multimedia-keyring' ) \
        && $sh_c 'sleep 3; apt-get --yes -qq update'
}


# Install Cython and Kivy requirements
depends_install()
{
    _info "[*] Installing Dependencies"
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install git build-essential' )
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install libav-tools' )
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install ffmpeg libsdl2-dev libsdl2-image-dev' )
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev' )
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install libswscale-dev libavformat-dev libavcodec-dev' )
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install zlib1g-dev python3-dev' )

    # pyshark dependency
    ( set -x; $sh_c 'sleep 3; apt-get --force-yes -qq --show-progress install tshark' )
}

#
## Actual Install
#

pip_install()
{
    _info "[*] Installing antikythera"

    # Setup to install
    ( set -x; $sh_c 'sleep 3; apt-get --yes -qq --show-progress install python3-pip curl' )
    ( set -x; $sh_c 'sleep 3; pip3 -q install --upgrade pip' )
    ( set -x; $sh_c 'sleep 3; pip3 -q install --upgrade setuptools' )

    # Can't let pip handle install order of dependancies
    # It always tries to install kivy before it's cython
    # dependency. `requirements.txt` has the depends listed
    # in order from top to bottom to support this.
    ( set -x; $sh_c 'sleep 3; curl -sSL "https://gitlab.com/finding-ray/antikythera/raw/master/requirements.txt" | xargs -n 1 -L 1 pip3 -q install' )
    ( set -x; $sh_c 'sleep 3; pip3 -q install antikythera' )
}


#
## Main
#

install()
{
    _greeting
    _rule
    user="$(id -un 2>/dev/null || true)"

    sh_c='sh -c'
    if (( $EUID != 0 )); then
        if command_exists sudo; then
            sh_c='sudo sh -c'
        elif command_exists su; then
            sh_c='su -c'
        else
            local message=(
            "[*] Error: Permissions required to install packages."
            "[*] The installer needs the ability to run commands as root."
            "[*] Unable to find either 'sudo' or 'su' for the installation."
            )
            printf '%s\n' "${message[@]}"
            exit 1
        fi
    fi

    check_distro       # Check what OS & package manager
    ARCH="$(uname -m)" # Check if ARM or x86
    case $ARCH in
        # Supported
        x86_64|armv7l)
            _info "Detected supported system architecture $ARCH."
            ;;
        # Not Supported
        *)
            _error "Error: $ARCH is not a supported platform"
            exit 1
            ;;
    esac

    # TODO:
    #
    #   * Support more OSs
    #
    case $OS in
        # Supported
        debian|raspbian)
            _info "Detected supported Linux distribution $OS"
            _info "Updating Packages"
            $sh_c 'sleep 3; apt-get --yes -qq update'
            prepare_ffmpeg
            depends_install
            pip_install
            _info "Setup successful"
            exit 0
        ;;
        ubuntu)
            _info "Detected supported Linux distribution $OS"
            _info "Updating Packages..."
            $sh_c 'sleep 3; apt-get --yes -qq update'
            depends_install
            pip_install
            _info "Setup successful"
            exit 0
        ;;
        # Unsupported
        *)
            _error "Error: $OS is not supported"
            exit 1
        ;;
    esac 

    exit 1
}

# All wrapped up in functions
# In case of partial download it should fail
install
