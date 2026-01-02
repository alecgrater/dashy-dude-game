#!/bin/bash
# Setup script for iOS build toolchain
# This script installs all necessary dependencies for building Dashy Dude for iOS

set -e  # Exit on error

echo "=========================================="
echo "Dashy Dude iOS Build Setup"
echo "=========================================="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script must be run on macOS"
    exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "Error: Xcode is not installed"
    echo "Please install Xcode from the App Store"
    exit 1
fi

echo "✓ Xcode found"

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo "Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "Please complete the installation and run this script again"
    exit 1
fi

echo "✓ Xcode Command Line Tools found"

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "✓ Homebrew found"

# Install dependencies via Homebrew
echo ""
echo "Installing dependencies via Homebrew..."
brew install autoconf automake libtool pkg-config || true
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer || true

echo "✓ Homebrew dependencies installed"

# Create virtual environment for iOS building
VENV_PATH="$HOME/kivy-ios-env"

if [ ! -d "$VENV_PATH" ]; then
    echo ""
    echo "Creating virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
fi

echo "✓ Virtual environment ready"

# Activate virtual environment and install kivy-ios
echo ""
echo "Installing kivy-ios..."
source "$VENV_PATH/bin/activate"
pip install --upgrade pip
pip install cython
pip install kivy-ios

echo "✓ kivy-ios installed"

# Create build directory
BUILD_DIR="$(dirname "$0")/../build"
mkdir -p "$BUILD_DIR"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source $VENV_PATH/bin/activate"
echo ""
echo "2. Build the toolchain:"
echo "   cd $(dirname "$0")/.."
echo "   toolchain build python3 kivy"
echo "   toolchain build sdl2 sdl2_image sdl2_ttf sdl2_mixer"
echo ""
echo "3. Create the Xcode project:"
echo "   toolchain create DashyDude ../../"
echo ""
echo "4. Open the project in Xcode:"
echo "   open build/DashyDude-ios/DashyDude.xcodeproj"
echo ""