#!/bin/bash
# Build script for iOS
# This script builds the Dashy Dude iOS app

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$MOBILE_DIR")"
BUILD_DIR="$MOBILE_DIR/build"
VENV_PATH="$HOME/kivy-ios-env"

echo "=========================================="
echo "Dashy Dude iOS Build"
echo "=========================================="
echo ""
echo "Project directory: $PROJECT_DIR"
echo "Build directory: $BUILD_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    echo "Please run setup_toolchain.sh first"
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if kivy-ios is installed
if ! command -v toolchain &> /dev/null; then
    echo "Error: kivy-ios toolchain not found"
    echo "Please run setup_toolchain.sh first"
    exit 1
fi

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Parse command line arguments
BUILD_TYPE="debug"
CLEAN_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --release)
            BUILD_TYPE="release"
            shift
            ;;
        --clean)
            CLEAN_BUILD=true
            shift
            ;;
        --help)
            echo "Usage: build_ios.sh [options]"
            echo ""
            echo "Options:"
            echo "  --release    Build for release (App Store)"
            echo "  --clean      Clean build directory before building"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Clean build if requested
if [ "$CLEAN_BUILD" = true ]; then
    echo "Cleaning build directory..."
    rm -rf "$BUILD_DIR"/*
fi

# Check if toolchain is built
if [ ! -d "$BUILD_DIR/dist" ]; then
    echo "Building iOS toolchain (this may take a while)..."
    echo ""
    
    # Build Python and dependencies
    toolchain build python3 kivy
    
    # Build SDL2 for pygame compatibility
    toolchain build sdl2 sdl2_image sdl2_ttf sdl2_mixer
    
    echo ""
    echo "✓ Toolchain built successfully"
fi

# Create or update Xcode project
XCODE_PROJECT="$BUILD_DIR/DashyDude-ios"

if [ ! -d "$XCODE_PROJECT" ]; then
    echo ""
    echo "Creating Xcode project..."
    toolchain create DashyDude "$PROJECT_DIR"
    echo "✓ Xcode project created"
else
    echo ""
    echo "Updating Xcode project..."
    toolchain update DashyDude-ios
    echo "✓ Xcode project updated"
fi

# Copy iOS-specific files
echo ""
echo "Copying iOS configuration files..."

# Copy Info.plist if it exists
if [ -f "$MOBILE_DIR/ios/Info.plist" ]; then
    cp "$MOBILE_DIR/ios/Info.plist" "$XCODE_PROJECT/DashyDude/"
    echo "✓ Info.plist copied"
fi

# Copy assets if they exist
if [ -d "$MOBILE_DIR/assets/icons" ]; then
    mkdir -p "$XCODE_PROJECT/DashyDude/Assets.xcassets/AppIcon.appiconset"
    cp -r "$MOBILE_DIR/assets/icons/"* "$XCODE_PROJECT/DashyDude/Assets.xcassets/AppIcon.appiconset/" 2>/dev/null || true
    echo "✓ App icons copied"
fi

# Build the app
echo ""
echo "Building iOS app ($BUILD_TYPE)..."

cd "$XCODE_PROJECT"

if [ "$BUILD_TYPE" = "release" ]; then
    xcodebuild -project DashyDude.xcodeproj \
        -scheme DashyDude \
        -configuration Release \
        -destination 'generic/platform=iOS' \
        clean build
else
    xcodebuild -project DashyDude.xcodeproj \
        -scheme DashyDude \
        -configuration Debug \
        -destination 'platform=iOS Simulator,name=iPhone 14' \
        clean build
fi

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
echo ""

if [ "$BUILD_TYPE" = "release" ]; then
    echo "Release build created."
    echo "To submit to App Store:"
    echo "1. Open $XCODE_PROJECT/DashyDude.xcodeproj in Xcode"
    echo "2. Select 'Product' > 'Archive'"
    echo "3. Use the Organizer to upload to App Store Connect"
else
    echo "Debug build created for iOS Simulator."
    echo "To run in simulator:"
    echo "1. Open $XCODE_PROJECT/DashyDude.xcodeproj in Xcode"
    echo "2. Select an iOS Simulator"
    echo "3. Click Run (⌘R)"
fi