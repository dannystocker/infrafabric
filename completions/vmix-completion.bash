#!/usr/bin/env bash
# Bash completion for IF.vmix CLI
# Install: source this file or add to ~/.bashrc
#
# Installation:
#   1. Copy to /etc/bash_completion.d/vmix
#   2. Or source in ~/.bashrc: source /path/to/vmix-completion.bash
#
# Usage: Type 'if vmix <TAB>' to see available commands and options

_if_vmix_completion() {
    local cur prev opts base
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Get the command path
    local cmd_idx=2  # 'if vmix' = index 2
    local cmd=""
    if [ ${#COMP_WORDS[@]} -gt 2 ]; then
        cmd="${COMP_WORDS[2]}"
    fi

    # Top-level commands
    local commands="add list test remove cut fade preview transition overlay ndi stream record status inputs state ptz audio"

    # NDI subcommands
    local ndi_commands="add list remove"

    # Stream subcommands
    local stream_commands="start stop status"

    # Record subcommands
    local record_commands="start stop status"

    # PTZ subcommands
    local ptz_commands="move preset home"

    # Audio subcommands
    local audio_commands="volume mute unmute"

    # Get list of configured instances
    _get_vmix_instances() {
        local config_file="${HOME}/.if/vmix/instances.yaml"
        if [ -f "$config_file" ]; then
            grep -E "^  [a-zA-Z]" "$config_file" | awk '{print $1}' | sed 's/:$//'
        fi
    }

    # Complete based on position and previous word
    case "${prev}" in
        vmix)
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
            return 0
            ;;
        add)
            case "${COMP_WORDS[COMP_CWORD-2]}" in
                ndi)
                    # ndi add <instance>
                    COMPREPLY=( $(compgen -W "$(_get_vmix_instances)" -- ${cur}) )
                    return 0
                    ;;
                *)
                    # vmix add <name>
                    COMPREPLY=( $(compgen -W "--host --port" -- ${cur}) )
                    return 0
                    ;;
            esac
            ;;
        list|test|remove|cut|fade|preview|transition|overlay|status|inputs|state)
            # These commands expect instance name
            COMPREPLY=( $(compgen -W "$(_get_vmix_instances)" -- ${cur}) )
            return 0
            ;;
        ndi)
            COMPREPLY=( $(compgen -W "${ndi_commands}" -- ${cur}) )
            return 0
            ;;
        stream)
            COMPREPLY=( $(compgen -W "${stream_commands}" -- ${cur}) )
            return 0
            ;;
        record)
            COMPREPLY=( $(compgen -W "${record_commands}" -- ${cur}) )
            return 0
            ;;
        ptz)
            COMPREPLY=( $(compgen -W "${ptz_commands}" -- ${cur}) )
            return 0
            ;;
        audio)
            COMPREPLY=( $(compgen -W "${audio_commands}" -- ${cur}) )
            return 0
            ;;
        start|stop|move|preset|home|volume|mute|unmute)
            # Subcommands that expect instance name
            COMPREPLY=( $(compgen -W "$(_get_vmix_instances)" -- ${cur}) )
            return 0
            ;;
        --host)
            # No completion for host
            return 0
            ;;
        --port)
            COMPREPLY=( $(compgen -W "8088" -- ${cur}) )
            return 0
            ;;
        --input)
            # Input numbers 1-10 (common range)
            COMPREPLY=( $(compgen -W "1 2 3 4 5 6 7 8 9 10" -- ${cur}) )
            return 0
            ;;
        --duration)
            # Common durations in milliseconds
            COMPREPLY=( $(compgen -W "500 1000 2000 3000" -- ${cur}) )
            return 0
            ;;
        --type)
            # Transition types
            COMPREPLY=( $(compgen -W "Fade Merge Wipe Zoom Stinger" -- ${cur}) )
            return 0
            ;;
        --num)
            # Overlay numbers
            COMPREPLY=( $(compgen -W "1 2 3 4" -- ${cur}) )
            return 0
            ;;
        --action)
            COMPREPLY=( $(compgen -W "OverlayInput OverlayInputIn OverlayInputOut" -- ${cur}) )
            return 0
            ;;
        --channel)
            COMPREPLY=( $(compgen -W "0 1 2" -- ${cur}) )
            return 0
            ;;
        --format)
            # Check if this is for file format or output format
            if [[ " ${COMP_WORDS[@]} " =~ " record " ]]; then
                COMPREPLY=( $(compgen -W "MP4 AVI MOV" -- ${cur}) )
            else
                COMPREPLY=( $(compgen -W "text json" -- ${cur}) )
            fi
            return 0
            ;;
        --volume)
            # Volume levels
            COMPREPLY=( $(compgen -W "0 25 50 75 100" -- ${cur}) )
            return 0
            ;;
        --pan|--tilt)
            # Pan/tilt values
            COMPREPLY=( $(compgen -W "-100 -50 0 50 100" -- ${cur}) )
            return 0
            ;;
        --zoom)
            # Zoom values
            COMPREPLY=( $(compgen -W "0 25 50 75 100" -- ${cur}) )
            return 0
            ;;
        --preset)
            # PTZ presets
            COMPREPLY=( $(compgen -W "1 2 3 4 5 6 7 8" -- ${cur}) )
            return 0
            ;;
        *)
            # Complete options based on current command
            case "${cmd}" in
                add)
                    COMPREPLY=( $(compgen -W "--host --port" -- ${cur}) )
                    ;;
                list|status|inputs|state)
                    COMPREPLY=( $(compgen -W "--format" -- ${cur}) )
                    ;;
                cut|preview)
                    COMPREPLY=( $(compgen -W "--input" -- ${cur}) )
                    ;;
                fade)
                    COMPREPLY=( $(compgen -W "--input --duration" -- ${cur}) )
                    ;;
                transition)
                    COMPREPLY=( $(compgen -W "--type --duration --input" -- ${cur}) )
                    ;;
                overlay)
                    COMPREPLY=( $(compgen -W "--num --input --action" -- ${cur}) )
                    ;;
                *)
                    # Default: show all commands if no command entered
                    if [ ${#COMP_WORDS[@]} -eq 3 ]; then
                        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
                    fi
                    ;;
            esac
            return 0
            ;;
    esac
}

# Register completion
complete -F _if_vmix_completion if
