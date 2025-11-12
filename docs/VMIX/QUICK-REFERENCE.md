# IF.vmix Quick Reference

**vMix CLI Cheat Sheet** - Keep this handy during production!

---

## Setup (One-Time)

```bash
# Add your vMix instance
if vmix add myvmix --host 192.168.1.100 --port 8088

# Test connection
if vmix test myvmix
```

---

## Production Control (Most Common)

```bash
# Instant cut
if vmix cut myvmix --input 1

# Fade (2 seconds)
if vmix fade myvmix --input 2 --duration 2000

# Set preview
if vmix preview myvmix --input 3

# Custom transition
if vmix transition myvmix --type Merge --duration 1000

# Add overlay
if vmix overlay myvmix --num 1 --input 4
```

---

## Status Queries

```bash
# Overall status
if vmix status myvmix

# List all inputs
if vmix inputs myvmix

# Current state (active/preview)
if vmix state myvmix
```

---

## Streaming

```bash
# Start stream (pre-configured)
if vmix stream start myvmix

# Start with RTMP URL
if vmix stream start myvmix --rtmp rtmp://server/live --key abc123

# Stop stream
if vmix stream stop myvmix

# Check status
if vmix stream status myvmix
```

---

## Recording

```bash
# Start recording
if vmix record start myvmix

# Start with filename
if vmix record start myvmix --file "Event_2025-11-11.mp4"

# Stop recording
if vmix record stop myvmix

# Check status
if vmix record status myvmix
```

---

## NDI Sources

```bash
# Add NDI source
if vmix ndi add myvmix --source "Camera 1 (192.168.1.50)"

# List NDI inputs
if vmix ndi list myvmix

# Remove input
if vmix ndi remove myvmix --input 5
```

---

## PTZ Camera Control

```bash
# Move camera
if vmix ptz move myvmix --input 1 --pan 50 --tilt 30 --zoom 80

# Recall preset
if vmix ptz preset myvmix --input 1 --preset 3

# Home position
if vmix ptz home myvmix --input 1
```

---

## Audio Control

```bash
# Set volume
if vmix audio volume myvmix --input 1 --volume 75

# Mute
if vmix audio mute myvmix --input 1

# Unmute
if vmix audio unmute myvmix --input 1
```

---

## Instance Management

```bash
# List instances
if vmix list

# Test connection
if vmix test myvmix

# Remove instance
if vmix remove myvmix
```

---

## Common Values

**Input numbers:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ...

**Transition types:** Fade, Merge, Wipe, Zoom, Stinger

**Duration:** milliseconds (500, 1000, 2000, 3000)

**Overlay numbers:** 1, 2, 3, 4

**Stream channels:** 0, 1, 2

**Volume:** 0-100

**Pan/Tilt:** -100 to 100

**Zoom:** 0 to 100

---

## Keyboard Shortcuts

Enable tab completion for faster entry:

```bash
if vmix <TAB>                    # Show all commands
if vmix cut my<TAB>             # Complete instance name
if vmix cut myvmix --inp<TAB>  # Complete --input option
```

---

## Output Formats

Most commands support `--format` option:

```bash
if vmix status myvmix --format json
if vmix inputs myvmix --format json
if vmix list --format json
```

---

## IF.witness Logging

All operations are automatically logged:

```bash
# View vMix logs
if witness query --component IF.vmix

# View specific instance
if witness query --component IF.vmix --filter "instance:myvmix"

# View specific operation
if witness query --component IF.vmix --filter "event:vmix_cut"
```

---

## Troubleshooting

**Connection failed?**
```bash
# Check vMix is running
if vmix test myvmix

# Verify host/port
curl http://192.168.1.100:8088/api/
```

**Instance not found?**
```bash
# List instances
if vmix list

# Check config
cat ~/.if/vmix/instances.yaml
```

**Input doesn't exist?**
```bash
# List all inputs
if vmix inputs myvmix
```

---

## Emergency Commands

```bash
# Quick status check
if vmix status myvmix

# Stop everything
if vmix record stop myvmix
if vmix stream stop myvmix

# Cut to safe input (e.g., holding slide)
if vmix cut myvmix --input 1
```

---

## Automation Tips

**Create aliases:**
```bash
alias vmix-cut1='if vmix cut myvmix --input 1'
alias vmix-cut2='if vmix cut myvmix --input 2'
alias vmix-rec-start='if vmix record start myvmix'
alias vmix-rec-stop='if vmix record stop myvmix'
```

**Use shell scripts:**
```bash
#!/bin/bash
# show.sh - Automated show sequence
if vmix cut myvmix --input 1
sleep 5
if vmix fade myvmix --input 2 --duration 2000
sleep 10
if vmix cut myvmix --input 1
```

**Monitor status:**
```bash
watch -n 2 'if vmix status myvmix'
```

---

## Help

```bash
# General help
if vmix --help

# Command help
if vmix cut --help
if vmix stream --help
if vmix ptz --help
```

---

**Print this page and keep it at your production desk!**

*IF.vmix - Dead-simple vMix control for production engineers*
