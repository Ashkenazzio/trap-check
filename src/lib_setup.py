"""
Library path setup for native dependencies (ChromaDB, sentence-transformers, etc.)

This module handles the LD_LIBRARY_PATH configuration needed for native libraries
in various environments (Nix, conda, standard Linux, etc.)

IMPORTANT: LD_LIBRARY_PATH must be set BEFORE Python starts to affect native
library loading. This module provides tools to:
1. Detect required library paths
2. Generate shell export commands
3. Auto-restart Python with correct paths (optional)

Usage:
    # Option 1: Source the generated exports before running Python
    $ eval $(python -m src.lib_setup --export)
    $ python app.py

    # Option 2: Use the wrapper script
    $ ./scripts/run_with_libs.sh python app.py

    # Option 3: Auto-restart (restarts Python with correct LD_LIBRARY_PATH)
    from src.lib_setup import ensure_library_paths
    ensure_library_paths()  # May restart the process

    # Option 4: Set environment variable manually
    $ export TRAPCHECK_LIB_PATHS="/path1:/path2"
    $ python app.py

Environment Variables:
    TRAPCHECK_LIB_PATHS: Colon-separated list of additional library paths
    TRAPCHECK_SKIP_LIB_SETUP: Set to "1" to skip automatic library setup
    TRAPCHECK_LIBS_CONFIGURED: Set automatically after restart to prevent loops
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


# Libraries we need for RAG functionality
REQUIRED_LIBS = ["libz.so", "libstdc++.so"]

# Default search locations for different environments
DEFAULT_SEARCH_PATHS = [
    # Nix store (common patterns)
    "/nix/store/*/lib",
    # Standard Linux
    "/usr/lib",
    "/usr/lib64",
    "/usr/lib/x86_64-linux-gnu",
    "/lib/x86_64-linux-gnu",
    # Conda/Miniconda
    "~/.conda/lib",
    "~/miniconda3/lib",
    "~/anaconda3/lib",
    # Homebrew (Linux)
    "/home/linuxbrew/.linuxbrew/lib",
    # Local installations
    "/usr/local/lib",
]


def _find_nix_lib(lib_pattern: str) -> Optional[str]:
    """Find a library in the Nix store using find command."""
    try:
        result = subprocess.run(
            ["find", "/nix/store", "-name", f"{lib_pattern}*", "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # Get the first match and return its directory
            lib_path = result.stdout.strip().split("\n")[0]
            return str(Path(lib_path).parent)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def _find_lib_in_path(lib_name: str, search_path: str) -> Optional[str]:
    """Check if a library exists in a given path (supports glob patterns)."""
    from glob import glob

    expanded_path = os.path.expanduser(search_path)

    # Handle glob patterns in path
    if "*" in expanded_path:
        matching_dirs = glob(expanded_path)
        for dir_path in matching_dirs:
            if Path(dir_path).is_dir():
                for lib_file in Path(dir_path).glob(f"{lib_name}*"):
                    if lib_file.is_file():
                        return str(lib_file.parent)
    else:
        dir_path = Path(expanded_path)
        if dir_path.is_dir():
            for lib_file in dir_path.glob(f"{lib_name}*"):
                if lib_file.is_file():
                    return str(lib_file.parent)
    return None


def _detect_environment() -> str:
    """Detect the current environment type."""
    if os.path.exists("/nix/store"):
        return "nix"
    elif os.environ.get("CONDA_PREFIX"):
        return "conda"
    elif Path("/home/linuxbrew/.linuxbrew").exists():
        return "linuxbrew"
    else:
        return "standard"


def find_required_libraries() -> dict[str, Optional[str]]:
    """Find all required libraries and return their paths."""
    found_libs = {}
    env_type = _detect_environment()

    for lib in REQUIRED_LIBS:
        lib_path = None

        # For Nix, use find command for better results
        if env_type == "nix":
            lib_path = _find_nix_lib(lib)

        # Fall back to searching default paths
        if not lib_path:
            for search_path in DEFAULT_SEARCH_PATHS:
                lib_path = _find_lib_in_path(lib, search_path)
                if lib_path:
                    break

        found_libs[lib] = lib_path

    return found_libs


def setup_library_paths(
    custom_paths: Optional[list[str]] = None,
    verbose: bool = False
) -> bool:
    """
    Configure LD_LIBRARY_PATH for native dependencies.

    Args:
        custom_paths: Additional library paths to add
        verbose: Print debug information

    Returns:
        True if setup was successful, False otherwise
    """
    # Check if setup should be skipped
    if os.environ.get("TRAPCHECK_SKIP_LIB_SETUP") == "1":
        if verbose:
            print("[lib_setup] Skipping library setup (TRAPCHECK_SKIP_LIB_SETUP=1)")
        return True

    # Collect all library paths
    lib_paths = []

    # 1. Add custom paths from environment variable
    env_paths = os.environ.get("TRAPCHECK_LIB_PATHS", "")
    if env_paths:
        lib_paths.extend(env_paths.split(":"))
        if verbose:
            print(f"[lib_setup] Using TRAPCHECK_LIB_PATHS: {env_paths}")

    # 2. Add custom paths from argument
    if custom_paths:
        lib_paths.extend(custom_paths)
        if verbose:
            print(f"[lib_setup] Using custom paths: {custom_paths}")

    # 3. Auto-detect required libraries
    if not lib_paths:
        if verbose:
            print(f"[lib_setup] Auto-detecting libraries for {_detect_environment()} environment...")

        found = find_required_libraries()
        for lib, path in found.items():
            if path:
                if path not in lib_paths:
                    lib_paths.append(path)
                if verbose:
                    print(f"[lib_setup] Found {lib}: {path}")
            elif verbose:
                print(f"[lib_setup] WARNING: {lib} not found")

    # 4. Update LD_LIBRARY_PATH
    if lib_paths:
        current = os.environ.get("LD_LIBRARY_PATH", "")
        new_paths = ":".join(lib_paths)

        if current:
            os.environ["LD_LIBRARY_PATH"] = f"{new_paths}:{current}"
        else:
            os.environ["LD_LIBRARY_PATH"] = new_paths

        if verbose:
            print(f"[lib_setup] LD_LIBRARY_PATH updated: {os.environ['LD_LIBRARY_PATH']}")

        return True

    return False


def get_library_path_string() -> str:
    """
    Get the LD_LIBRARY_PATH string needed for native dependencies.

    Returns:
        Colon-separated library path string
    """
    found = find_required_libraries()
    paths = [path for path in found.values() if path]
    return ":".join(paths)


def get_export_command() -> str:
    """
    Generate shell export command for library paths.

    Returns:
        Shell command string like: export LD_LIBRARY_PATH="/path1:/path2:$LD_LIBRARY_PATH"
    """
    lib_paths = get_library_path_string()
    if lib_paths:
        return f'export LD_LIBRARY_PATH="{lib_paths}:$LD_LIBRARY_PATH"'
    return ""


def ensure_library_paths(verbose: bool = False, allow_restart: bool = True) -> bool:
    """
    Ensure library paths are set, optionally restarting Python if necessary.

    This function checks if libraries can be loaded. If not, and if restart is
    allowed, it will re-exec the Python process with correct LD_LIBRARY_PATH.

    On systems where native libraries work correctly (standard Linux, conda),
    this function is a no-op and returns immediately.

    Args:
        verbose: Print debug information
        allow_restart: If True, may restart the Python process (default: True)
                      Set to False to just check without restarting

    Returns:
        True if libraries are working, False if restart was needed but not allowed
    """
    # Check if we've already configured (prevent restart loops)
    if os.environ.get("TRAPCHECK_LIBS_CONFIGURED") == "1":
        if verbose:
            print("[lib_setup] Libraries already configured")
        return True

    # Check if skip is requested
    if os.environ.get("TRAPCHECK_SKIP_LIB_SETUP") == "1":
        if verbose:
            print("[lib_setup] Skipping library setup (TRAPCHECK_SKIP_LIB_SETUP=1)")
        return True

    # Try to import numpy to test if libs are working
    # On most systems (Ubuntu, Fedora, conda), this will succeed immediately
    try:
        import numpy
        if verbose:
            print("[lib_setup] Libraries already working (no setup needed)")
        os.environ["TRAPCHECK_LIBS_CONFIGURED"] = "1"
        return True
    except ImportError as e:
        if verbose:
            print(f"[lib_setup] numpy import failed: {e}")

    # Libraries not working - need to configure paths
    lib_paths = get_library_path_string()
    if not lib_paths:
        if verbose:
            print("[lib_setup] Could not find required libraries - they may need to be installed")
        return False

    # Update environment
    current = os.environ.get("LD_LIBRARY_PATH", "")
    if current:
        os.environ["LD_LIBRARY_PATH"] = f"{lib_paths}:{current}"
    else:
        os.environ["LD_LIBRARY_PATH"] = lib_paths

    # Mark as configured to prevent loops
    os.environ["TRAPCHECK_LIBS_CONFIGURED"] = "1"

    if not allow_restart:
        if verbose:
            print(f"[lib_setup] LD_LIBRARY_PATH set but restart not allowed")
            print(f"[lib_setup] Use: ./scripts/run_with_libs.sh python ...")
        return False

    # Check if we can safely restart (not running with -c or in interactive mode)
    if not sys.argv[0] or sys.argv[0] == '-c':
        if verbose:
            print("[lib_setup] Cannot restart in this context (python -c or interactive)")
            print("[lib_setup] Use: ./scripts/run_with_libs.sh python ...")
        return False

    if verbose:
        print(f"[lib_setup] Restarting with LD_LIBRARY_PATH={os.environ['LD_LIBRARY_PATH']}")

    # Re-exec the same Python script with same arguments
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except OSError as e:
        if verbose:
            print(f"[lib_setup] Restart failed: {e}")
        return False

    return True  # Should not reach here after successful execv


def verify_imports() -> dict[str, bool]:
    """
    Verify that required imports work after library setup.

    Returns:
        Dict mapping module names to import success status
    """
    results = {}

    modules_to_check = [
        ("numpy", "numpy"),
        ("chromadb", "chromadb"),
        ("sentence_transformers", "sentence-transformers"),
    ]

    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            results[display_name] = True
        except ImportError as e:
            results[display_name] = False

    return results


def print_setup_help():
    """Print help for configuring library paths."""
    print("""
TrapCheck Library Setup Help
============================

If you're seeing import errors for numpy, chromadb, or sentence-transformers,
you may need to configure library paths for your environment.

Options:
--------

1. Set TRAPCHECK_LIB_PATHS environment variable:
   export TRAPCHECK_LIB_PATHS="/path/to/libz:/path/to/libstdc++"
   python app.py

2. For Nix environments, find and set paths:
   # Find libraries
   find /nix/store -name "libz.so.1" 2>/dev/null | head -1
   find /nix/store -name "libstdc++.so.6" 2>/dev/null | head -1

   # Set paths (use the directory containing the library)
   export TRAPCHECK_LIB_PATHS="/nix/store/.../lib:/nix/store/.../lib"

3. Skip automatic setup if your system handles libraries correctly:
   export TRAPCHECK_SKIP_LIB_SETUP=1

4. Use conda/mamba which bundles native dependencies:
   conda create -n trapcheck python=3.12
   conda activate trapcheck
   pip install -r requirements.txt

Current Environment:
-------------------
""")
    env_type = _detect_environment()
    print(f"  Environment type: {env_type}")
    print(f"  LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', '(not set)')}")
    print(f"  TRAPCHECK_LIB_PATHS: {os.environ.get('TRAPCHECK_LIB_PATHS', '(not set)')}")

    print("\nLibrary Detection:")
    found = find_required_libraries()
    for lib, path in found.items():
        status = f"✓ {path}" if path else "✗ NOT FOUND"
        print(f"  {lib}: {status}")

    print("\nImport Verification:")
    results = verify_imports()
    for module, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {module}: {status}")


# Auto-setup when imported (can be disabled with TRAPCHECK_SKIP_LIB_SETUP=1)
if os.environ.get("TRAPCHECK_SKIP_LIB_SETUP") != "1":
    _auto_setup_done = setup_library_paths(verbose=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TrapCheck library path setup utility")
    parser.add_argument("--verify", action="store_true", help="Verify imports work (restarts if needed)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--help-setup", action="store_true", help="Print setup help")
    parser.add_argument("--find-libs", action="store_true", help="Find required libraries")
    parser.add_argument("--export", action="store_true", help="Print shell export command (use with eval)")

    args = parser.parse_args()

    if args.export:
        # Print just the export command for shell integration
        # Usage: eval $(python -m src.lib_setup --export)
        cmd = get_export_command()
        if cmd:
            print(cmd)
        sys.exit(0)
    elif args.help_setup:
        print_setup_help()
    elif args.find_libs:
        print("Searching for required libraries...", file=sys.stderr)
        found = find_required_libraries()
        for lib, path in found.items():
            if path:
                print(f"  {lib}: {path}")
            else:
                print(f"  {lib}: NOT FOUND")
    elif args.verify:
        # Use ensure_library_paths which will restart if needed
        ensure_library_paths(verbose=args.verbose)

        # If we get here, libraries should work
        print("Verifying imports...")
        results = verify_imports()
        all_ok = True
        for module, success in results.items():
            status = "✓ OK" if success else "✗ FAILED"
            print(f"  {module}: {status}")
            if not success:
                all_ok = False

        if all_ok:
            print("\nAll imports successful!")
            sys.exit(0)
        else:
            print("\nSome imports failed. Run with --help-setup for guidance.")
            sys.exit(1)
    else:
        # Default: show detected paths and export command
        print("TrapCheck Library Setup")
        print("=" * 50)
        print(f"\nEnvironment: {_detect_environment()}")
        print("\nDetected library paths:")
        found = find_required_libraries()
        for lib, path in found.items():
            status = f"✓ {path}" if path else "✗ NOT FOUND"
            print(f"  {lib}: {status}")

        export_cmd = get_export_command()
        if export_cmd:
            print(f"\nTo configure your shell, run:")
            print(f"  eval $(python -m src.lib_setup --export)")
            print(f"\nOr add to your shell config:")
            print(f"  {export_cmd}")
            print(f"\nTo verify setup works:")
            print(f"  python -m src.lib_setup --verify")
