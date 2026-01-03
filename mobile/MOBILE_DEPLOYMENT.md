# Getting Dashy Dude on Your iPhone

This guide walks you through the complete process of deploying Dashy Dude to your iOS device.

## Prerequisites

Before you begin, you'll need:

1. **A Mac** - iOS apps can only be built on macOS
2. **Xcode** - Download from the Mac App Store (free)
3. **Apple Developer Account** - You have two options:
   - **Free Account**: Can deploy to your own device for testing (7-day expiration)
   - **Paid Account ($99/year)**: Required for App Store distribution

## Step-by-Step Guide

### Step 1: Install Xcode

1. Open the **Mac App Store**
2. Search for "Xcode"
3. Click **Get** / **Install** (it's about 12GB, so this takes a while)
4. Once installed, open Xcode and accept the license agreement
5. Install additional components when prompted

### Step 2: Install Command Line Tools

Open Terminal and run:
```bash
xcode-select --install
```

Click "Install" in the popup dialog.

### Step 3: Set Up Your Apple Developer Account

1. Go to [developer.apple.com](https://developer.apple.com)
2. Sign in with your Apple ID (or create one)
3. Accept the developer agreement

**For free account (personal testing):**
- Just signing in is enough

**For paid account (App Store):**
- Enroll in the Apple Developer Program ($99/year)

### Step 4: Configure Xcode with Your Account

1. Open **Xcode**
2. Go to **Xcode → Settings** (or Preferences)
3. Click the **Accounts** tab
4. Click the **+** button and select "Apple ID"
5. Sign in with your Apple ID

### Step 5: Install Build Dependencies

Open Terminal and run:
```bash
# Navigate to the project
cd /path/to/dashy-dude-game

# Run the setup script
./mobile/scripts/setup_toolchain.sh
```

This will install:
- Homebrew (if not installed)
- SDL2 libraries
- Python dependencies
- kivy-ios toolchain

**Note:** This step can take 30-60 minutes on first run.

### Step 6: Build the iOS Project

```bash
# Activate the virtual environment
source ~/kivy-ios-env/bin/activate

# Run the build script
./mobile/scripts/build_ios.sh
```

This creates an Xcode project at `mobile/build/DashyDude-ios/`

### Step 7: Open in Xcode

```bash
open mobile/build/DashyDude-ios/DashyDude.xcodeproj
```

Or manually:
1. Open **Xcode**
2. File → Open
3. Navigate to `mobile/build/DashyDude-ios/DashyDude.xcodeproj`

### Step 8: Configure Signing

1. In Xcode, click on **DashyDude** in the project navigator (left sidebar)
2. Select the **DashyDude** target
3. Go to the **Signing & Capabilities** tab
4. Check **Automatically manage signing**
5. Select your **Team** (your Apple ID)
6. If you see a "Bundle Identifier" error, change it to something unique like:
   - `com.yourname.dashydude`

### Step 9: Connect Your iPhone

1. Connect your iPhone to your Mac with a USB cable
2. On your iPhone, tap **Trust** when prompted
3. Enter your iPhone passcode if asked

### Step 10: Select Your Device

1. In Xcode, click the device selector (next to the Play button)
2. Select your iPhone from the list
3. If your iPhone doesn't appear:
   - Make sure it's unlocked
   - Try a different USB cable
   - Restart Xcode

### Step 11: Build and Run

1. Click the **Play** button (▶) or press **⌘R**
2. Wait for the build to complete (first build takes longer)
3. **First time only:** You'll see an error about "Untrusted Developer"

### Step 12: Trust the Developer (First Time Only)

On your iPhone:
1. Go to **Settings → General → VPN & Device Management**
   - (On older iOS: Settings → General → Profiles & Device Management)
2. Find your Apple ID under "Developer App"
3. Tap it and select **Trust**
4. Confirm by tapping **Trust** again

### Step 13: Run the App

1. Go back to Xcode and click **Play** again
2. The app should now launch on your iPhone!

## Troubleshooting

### "Unable to install app" error
- Make sure your iPhone is unlocked
- Check that you trusted the developer certificate
- Try restarting your iPhone

### "Provisioning profile" errors
- Go to Signing & Capabilities and re-select your team
- Try changing the Bundle Identifier to something unique

### App crashes on launch
- Check the Xcode console for error messages
- Make sure all assets are included in the build

### Build takes forever
- First builds are slow (compiling Python for iOS)
- Subsequent builds are much faster

### "No such module" errors
- Run the setup script again
- Make sure the virtual environment is activated

## Free Account Limitations

With a free Apple Developer account:
- Apps expire after **7 days** and need to be reinstalled
- You can only have **3 apps** installed at a time
- You can only install on devices registered to your Apple ID

To avoid these limitations, consider the $99/year Apple Developer Program.

## Alternative: TestFlight (Paid Account Only)

If you have a paid developer account, you can use TestFlight:

1. Archive your app in Xcode (Product → Archive)
2. Upload to App Store Connect
3. Add testers via TestFlight
4. Testers install via the TestFlight app

This allows testing without connecting to a Mac each time.

## Quick Reference Commands

```bash
# Setup (one time)
./mobile/scripts/setup_toolchain.sh

# Build
source ~/kivy-ios-env/bin/activate
./mobile/scripts/build_ios.sh

# Open in Xcode
open mobile/build/DashyDude-ios/DashyDude.xcodeproj
```

## Need Help?

- **Xcode issues**: [Apple Developer Forums](https://developer.apple.com/forums/)
- **kivy-ios issues**: [kivy-ios GitHub](https://github.com/kivy/kivy-ios)
- **Pygame issues**: [pygame-ce Discord](https://discord.gg/pygame)