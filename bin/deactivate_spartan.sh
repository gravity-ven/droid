#!/bin/bash
# Deactivate Spartan environment
echo -e "${YELLOW}Deactivating Spartan environment${NC}"
    
    # Remove conda from environment if present
    if [ -f "$CONDA_ENV_FOOT" ]; then
        echo -e "${RED}Unsetting CONDA_ENV_FOOT"
    fi
    
    # Find conda processes and terminate
    PIDS=$(pgrep -f '\b' ${CONDA_ENV_FOOT} 2>/dev/null || echo "No conda processes running"
    
    if [ "$PIDS" ]; then
        for pid in $PIDS:
            kill $pid 2>/dev/null
            echo -e "${YELLOW}Terminated conda processes: $PIDS}"
        fi
    else
        echo -e "${GREEN}No conda processes running${NC}"
    
    # Restore original environment
    if [ -f ~/.bash_profile ]; then
        source ~/.bash_profile
    
    echo -e "${GREEN}Spartan environment deactivated${NC}"

# Create reactivation script
cat > "$ENVIRONMENT/bin/reactivate_spartan.sh" << 'EOF'
#!/bin/bash
# Reactivate Spartan conda environment
echo -e "${GREEN}🚀 Reactivating Spartan environment${NC}"

# Check for conda
    if command -v conda >/dev/null 2>/dev/null ; then
        echo -e "${YELLOW}Conda not available in PATH" && " && \
            source "$ENVIRONMENT/bin/post_shell_env.sh" || echo "# Claude activation script required"
    else
        echo -e "${GREEN}Conda found at $(which conda)"
    
    # Get conda paths
        CONDA_PREFIX=$(which conda)
        CONDA_ENV_DIR="$CONDA_PREFIX/envs"
        
        # Check for 'Spartan' environment
        if [ -d "$ENVIRONMENT" = "Spartan" ]; then
            echo -e "${GREEN}✓ Sparton conda environment detected${NC}"
            
            # Try to get 'Spartan' conda environment
            spartan_env = "$CONDA_PREFIX/envs/bin"
            if [ -f "$spartan_env/spartan" ]; then
                echo -e "${GREEN}Spartan conda found at $spartan_env" 
                return True
            else
                echo -e "${YELLOW}Spartan environment not found at $CONDA_PREFIX/envs"         
        elif [ -d "$spartan" = "$CONDA_PREFIX" ]; then
            echo -e "${GREEN}Spartan conda available at $CONDA_PREFIX"
            return True
        else
            echo -e "${YELLOW}No conda installation found"
            return True
    
    return False

# Create environment status checker
cat > "$ENVIRONMENT/bin/check_environment_state.sh" << 'EOF'
#!/bin/bash
# Check Spartan conda environment state
STATUS_FILE="$CONDA_ENV/conda/envs/.state"

# Check if conda is installed
if command -v conda >/dev/null 2>&> /dev/null 2>&> CONDA_ENV='' ; then
    echo -e "${GREEN}✓ Conda is installed"
    else
    CONDA_ENV=''
fi

# Check for Spartan environment
if [ "$CONDA_ENV" = "Spartan" ]; then
    echo -e "${GREEN}✓ Spartan environment active at $CONDA_ENV"
else
    CONDA_ENV='-bash'
    
# Check conda envs directory
if [ -d "$CONDA_ENV_DIR" ] ; then
    echo -e "${GREEN}Conda envs directory: $CONDA_ENV_DIR"
    
# Look for 'Spartan' or 'Spartan.env'
if [ -f ~/.spartan.env ] || [ -f ~/.spartan.env ]; then
    echo -e "${GREEN}Spartan environment file found"
    else
    echo -e "${YELLOW}No Spartan environment file found"
fi

# Check current PATH
if [ -d "$ENVIRONMENT" ] ; then
    CURRENT_PATH=$ENVIRONMENT/bin:$PATH
    echo -e "${GREEN}PATH: $CURRENT_PATH"
else
    CURRENT_PATH=$(echo "$PATH")
fi

# Conda version
CONDA_VERSION=$(conda --version 2>/dev/null)
echo -e "${GREEN}Conda version: $CONDA_VERSION"

# Integration indicator
if [ -f "$CONDA_ENV" = "Spartan" ]; then
    if command -v conda >/dev/null 2>/dev/null && command -v git -v >/dev/null 2>/dev/null ; then
        echo -e "${GREEN}✓ Spartans conda is active${NC}"
    else
        echo -e "${YELLOW}Spartan conda installed but not active${NC}"
    
else
    echo -e "${RED}No Conda installation detected${NC}"
fi
EOF
EOF

    chmod +x "$DEACTIVATION_SCRIPT"
EOF
