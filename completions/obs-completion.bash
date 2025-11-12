#!/bin/bash
# Bash completion for if-obs CLI
#
# Installation:
#   Copy to /etc/bash_completion.d/if-obs
#   Or source in ~/.bashrc:
#     source /path/to/obs-completion.bash

_if_obs_completion() {
    local cur prev words cword
    _init_completion || return

    # Main commands
    local commands="add list test remove scene source stream record virtualcam filter media browser status stats version"

    # Scene subcommands
    local scene_commands="list switch create remove current"

    # Source subcommands
    local source_commands="list add show hide remove"

    # Stream subcommands
    local stream_commands="start stop status"

    # Record subcommands
    local record_commands="start stop status"

    # Virtual camera subcommands
    local virtualcam_commands="start stop"

    # Filter subcommands
    local filter_commands="list add remove"

    # Media subcommands
    local media_commands="add play pause stop"

    # Browser subcommands
    local browser_commands="add"

    # Get list of configured instances
    _get_obs_instances() {
        if command -v if-obs &> /dev/null; then
            if-obs list 2>/dev/null | awk 'NR>3 && NF>0 && !/^-/ {print $1}'
        fi
    }

    # Get list of scenes for an instance
    _get_obs_scenes() {
        local instance=$1
        if command -v if-obs &> /dev/null && [ -n "$instance" ]; then
            if-obs scene list "$instance" 2>/dev/null | awk 'NR>3 && NF>0 && !/^-/ {print $1}'
        fi
    }

    # Handle completion based on position
    case $cword in
        1)
            # First argument: main command
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
            ;;
        2)
            # Second argument depends on first command
            case ${words[1]} in
                add|list|test|remove|status|stats|version)
                    # Instance name for these commands
                    COMPREPLY=( $(compgen -W "$(_get_obs_instances)" -- "$cur") )
                    ;;
                scene)
                    # Scene subcommand
                    COMPREPLY=( $(compgen -W "$scene_commands" -- "$cur") )
                    ;;
                source)
                    # Source subcommand
                    COMPREPLY=( $(compgen -W "$source_commands" -- "$cur") )
                    ;;
                stream)
                    # Stream subcommand
                    COMPREPLY=( $(compgen -W "$stream_commands" -- "$cur") )
                    ;;
                record)
                    # Record subcommand
                    COMPREPLY=( $(compgen -W "$record_commands" -- "$cur") )
                    ;;
                virtualcam)
                    # Virtual camera subcommand
                    COMPREPLY=( $(compgen -W "$virtualcam_commands" -- "$cur") )
                    ;;
                filter)
                    # Filter subcommand
                    COMPREPLY=( $(compgen -W "$filter_commands" -- "$cur") )
                    ;;
                media)
                    # Media subcommand
                    COMPREPLY=( $(compgen -W "$media_commands" -- "$cur") )
                    ;;
                browser)
                    # Browser subcommand
                    COMPREPLY=( $(compgen -W "$browser_commands" -- "$cur") )
                    ;;
            esac
            ;;
        3)
            # Third argument for subcommands
            case ${words[1]} in
                scene|source|stream|record|virtualcam|filter|media|browser)
                    # Instance name for subcommands
                    COMPREPLY=( $(compgen -W "$(_get_obs_instances)" -- "$cur") )
                    ;;
            esac
            ;;
        *)
            # Handle options
            case $prev in
                --host)
                    # Suggest localhost
                    COMPREPLY=( $(compgen -W "localhost 127.0.0.1" -- "$cur") )
                    ;;
                --port)
                    # Suggest default OBS port
                    COMPREPLY=( $(compgen -W "4455" -- "$cur") )
                    ;;
                --format)
                    # Format options
                    COMPREPLY=( $(compgen -W "text json" -- "$cur") )
                    ;;
                --scene)
                    # Get instance name (varies by command structure)
                    local instance=""
                    if [[ ${words[1]} == "scene" || ${words[1]} == "source" || ${words[1]} == "media" || ${words[1]} == "browser" ]]; then
                        instance=${words[3]}
                    else
                        instance=${words[2]}
                    fi
                    # Complete with scene names
                    COMPREPLY=( $(compgen -W "$(_get_obs_scenes "$instance")" -- "$cur") )
                    ;;
                --type)
                    # Source/filter types
                    if [[ ${words[1]} == "source" ]]; then
                        COMPREPLY=( $(compgen -W "camera webcam ndi media video image browser text color" -- "$cur") )
                    elif [[ ${words[1]} == "filter" ]]; then
                        COMPREPLY=( $(compgen -W "chroma_key color_correction sharpness lut noise_reduction gain" -- "$cur") )
                    fi
                    ;;
                --width)
                    # Common widths
                    COMPREPLY=( $(compgen -W "1920 1280 854 640" -- "$cur") )
                    ;;
                --height)
                    # Common heights
                    COMPREPLY=( $(compgen -W "1080 720 480 360" -- "$cur") )
                    ;;
                --file)
                    # File completion
                    _filedir
                    ;;
                --password|--ndi-name|--source|--filter|--url)
                    # No completion for these
                    ;;
                *)
                    # Suggest common options based on command
                    local opts=""
                    case ${words[1]} in
                        add)
                            opts="--host --port --password"
                            ;;
                        list|status|stats|version)
                            opts="--format"
                            ;;
                        scene)
                            case ${words[2]} in
                                list|current)
                                    opts="--format"
                                    ;;
                                switch|create|remove)
                                    opts="--scene"
                                    ;;
                            esac
                            ;;
                        source)
                            case ${words[2]} in
                                list)
                                    opts="--scene --format"
                                    ;;
                                add)
                                    opts="--scene --source --type --ndi-name"
                                    ;;
                                show|hide|remove)
                                    opts="--scene --source"
                                    ;;
                            esac
                            ;;
                        stream)
                            case ${words[2]} in
                                status)
                                    opts="--format"
                                    ;;
                            esac
                            ;;
                        record)
                            case ${words[2]} in
                                start)
                                    opts="--file"
                                    ;;
                                status)
                                    opts="--format"
                                    ;;
                            esac
                            ;;
                        filter)
                            case ${words[2]} in
                                list)
                                    opts="--source --format"
                                    ;;
                                add)
                                    opts="--source --filter --type"
                                    ;;
                                remove)
                                    opts="--source --filter"
                                    ;;
                            esac
                            ;;
                        media)
                            case ${words[2]} in
                                add)
                                    opts="--scene --source --file --loop"
                                    ;;
                                play|pause|stop)
                                    opts="--source"
                                    ;;
                            esac
                            ;;
                        browser)
                            case ${words[2]} in
                                add)
                                    opts="--scene --source --url --width --height"
                                    ;;
                            esac
                            ;;
                    esac
                    COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
                    ;;
            esac
            ;;
    esac
}

# Register completion function
complete -F _if_obs_completion if-obs
