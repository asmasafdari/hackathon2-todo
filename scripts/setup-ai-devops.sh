#!/bin/bash
# Setup script for AI-DevOps tools (kubectl-ai, kagent, Gordon)

set -e

echo "========================================"
echo "  AI-DevOps Tools Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Install kubectl-ai
echo -e "${YELLOW}Installing kubectl-ai...${NC}"
if command_exists kubectl-ai; then
    echo -e "${GREEN}✓ kubectl-ai already installed${NC}"
    kubectl-ai version
else
    # Install kubectl-ai using krew (kubectl plugin manager)
    if command_exists kubectl-krew; then
        kubectl krew install ai
        echo -e "${GREEN}✓ kubectl-ai installed via krew${NC}"
    else
        # Manual installation
        echo "Installing krew first..."
        (
            set -x; cd "$(mktemp -d)" &&
            OS="$(uname | tr '[:upper:]' '[:lower:]')" &&
            case "$OS" in mingw*|msys*|cygwin*) OS="windows" ;; esac &&
            ARCH="$(uname -m | sed -e 's/x86_64/amd64/' -e 's/\(arm\)\(64\)\?.*/\1\2/' -e 's/aarch64$/arm64/')" &&
            KREW="krew-${OS}_${ARCH}" &&
            curl -fsSLO "https://github.com/kubernetes-sigs/krew/releases/latest/download/${KREW}.tar.gz" &&
            tar zxvf "${KREW}.tar.gz" &&
            ./"${KREW}" install krew
        )
        export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH"
        kubectl krew install ai
        echo -e "${GREEN}✓ kubectl-ai installed${NC}"
    fi
fi

echo ""

# 2. Install kagent
echo -e "${YELLOW}Installing kagent...${NC}"
if command_exists kagent; then
    echo -e "${GREEN}✓ kagent already installed${NC}"
    kagent version
else
    # Install kagent
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows
        echo "Downloading kagent for Windows..."
        curl -L -o kagent.exe https://github.com/kagent-dev/kagent/releases/latest/download/kagent_windows_amd64.exe
        chmod +x kagent.exe
        mv kagent.exe /usr/local/bin/kagent || mv kagent.exe $HOME/bin/kagent || echo "Please move kagent.exe to your PATH"
    else
        # Linux/Mac
        curl -sSL https://raw.githubusercontent.com/kagent-dev/kagent/main/install.sh | bash
    fi
    echo -e "${GREEN}✓ kagent installed${NC}"
fi

echo ""

# 3. Check Gordon (Docker AI)
echo -e "${YELLOW}Checking Gordon (Docker AI)...${NC}"
if docker ai --help >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Gordon (Docker AI) is available${NC}"
    docker ai "What can you do?"
else
    echo -e "${RED}✗ Gordon (Docker AI) not available${NC}"
    echo "To enable Gordon:"
    echo "  1. Open Docker Desktop"
    echo "  2. Go to Settings > Beta features"
    echo "  3. Toggle 'Docker AI' or 'Gordon' ON"
    echo "  4. Restart Docker Desktop"
    echo ""
    echo "Note: Gordon may not be available in all regions or Docker Desktop tiers."
    echo "If unavailable, we'll use standard Docker CLI commands."
fi

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Available AI-DevOps tools:"
command_exists kubectl-ai && echo "  ✓ kubectl-ai"
command_exists kagent && echo "  ✓ kagent"
docker ai --help >/dev/null 2>&1 && echo "  ✓ Gordon (Docker AI)"
echo ""
echo "Try these commands:"
echo "  kubectl-ai 'deploy the todo frontend'"
echo "  kagent 'check cluster health'"
echo "  docker ai 'optimize my Dockerfile'"
