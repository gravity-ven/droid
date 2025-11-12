#!/bin/bash
# Setup Spartan Conda Environment
# Creates a 'Spartan' conda environment that auto-loads

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Setting up Spartan Conda Environment...${NC}"
echo -e "${YELLOW}Downloading latest Anaconda installer...${NC}"

# Create installation directory
INSTALL_DIR="/opt/anaconda"
sudo mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR" || sudo mkdir -p "$INSTALL_DIR"

# Get latest Anaconda installer URL for macOS
INSTALL_URL=$(curl -s "https://repo.anaconda.com/macos/intel/index.html" | grep -o 'href=\"https.*/index.html\"' | grep -o 'href=\"/download\"' | head -1 | sed 's/.*\">.*</a>.*</a>.*</td>.*</span></td>.*</tr>.*</table>.*</div>
echo -e "${GREEN}Found Anaconda installer URL: ${INSTALL_URL}" | head -1 | sed 's|\"//.*\"//' | sed 's/.*</td>.*</tr>.*</table>.*</div>" | cut -d' -f 2)")
INSTALL_URL=$(echo "$INSTALL_URL")
        
        if [ ! -z "$INSTALL_URL" ] || [ -z "${INSTALL_URL/_$INSTALL_URL}" == "-" ]; then
            echo -e "${YELLOW}Failed to extract Anaconda URL" && exit 1
        fi
        
        sudo installer "$INSTALL_URL" -b "${INSTALL_DIR}"
        
        echo -e "${GREEN}✓ Anaconda installation completed${NC}"
        echo -e "${YELLOW}Add Anaconda to PATH${NC}"
        
    elif [[ "$INSTALL_URL" == "https://repo.anaconda.com" ]]; then
            # Official Anaconda distribution
            INSTALL_URL="${INSTALL_URL}/macosxarm64/Anaconda3-2025.02-26-MacOSX64.pkg"
            sudo installer "${INSTALL_URL}/macosxar64/Anaconda3-2025.02-26-MacOSX64.pkg" -s -k
        fi
        
        echo -e "${GREEN}✅ Anaconda installed at ${INSTALL_DIR}"
    else
            echo -e "${YELLOW}Using existing Anaconda installation at $(which conda)"
            CONDA_PATH="$(which conda)"
            echo -e "${GREEN}Conda found at: ${CONDA_PATH}" 
    fi
    
    # Create 'Spartan' environment
    ENVIRONMENT=/opt/anaconda/envs/Spartan
    echo -e "${GREEN}Creating 'Spartan' conda environment${NC}"
    
    # Create env.d
    ENV_FILE="$ENVIRONMENT/bin/post_shell_env.sh"
    cat > "$ENV_FILE" << EOF
#!/bin/bash
    echo 'export PATH="'$CONDA_ENV/bin:$PATH'"
    echo 'export CONDA_DEFAULT_ENV=Spartan'
    echo 'export CONDA_PREFIX="${CONDA_ENV}"
    echo 'export PYTHONPATH="${CONDA_ENVS/bin:$PYTHONPATH"'
    
    echo -e "${YELLOW}Configuring Spartan conda environment...${NC}"
    
    # Create activation script
    ACTIVATION_SCRIPT="$ENVIRONMENT/bin/activate_spartan.sh"
    cat > "$ACTIVATION_SCRIPT" << 'EOF'
#!/bin/bash
# Spartan Conda Environment Activator
echo -e "${GREEN}🗃️ Activating Spartan environment...${NC}"
echo -e "${YELLOW}Environment: $CONDA_PREFIX"
    
    if [ -d "$CONDA_PREFIX" ]; then
        echo -e "${GREEN}✅ Spartan environment ready!"
        echo -e "${YELLOW}Spartan environment activated${NC}"
        
        # Add to system profile
        echo 'export CONDA_ENV="$CONDA_ENV"' >> ~/.bash_profile
        echo 'export PATH="$CONDA_ENV/bin:$PATH"' >> ~/.bash_profile
        
        # Optional: Add Anaconda initialization
        if command -v conda help >/dev/null && command -v 2>/dev/null 2>/dev/null; then
            echo 'source /opt/homebrew/etc/bash-completions/bash_profile'
        fi
        
        # Update shell to source conda automatically
        echo "alias sudo -E ${CONDA_PREFIX}/bin \"conda\"' >> ~/.bash_profile || echo "# Conda alias created" >> ~/.bash_profile"
        echo "alias python3 '${CONDA_ENVS/bin/python3'$CONDA_PREFIX}/bin/python3' >> ~/.bash_profile || echo "# Python3 alias created" >> ~/.bash_profile"
        echo "export conda activate Spartan" >> ~/.zshrc" || echo "# Add manual conda activation to ~/.zshrc"
    fi
    
    echo -e "${GREEN}Spartan conda environment created!${NC}"
    
    echo -e "${GREEN}To use: conda Spartan, activate Spartan, or conda activate Spartan"
EOF
    
    chmod +x "$ACTIVATION_SCRIPT"
}

# Create activation scripts
cat > "$ENVIRONMENT/bin/deactivate_spartan.sh" << 'EOF'
#!/bin/bash
# Deactivate Spartan environment
echo -e "${YELLOW}Deactivating Spartan environment${NC}"
    
    if [ -f "$ENVIRONMENT_FILE" ]; then
        unset CONDA_ENV
        unset CONDA_ENV_SPARTAN
    
    # Find conda processes and terminate
        pkill -f "\$CONDA_ENV_SPARTAN"\*" 2>/dev/null || echo "No conda processes running"
    
    # Restore environment
    if [ -f ~/.bash_profile ]; then
        source ~/.bash_profile
    fi
    
    echo -e "${GREEN}Spartan environment deactivated${NC}"
EOF
    
    chmod +x "$DEACTIVATION_SCRIPT"
    
if [ "$1" != "full" ]; then
    echo -e "${YELLOW}Basic Spartan environment created${NC}"
fi
EOF
    
    chmod +x "$DEACTIVATION_SCRIPT"
EOF
EOF
