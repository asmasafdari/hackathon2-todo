#!/bin/bash
# Windows/Git Bash compatible setup script for AI-DevOps tools

set -e

echo "========================================"
echo "  AI-DevOps Tools Setup for Windows"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Create bin directory if it doesn't exist
BIN_DIR="$HOME/bin"
mkdir -p "$BIN_DIR"

# Function to download file
download_file() {
    local url="$1"
    local output="$2"
    
    if command -v curl &> /dev/null; then
        curl -L -o "$output" "$url"
    elif command -v wget &> /dev/null; then
        wget -O "$output" "$url"
    else
        log_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
}

# Install kubectl-ai
install_kubectl_ai() {
    log_info "Installing kubectl-ai for Windows..."
    
    cd "$TEMP"
    
    # Download Windows binary directly
    KUBECTL_AI_URL="https://github.com/kubernetes-sigs/kubectl-ai/releases/latest/download/kubectl-ai_windows_amd64.exe"
    
    log_info "Downloading kubectl-ai..."
    if download_file "$KUBECTL_AI_URL" "kubectl-ai.exe"; then
        chmod +x kubectl-ai.exe
        mv kubectl-ai.exe "$BIN_DIR/"
        log_success "kubectl-ai installed to $BIN_DIR/kubectl-ai.exe"
    else
        log_error "Failed to download kubectl-ai"
        return 1
    fi
}

# Install kagent
install_kagent() {
    log_info "Installing kagent for Windows..."
    
    cd "$TEMP"
    
    # Download kagent Windows binary
    KAGENT_URL="https://github.com/kagent-dev/kagent/releases/latest/download/kagent_windows_amd64.zip"
    
    log_info "Downloading kagent..."
    if download_file "$KAGENT_URL" "kagent.zip"; then
        # Extract using PowerShell (available on Windows)
        powershell -Command "Expand-Archive -Path 'kagent.zip' -DestinationPath '.' -Force"
        
        if [ -f "kagent.exe" ]; then
            chmod +x kagent.exe
            mv kagent.exe "$BIN_DIR/"
            log_success "kagent installed to $BIN_DIR/kagent.exe"
        else
            log_error "Failed to extract kagent.exe"
            return 1
        fi
        
        # Cleanup
        rm -f kagent.zip
    else
        log_error "Failed to download kagent"
        log_info "Please install manually from: https://github.com/kagent-dev/kagent/releases"
        return 1
    fi
}

# Check Gordon (Docker AI)
check_gordon() {
    log_info "Checking Gordon (Docker AI) availability..."
    
    if docker ai --help &> /dev/null; then
        log_success "Gordon (Docker AI) is available!"
        docker ai "What can you do?" 2>/dev/null || true
    else
        log_warn "Gordon (Docker AI) is not available"
        echo ""
        echo "To enable Gordon:"
        echo "  1. Open Docker Desktop"
        echo "  2. Go to Settings > Beta features"
        echo "  3. Toggle 'Docker AI' or 'Gordon' ON"
        echo "  4. Restart Docker Desktop"
        echo ""
        log_warn "Note: Gordon may not be available in all regions or Docker Desktop tiers."
        log_info "If unavailable, use standard Docker CLI commands."
    fi
}

# Update PATH
update_path() {
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        log_info "Adding $BIN_DIR to PATH..."
        echo ""
        echo "IMPORTANT: Please add the following to your ~/.bashrc or ~/.bash_profile:"
        echo "export PATH=\"$BIN_DIR:\$PATH\""
        echo ""
        log_info "Or run this command now:"
        echo "export PATH=\"$BIN_DIR:\$PATH\""
        echo ""
    fi
}

# Main installation
main() {
    log_info "Starting AI-DevOps tools installation..."
    echo ""
    
    # Install kubectl-ai
    if command -v kubectl-ai &> /dev/null; then
        log_success "kubectl-ai is already installed"
        kubectl-ai version 2>/dev/null || true
    else
        install_kubectl_ai || log_warn "kubectl-ai installation failed"
    fi
    
    echo ""
    
    # Install kagent
    if command -v kagent &> /dev/null; then
        log_success "kagent is already installed"
        kagent version 2>/dev/null || true
    else
        install_kagent || log_warn "kagent installation failed"
    fi
    
    echo ""
    
    # Check Gordon
    check_gordon
    
    echo ""
    
    # Update PATH
    update_path
    
    echo ""
    log_success "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Add to PATH: export PATH=\"$BIN_DIR:\$PATH\""
    echo "  2. Set OpenAI API Key: export OPENAI_API_KEY=sk-your-key-here"
    echo "  3. Deploy chatbot: ./scripts/deploy-chatbot-minikube.sh"
    echo ""
    echo "Try AI-assisted commands:"
    echo "  kubectl-ai 'check pod status' -n todo-chatbot"
    echo "  kagent 'analyze cluster health'"
    echo ""
}

# Run main function
main "$@"
