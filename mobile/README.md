# Mobile Deployment for Dashy Dude

This directory contains configuration and tools for building Dashy Dude as an iOS app.

## Overview

There are two main approaches for deploying a Pygame game to iOS:

### Option 1: Kivy + python-for-ios (Recommended)
- Uses Kivy's python-for-ios toolchain
- Requires converting Pygame code to Kivy
- Best for production iOS apps

### Option 2: Pygame Subset for Android (pgs4a) / pygame-ce-ios
- Experimental support for iOS
- May have limitations

## Prerequisites

### macOS Requirements
- macOS 10.15 or later
- Xcode 12+ with Command Line Tools
- Python 3.9+ (via pyenv or homebrew)
- Homebrew package manager

### Install Required Tools

```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install autoconf automake libtool pkg-config
brew install sdl2 sdl2_image sdl2_ttf sdl2_mixer

# Install Cython (required for building)
pip install cython
```

## Option 1: Using Kivy (Recommended)

### Step 1: Install kivy-ios

```bash
# Create a virtual environment for iOS building
python3 -m venv ~/kivy-ios-env
source ~/kivy-ios-env/bin/activate

# Install kivy-ios
pip install kivy-ios
```

### Step 2: Build the toolchain

```bash
# Navigate to mobile directory
cd mobile

# Build Python for iOS
toolchain build python3 kivy

# Build SDL2 (for pygame compatibility layer)
toolchain build sdl2 sdl2_image sdl2_ttf sdl2_mixer
```

### Step 3: Create Xcode Project

```bash
# Create the iOS project
toolchain create DashyDude ../

# This creates an Xcode project in mobile/DashyDude-ios/
```

### Step 4: Build and Run

1. Open `mobile/DashyDude-ios/DashyDude.xcodeproj` in Xcode
2. Select your target device or simulator
3. Click Run (⌘R)

## Option 2: Using BeeWare Briefcase

### Step 1: Install Briefcase

```bash
pip install briefcase
```

### Step 2: Initialize iOS Project

```bash
cd ..  # Go to project root
briefcase create iOS
```

### Step 3: Build and Run

```bash
briefcase build iOS
briefcase run iOS
```

## Project Structure for Mobile

```
mobile/
├── README.md              # This file
├── ios/
│   ├── Info.plist         # iOS app configuration
│   ├── LaunchScreen.storyboard
│   └── Assets.xcassets/   # App icons and images
├── config/
│   ├── mobile_constants.py  # Mobile-specific settings
│   └── touch_controls.py    # Touch input handling
├── scripts/
│   ├── build_ios.sh       # Build script for iOS
│   └── setup_toolchain.sh # Setup script
└── assets/
    └── icons/             # App icons for iOS
```

## Mobile-Specific Considerations

### Screen Resolution
- iPhone SE: 750 x 1334 (375 x 667 points)
- iPhone 14: 1170 x 2532 (390 x 844 points)
- iPhone 14 Pro Max: 1290 x 2796 (430 x 932 points)
- iPad: Various resolutions

The game should adapt to different screen sizes. See `config/mobile_constants.py`.

### Touch Controls
- Tap anywhere: Jump
- Hold: Helicopter glide
- Swipe up: Double jump (alternative)

### Performance
- Target 60 FPS on iPhone 8 and newer
- Reduce particle effects on older devices
- Use texture atlases for better performance

### App Store Requirements
- App icons in all required sizes
- Launch screen
- Privacy policy (if collecting any data)
- Age rating

## Troubleshooting

### Common Issues

1. **Build fails with "No module named 'pygame'"**
   - Ensure SDL2 libraries are built first
   - Check that pygame is in the requirements

2. **App crashes on launch**
   - Check Xcode console for error messages
   - Verify all assets are included in the bundle

3. **Touch input not working**
   - Ensure touch_controls.py is properly integrated
   - Check event handling in game loop

### Getting Help

- Kivy-ios documentation: https://kivy.org/doc/stable/guide/packaging-ios.html
- BeeWare documentation: https://briefcase.readthedocs.io/
- Pygame-ce documentation: https://pyga.me/docs/

## Next Steps

1. [ ] Convert input handling to support touch
2. [ ] Add mobile-specific UI scaling
3. [ ] Create app icons and launch screens
4. [ ] Test on iOS Simulator
5. [ ] Test on physical device
6. [ ] Prepare for App Store submission