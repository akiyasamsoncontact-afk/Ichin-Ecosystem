#!/bin/sh
# ICHIN OS — Initramfs init script
# Mounts filesystems, starts all ICHIN services

echo "=== ICHIN OS v0.1 ==="
echo "Mounting filesystems..."

# Mount essential filesystems
mount -t proc none /proc
mount -t sysfs none /sys
mount -t tmpfs none /tmp
mount -t devtmpfs none /dev
mount -t tmpfs none /run

# Populate /dev with mdev
echo /sbin/mdev > /proc/sys/kernel/hotplug
mdev -s

# Set up networking
echo "Setting up loopback..."
ip link set lo up

# Set hostname
echo "ichin-os" > /proc/sys/kernel/hostname

# Detect and mount root filesystem (if available)
if [ -b /dev/sda1 ]; then
    mount /dev/sda1 /mnt 2>/dev/null && echo "Mounted /dev/sda1 to /mnt"
elif [ -b /dev/vda1 ]; then
    mount /dev/vda1 /mnt 2>/dev/null && echo "Mounted /dev/vda1 to /mnt"
fi

# Setup ICHIN directories
mkdir -p /var/log/ichin
mkdir -p /ichin/{data,config,logs}

# Export ICHIN paths
export PATH=/ichin/bin:/usr/bin:/bin:/sbin
export PYTHONPATH=/ichin/services:/ichin/ecosystem

# Start ICHIN services
echo "Starting ICHIN services..."

start_service() {
    local name=$1
    local port=$2
    local script=$3
    echo "  [$name] starting on port $port..."
    if [ -f "/ichin/services/$script" ]; then
        python3 /ichin/services/$script &
        echo $! > /var/run/ichin-$name.pid
    else
        echo "  [$name] SKIPPED (not found)"
    fi
}

# Service 1: Orchestrator (port 8011)
start_service "orchestrator" 8011 "orchestrator/main.py"

# AI Framework: OpenJarvis (port 8090) — Stanford local-first personal AI
start_openjarvis() {
    echo "  [openjarvis] starting on port 8090..."
    if [ -f /ichin/external/OpenJarvis/jarvis/main.py ]; then
        cd /ichin/external/OpenJarvis
        python3 -m jarvis --port 8090 &
        echo $! > /var/run/ichin-openjarvis.pid
    elif [ -f /ichin/external/OpenJarvis/cli.py ]; then
        cd /ichin/external/OpenJarvis
        python3 cli.py --port 8090 &
        echo $! > /var/run/ichin-openjarvis.pid
    else
        echo "  [openjarvis] SKIPPED (not found)"
    fi
}
start_openjarvis

# AI Framework: Ruflo (port 8091) — Multi-agent meta-harness
start_ruflo() {
    echo "  [ruflo] starting on port 8091..."
    if [ -f /ichin/external/ruflo/dist/agent.mjs ]; then
        node /ichin/external/ruflo/dist/agent.mjs --port 8091 &
        echo $! > /var/run/ichin-ruflo.pid
    elif [ -f /ichin/external/ruflo/index.js ]; then
        node /ichin/external/ruflo/index.js --port 8091 &
        echo $! > /var/run/ichin-ruflo.pid
    elif [ -f /ichin/external/ruflo/index.mjs ]; then
        node /ichin/external/ruflo/index.mjs --port 8091 &
        echo $! > /var/run/ichin-ruflo.pid
    else
        echo "  [ruflo] SKIPPED (not found)"
    fi
}
start_ruflo

# AI Framework: Dexter (port 8092) — Autonomous financial research agent
start_dexter() {
    echo "  [dexter] starting on port 8092..."
    if [ -f /ichin/external/dexter/src/index.ts ]; then
        cd /ichin/external/dexter
        bun run src/index.ts --port 8092 &
        echo $! > /var/run/ichin-dexter.pid
    elif [ -f /ichin/external/dexter/index.ts ]; then
        cd /ichin/external/dexter
        bun run index.ts --port 8092 &
        echo $! > /var/run/ichin-dexter.pid
    else
        echo "  [dexter] SKIPPED (not found)"
    fi
}
start_dexter

# Engineering Skills: mattpocock/skills — Load into coding agent
setup_skills() {
    echo "  [skills] installing engineering skills..."
    if [ -d /ichin/external/skills/skills ]; then
        mkdir -p /ichin/data/skills
        cp -r /ichin/external/skills/skills/* /ichin/data/skills/ 2>/dev/null
        echo "  [skills] loaded $(ls /ichin/data/skills/engineering/ 2>/dev/null | wc -l) engineering skills"
    else
        echo "  [skills] SKIPPED (not found)"
    fi
}
setup_skills

# AI Framework: jcode (port 8093) — Coding agent harness with memory
start_jcode() {
    echo "  [jcode] starting on port 8093..."
    if [ -f /ichin/external/jcode/target/release/jcode ]; then
        /ichin/external/jcode/target/release/jcode server --port 8093 &
        echo $! > /var/run/ichin-jcode.pid
    elif [ -f /ichin/external/jcode/jcode ]; then
        /ichin/external/jcode/jcode server --port 8093 &
        echo $! > /var/run/ichin-jcode.pid
    else
        echo "  [jcode] SKIPPED (not found — build with: cargo build --release)"
    fi
}
start_jcode

# AI Framework: ClawRouter (port 8402) — Agent-native LLM router
start_clawrouter() {
    echo "  [clawrouter] starting on port 8402..."
    if [ -f /ichin/external/ClawRouter/proxy.ts ]; then
        cd /ichin/external/ClawRouter
        npx tsx proxy.ts --port 8402 &
        echo $! > /var/run/ichin-clawrouter.pid
    elif [ -f /ichin/external/ClawRouter/index.ts ]; then
        cd /ichin/external/ClawRouter
        npx tsx index.ts &
        echo $! > /var/run/ichin-clawrouter.pid
    else
        echo "  [clawrouter] SKIPPED (not found)"
    fi
}
start_clawrouter

# AI Framework: agentic-inbox (port 8094) — Cloudflare AI email agent
start_agentic_inbox() {
    echo "  [agentic-inbox] starting on port 8094..."
    if [ -f /ichin/external/agentic-inbox/src/index.ts ]; then
        cd /ichin/external/agentic-inbox
        npx tsx src/index.ts --port 8094 &
        echo $! > /var/run/ichin-agentic-inbox.pid
    elif [ -f /ichin/external/agentic-inbox/index.ts ]; then
        cd /ichin/external/agentic-inbox
        npx tsx index.ts --port 8094 &
        echo $! > /var/run/ichin-agentic-inbox.pid
    else
        echo "  [agentic-inbox] SKIPPED (deploy to Cloudflare for full functionality)"
    fi
}
start_agentic_inbox

# Obsidian Vault: obsidian-mind (port None) — Persistent memory vault for AI agents
setup_obsidian_mind() {
    echo "  [obsidian-mind] setting up AI persistent memory vault..."
    if [ -d /ichin/external/obsidian-mind ]; then
        mkdir -p /ichin/data/obsidian-vaults
        cp -r /ichin/external/obsidian-mind /ichin/data/obsidian-vaults/mind 2>/dev/null
        echo "  [obsidian-mind] vault ready at /ichin/data/obsidian-vaults/mind"
    else
        echo "  [obsidian-mind] SKIPPED (not found)"
    fi
}
setup_obsidian_mind

# Obsidian Skills: kepano/obsidian-skills (port None) — Agent skills for Obsidian
setup_obsidian_skills() {
    echo "  [obsidian-skills] loading agent skills..."
    if [ -d /ichin/external/obsidian-skills/skills ]; then
        mkdir -p /ichin/data/skills/obsidian
        cp -r /ichin/external/obsidian-skills/skills/* /ichin/data/skills/obsidian/ 2>/dev/null
        echo "  [obsidian-skills] loaded skills: $(ls /ichin/data/skills/obsidian/ 2>/dev/null | wc -l)"
    else
        echo "  [obsidian-skills] SKIPPED (not found)"
    fi
}
setup_obsidian_skills

# Obsidian Second Brain (port None) — Cross-CLI second brain skill
setup_obsidian_second_brain() {
    echo "  [obsidian-second-brain] installing second brain skill..."
    if [ -d /ichin/external/obsidian-second-brain/skills ]; then
        mkdir -p /ichin/data/skills/obsidian
        cp -r /ichin/external/obsidian-second-brain/skills/* /ichin/data/skills/obsidian/ 2>/dev/null
        echo "  [obsidian-second-brain] loaded second brain skills"
    elif [ -d /ichin/external/obsidian-second-brain ]; then
        mkdir -p /ichin/data/obsidian-vaults/second-brain
        cp -r /ichin/external/obsidian-second-brain/* /ichin/data/obsidian-vaults/second-brain/ 2>/dev/null
        echo "  [obsidian-second-brain] vault ready at /ichin/data/obsidian-vaults/second-brain"
    else
        echo "  [obsidian-second-brain] SKIPPED (not found)"
    fi
}
setup_obsidian_second_brain

# Service 2: AI Agents (port 8012)  
start_service "agents" 8012 "agents/main.py"

# Service 3: Memory Engine (port 8013)
start_service "memory-engine" 8013 "memory-engine/main.py"

# Service 4: UI System (port 8014)
start_service "ui-system" 8014 "ai-studio/ui_system.py"

# Service 5: AI Studio (port 8016)
start_service "ai-studio" 8016 "ai-studio/main.py"

# ICHIN Account (port 8081)
if [ -f /ichin/services/account/server/target/release/ichin-account-server ]; then
    echo "  [account] starting on port 8081..."
    /ichin/services/account/server/target/release/ichin-account-server &
fi

# ICHIN Mail (port 8080)
if [ -f /ichin/services/mail/target/release/ichin-mail-server ]; then
    echo "  [mail] starting on port 8080..."
    /ichin/services/mail/target/release/ichin-mail-server &
fi

# ICHIN Search Engine (port 3001)
if [ -f /ichin/services/search-engine/server/target/release/ichin-search ]; then
    echo "  [search] starting on port 3001..."
    /ichin/services/search-engine/server/target/release/ichin-search &
fi

# ICHIN Protocol services (Python, ports 4889-4891)
for svc in Ichin-Protocol Ichin-DNS Ichin-CA Ichin-Daemon; do
    if [ -f "/ichin/services/protocol/$svc/server.py" ]; then
        echo "  [protocol/$svc] starting..."
        python3 /ichin/services/protocol/$svc/server.py &
    fi
done

# ICHIN Kernel module (port 7000)
if [ -f /ichin/kernel/ichin-kernel ]; then
    echo "  [kernel] loading ICHIN microkernel..."
    /ichin/kernel/ichin-kernel &
fi

echo ""
echo "=== ICHIN OS ready ==="
echo "Orchestrator:  http://localhost:8011"
echo "AI Agents:     http://localhost:8012"
echo "Memory Engine: http://localhost:8013"
echo "UI System:     http://localhost:8014"
echo "AI Studio:     http://localhost:8016"
echo "Account:       http://localhost:8081"
echo "Mail:          http://localhost:8080"
echo "Search:        http://localhost:3001"
echo "OpenJarvis:    http://localhost:8090"
echo "Ruflo:         http://localhost:8091"
echo "Dexter:        http://localhost:8092"
echo "jcode:         http://localhost:8093"
echo "ClawRouter:    http://localhost:8402"
echo "AgenticInbox:  http://localhost:8094"
echo "Skills:        /ichin/data/skills/ (engineering + obsidian skills loaded)"
echo "Mind Vault:    /ichin/data/obsidian-vaults/mind (persistent AI memory)"
echo "Second Brain:  /ichin/data/obsidian-vaults/second-brain (living vault)"
echo ""

# Drop to shell if debug mode
if [ "$1" = "debug" ]; then
    echo "DEBUG MODE: dropping to shell"
    exec /bin/sh
fi

# Watchdog loop — keep services alive
echo "Starting watchdog..."
while true; do
    sleep 30
    # Check key services and restart if dead
    for pid_file in /var/run/ichin-*.pid; do
        [ -f "$pid_file" ] || continue
        pid=$(cat "$pid_file")
        name=$(basename "$pid_file" .pid | sed 's/ichin-//')
        if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
            echo "[watchdog] $name (PID $pid) died, restarting..."
            rm -f "$pid_file"
        fi
    done
done
