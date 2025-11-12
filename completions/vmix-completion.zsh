#compdef if

# Zsh completion for IF.vmix CLI
# Install: Place in your $fpath (e.g., /usr/local/share/zsh/site-functions/_if)
#
# Installation:
#   1. Copy to a directory in your $fpath
#   2. Rename to _if
#   3. Run: compinit
#
# Usage: Type 'if vmix <TAB>' to see available commands and options

_if_vmix() {
    local -a commands
    local -a instances

    # Get configured instances
    _get_vmix_instances() {
        local config_file="${HOME}/.if/vmix/instances.yaml"
        if [[ -f "$config_file" ]]; then
            grep -E "^  [a-zA-Z]" "$config_file" | awk '{print $1}' | sed 's/:$//'
        fi
    }

    instances=("${(@f)$(eval _get_vmix_instances)}")

    # Main vmix commands
    commands=(
        'add:Add vMix instance'
        'list:List vMix instances'
        'test:Test connection to vMix'
        'remove:Remove vMix instance'
        'cut:Cut to input (instant)'
        'fade:Fade to input'
        'preview:Set preview input'
        'transition:Execute custom transition'
        'overlay:Set overlay input'
        'ndi:NDI source control'
        'stream:Streaming control'
        'record:Recording control'
        'status:Get vMix status'
        'inputs:List all inputs'
        'state:Get production state'
        'ptz:PTZ camera control'
        'audio:Audio control'
    )

    # Parse command line
    local line state

    _arguments -C \
        '1: :->command' \
        '*::arg:->args'

    case $state in
        command)
            _describe 'vmix command' commands
            ;;
        args)
            case ${words[1]} in
                add)
                    _arguments \
                        '1:instance name:' \
                        '--host[vMix host IP]:host:' \
                        '--port[vMix API port (default 8088)]:port:(8088)'
                    ;;
                list)
                    _arguments \
                        '--format[Output format]:format:(text json)'
                    ;;
                test|remove)
                    _arguments \
                        "1:instance name:(${instances[@]})"
                    ;;
                cut)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                    ;;
                fade)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)' \
                        '--duration[Fade duration in ms]:duration:(500 1000 2000 3000)'
                    ;;
                preview)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                    ;;
                transition)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--type[Transition type]:type:(Fade Merge Wipe Zoom Stinger)' \
                        '--duration[Duration in ms]:duration:(500 1000 2000 3000)' \
                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                    ;;
                overlay)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--num[Overlay number]:num:(1 2 3 4)' \
                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)' \
                        '--action[Overlay action]:action:(OverlayInput OverlayInputIn OverlayInputOut)'
                    ;;
                ndi)
                    local -a ndi_commands
                    ndi_commands=(
                        'add:Add NDI input source'
                        'list:List NDI inputs'
                        'remove:Remove NDI input'
                    )
                    _arguments -C \
                        '1: :->ndi_command' \
                        '*::arg:->ndi_args'

                    case $state in
                        ndi_command)
                            _describe 'ndi command' ndi_commands
                            ;;
                        ndi_args)
                            case ${words[1]} in
                                add)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--source[NDI source name]:source:'
                                    ;;
                                list)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--format[Output format]:format:(text json)'
                                    ;;
                                remove)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                stream)
                    local -a stream_commands
                    stream_commands=(
                        'start:Start streaming'
                        'stop:Stop streaming'
                        'status:Get streaming status'
                    )
                    _arguments -C \
                        '1: :->stream_command' \
                        '*::arg:->stream_args'

                    case $state in
                        stream_command)
                            _describe 'stream command' stream_commands
                            ;;
                        stream_args)
                            case ${words[1]} in
                                start)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--rtmp[RTMP URL]:rtmp:' \
                                        '--key[Stream key]:key:' \
                                        '--channel[Stream channel]:channel:(0 1 2)'
                                    ;;
                                stop)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--channel[Stream channel]:channel:(0 1 2)'
                                    ;;
                                status)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--format[Output format]:format:(text json)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                record)
                    local -a record_commands
                    record_commands=(
                        'start:Start recording'
                        'stop:Stop recording'
                        'status:Get recording status'
                    )
                    _arguments -C \
                        '1: :->record_command' \
                        '*::arg:->record_args'

                    case $state in
                        record_command)
                            _describe 'record command' record_commands
                            ;;
                        record_args)
                            case ${words[1]} in
                                start)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--file[Output filename]:file:_files' \
                                        '--format[File format]:format:(MP4 AVI MOV)'
                                    ;;
                                stop)
                                    _arguments \
                                        "1:instance name:(${instances[@]})"
                                    ;;
                                status)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--format[Output format]:format:(text json)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                status|inputs|state)
                    _arguments \
                        "1:instance name:(${instances[@]})" \
                        '--format[Output format]:format:(text json)'
                    ;;
                ptz)
                    local -a ptz_commands
                    ptz_commands=(
                        'move:Move PTZ camera'
                        'preset:Recall PTZ preset'
                        'home:Move PTZ to home position'
                    )
                    _arguments -C \
                        '1: :->ptz_command' \
                        '*::arg:->ptz_args'

                    case $state in
                        ptz_command)
                            _describe 'ptz command' ptz_commands
                            ;;
                        ptz_args)
                            case ${words[1]} in
                                move)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)' \
                                        '--pan[Pan value]:pan:(-100 -50 0 50 100)' \
                                        '--tilt[Tilt value]:tilt:(-100 -50 0 50 100)' \
                                        '--zoom[Zoom value]:zoom:(0 25 50 75 100)'
                                    ;;
                                preset)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)' \
                                        '--preset[Preset number]:preset:(1 2 3 4 5 6 7 8)'
                                    ;;
                                home)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
                audio)
                    local -a audio_commands
                    audio_commands=(
                        'volume:Set input volume'
                        'mute:Mute input audio'
                        'unmute:Unmute input audio'
                    )
                    _arguments -C \
                        '1: :->audio_command' \
                        '*::arg:->audio_args'

                    case $state in
                        audio_command)
                            _describe 'audio command' audio_commands
                            ;;
                        audio_args)
                            case ${words[1]} in
                                volume)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)' \
                                        '--volume[Volume level]:volume:(0 25 50 75 100)'
                                    ;;
                                mute|unmute)
                                    _arguments \
                                        "1:instance name:(${instances[@]})" \
                                        '--input[Input number]:input:(1 2 3 4 5 6 7 8 9 10)'
                                    ;;
                            esac
                            ;;
                    esac
                    ;;
            esac
            ;;
    esac
}

# Only define completion if we're in the vmix subcommand
if [[ ${words[2]} == "vmix" ]]; then
    _if_vmix
fi
