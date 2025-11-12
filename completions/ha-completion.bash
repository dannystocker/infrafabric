#!/usr/bin/env bash
# Bash completion for if-ha (Home Assistant CLI)
#
# Installation:
#   source completions/ha-completion.bash
#   Or add to ~/.bashrc:
#   source /path/to/infrafabric/completions/ha-completion.bash

_if_ha_completion() {
    local cur prev words cword
    _init_completion || return

    # Get command line so far
    local cmd="${words[1]}"
    local subcmd="${words[2]}"

    # Available main commands
    local commands="add list test remove entities state set service camera automation script scene notify media tts event status info config"

    # Get configured instances
    local instances=""
    if [[ -f ~/.if/home-assistant/instances.yaml ]]; then
        instances=$(grep -E "^  [a-z0-9_-]+:" ~/.if/home-assistant/instances.yaml | sed 's/://g' | tr -d ' ')
    fi

    # Handle completion based on position
    case "${cword}" in
        1)
            # Complete main command
            COMPREPLY=( $(compgen -W "${commands}" -- "${cur}") )
            return 0
            ;;
        2)
            # Complete instance name for most commands
            case "${cmd}" in
                add)
                    # For 'add', complete new instance name (no suggestions)
                    return 0
                    ;;
                list)
                    # 'list' doesn't take arguments
                    COMPREPLY=( $(compgen -W "--format" -- "${cur}") )
                    return 0
                    ;;
                camera|automation|script|scene|media|event)
                    # For group commands, complete subcommand
                    case "${cmd}" in
                        camera)
                            COMPREPLY=( $(compgen -W "list snapshot stream" -- "${cur}") )
                            ;;
                        automation)
                            COMPREPLY=( $(compgen -W "list trigger enable disable" -- "${cur}") )
                            ;;
                        script)
                            COMPREPLY=( $(compgen -W "list run" -- "${cur}") )
                            ;;
                        scene)
                            COMPREPLY=( $(compgen -W "list activate" -- "${cur}") )
                            ;;
                        media)
                            COMPREPLY=( $(compgen -W "list play pause stop" -- "${cur}") )
                            ;;
                        event)
                            COMPREPLY=( $(compgen -W "fire list" -- "${cur}") )
                            ;;
                    esac
                    return 0
                    ;;
                *)
                    # Complete instance name
                    COMPREPLY=( $(compgen -W "${instances}" -- "${cur}") )
                    return 0
                    ;;
            esac
            ;;
        3)
            # Handle subcommand completions
            case "${cmd}" in
                camera|automation|script|scene|media|event)
                    # Complete instance name after subcommand
                    COMPREPLY=( $(compgen -W "${instances}" -- "${cur}") )
                    return 0
                    ;;
                entities)
                    # Complete --domain option
                    if [[ "${cur}" == -* ]]; then
                        COMPREPLY=( $(compgen -W "--domain --json" -- "${cur}") )
                    fi
                    return 0
                    ;;
                state|set|service|notify|tts)
                    # Complete entity ID (would need to query HA API)
                    if [[ "${cur}" == -* ]]; then
                        case "${cmd}" in
                            set)
                                COMPREPLY=( $(compgen -W "--state --brightness --temperature --json" -- "${cur}") )
                                ;;
                            service)
                                COMPREPLY=( $(compgen -W "--entity --brightness --temperature --data --json" -- "${cur}") )
                                ;;
                            notify)
                                COMPREPLY=( $(compgen -W "--message --title --service" -- "${cur}") )
                                ;;
                            tts)
                                COMPREPLY=( $(compgen -W "--message --language" -- "${cur}") )
                                ;;
                        esac
                    fi
                    return 0
                    ;;
                status|info|config)
                    # Complete --json flag
                    if [[ "${cur}" == -* ]]; then
                        COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                    fi
                    return 0
                    ;;
            esac
            ;;
        4)
            # Handle fourth position (entity IDs, options, etc.)
            case "${cmd}" in
                camera)
                    case "${subcmd}" in
                        snapshot|stream)
                            # Would complete entity IDs here if we cached them
                            if [[ "${cur}" == -* ]]; then
                                case "${subcmd}" in
                                    snapshot)
                                        COMPREPLY=( $(compgen -W "--file" -- "${cur}") )
                                        ;;
                                    stream)
                                        COMPREPLY=( $(compgen -W "--ndi" -- "${cur}") )
                                        ;;
                                esac
                            fi
                            ;;
                        list)
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                            fi
                            ;;
                    esac
                    return 0
                    ;;
                automation|script|scene)
                    case "${subcmd}" in
                        list)
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                            fi
                            ;;
                        trigger|enable|disable|run|activate)
                            # Would complete entity IDs here
                            if [[ "${cur}" == -* ]]; then
                                if [[ "${subcmd}" == "run" ]]; then
                                    COMPREPLY=( $(compgen -W "--variables" -- "${cur}") )
                                fi
                            fi
                            ;;
                    esac
                    return 0
                    ;;
                media)
                    case "${subcmd}" in
                        list)
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                            fi
                            ;;
                        play)
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--url" -- "${cur}") )
                            fi
                            ;;
                    esac
                    return 0
                    ;;
                event)
                    case "${subcmd}" in
                        fire)
                            # Complete event type
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--data" -- "${cur}") )
                            fi
                            ;;
                        list)
                            if [[ "${cur}" == -* ]]; then
                                COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                            fi
                            ;;
                    esac
                    return 0
                    ;;
            esac
            ;;
        *)
            # Complete options for any position
            if [[ "${cur}" == -* ]]; then
                case "${cmd}" in
                    add)
                        COMPREPLY=( $(compgen -W "--url --token" -- "${cur}") )
                        ;;
                    entities)
                        COMPREPLY=( $(compgen -W "--domain --json" -- "${cur}") )
                        ;;
                    state)
                        COMPREPLY=( $(compgen -W "--json" -- "${cur}") )
                        ;;
                    set)
                        COMPREPLY=( $(compgen -W "--state --brightness --temperature --json" -- "${cur}") )
                        ;;
                    service)
                        COMPREPLY=( $(compgen -W "--entity --brightness --temperature --data --json" -- "${cur}") )
                        ;;
                    notify)
                        COMPREPLY=( $(compgen -W "--message --title --service" -- "${cur}") )
                        ;;
                    tts)
                        COMPREPLY=( $(compgen -W "--message --language" -- "${cur}") )
                        ;;
                    *)
                        COMPREPLY=( $(compgen -W "--json --format" -- "${cur}") )
                        ;;
                esac
            fi
            return 0
            ;;
    esac
}

# Register completion function
complete -F _if_ha_completion if-ha

# Completion for common domains (for --domain flag)
_if_ha_domains="light switch sensor binary_sensor climate camera automation script scene media_player lock cover fan"

# Helper: Complete entity domains
_if_ha_complete_domain() {
    local cur="${1}"
    COMPREPLY=( $(compgen -W "${_if_ha_domains}" -- "${cur}") )
}

# Helper: Complete state values
_if_ha_complete_state() {
    local cur="${1}"
    COMPREPLY=( $(compgen -W "on off" -- "${cur}") )
}

# Enable completion debugging (optional)
# export _COMPLETION_DEBUG=1
