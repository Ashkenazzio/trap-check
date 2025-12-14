#!/usr/bin/env bash
#
# Wrapper script to run Python with correct native library paths
#
# Usage:
#   ./scripts/run_with_libs.sh python app.py
#   ./scripts/run_with_libs.sh python -m src.rag.retriever
#   ./scripts/run_with_libs.sh python scripts/evaluation.py --rag
#
# This script auto-detects library paths for different environments (Nix, conda, standard Linux)
# You can also set TRAPCHECK_LIB_PATHS manually:
#   export TRAPCHECK_LIB_PATHS="/path/to/libs:/other/path"
#

set -e

# Function to find a library in common locations
find_lib() {
    local lib_name="$1"
    local lib_path=""

    # Check Nix store first
    if [[ -d "/nix/store" ]]; then
        lib_path=$(find /nix/store -name "${lib_name}*" -type f 2>/dev/null | head -1)
        if [[ -n "$lib_path" ]]; then
            dirname "$lib_path"
            return 0
        fi
    fi

    # Check standard Linux paths
    for dir in /usr/lib /usr/lib64 /usr/lib/x86_64-linux-gnu /lib/x86_64-linux-gnu /usr/local/lib; do
        if [[ -f "$dir/$lib_name" ]] || [[ -f "$dir/${lib_name}.6" ]] || [[ -f "$dir/${lib_name}.1" ]]; then
            echo "$dir"
            return 0
        fi
    done

    # Check conda paths
    for dir in ~/.conda/lib ~/miniconda3/lib ~/anaconda3/lib "$CONDA_PREFIX/lib"; do
        if [[ -d "$dir" ]] && [[ -f "$dir/$lib_name" || -f "$dir/${lib_name}.6" || -f "$dir/${lib_name}.1" ]]; then
            echo "$dir"
            return 0
        fi
    done

    return 1
}

# Build LD_LIBRARY_PATH
LIB_PATHS=""

# Use custom paths if set
if [[ -n "$TRAPCHECK_LIB_PATHS" ]]; then
    LIB_PATHS="$TRAPCHECK_LIB_PATHS"
else
    # Auto-detect required libraries
    LIBSTDCPP_PATH=$(find_lib "libstdc++.so" 2>/dev/null || true)
    LIBZ_PATH=$(find_lib "libz.so" 2>/dev/null || true)

    if [[ -n "$LIBSTDCPP_PATH" ]]; then
        LIB_PATHS="$LIBSTDCPP_PATH"
    fi

    if [[ -n "$LIBZ_PATH" ]]; then
        if [[ -n "$LIB_PATHS" ]]; then
            LIB_PATHS="$LIB_PATHS:$LIBZ_PATH"
        else
            LIB_PATHS="$LIBZ_PATH"
        fi
    fi
fi

# Prepend to existing LD_LIBRARY_PATH
if [[ -n "$LIB_PATHS" ]]; then
    if [[ -n "$LD_LIBRARY_PATH" ]]; then
        export LD_LIBRARY_PATH="$LIB_PATHS:$LD_LIBRARY_PATH"
    else
        export LD_LIBRARY_PATH="$LIB_PATHS"
    fi
fi

# Show what we're doing (only if verbose or no args)
if [[ "$1" == "-v" ]] || [[ "$1" == "--verbose" ]]; then
    echo "LD_LIBRARY_PATH=$LD_LIBRARY_PATH" >&2
    shift
fi

# Run the command
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [OPTIONS] <command> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 python app.py"
    echo "  $0 python -m src.rag.retriever"
    echo "  $0 python scripts/evaluation.py --name rag_test --rag"
    echo ""
    echo "Environment:"
    echo "  LD_LIBRARY_PATH=$LD_LIBRARY_PATH"
    exit 0
fi

exec "$@"
