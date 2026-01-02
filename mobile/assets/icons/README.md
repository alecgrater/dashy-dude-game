# App Icons for iOS

This directory should contain app icons in the following sizes for iOS:

## Required Icon Sizes

### iPhone
- `icon-20@2x.png` - 40x40 (Notification)
- `icon-20@3x.png` - 60x60 (Notification)
- `icon-29@2x.png` - 58x58 (Settings)
- `icon-29@3x.png` - 87x87 (Settings)
- `icon-40@2x.png` - 80x80 (Spotlight)
- `icon-40@3x.png` - 120x120 (Spotlight)
- `icon-60@2x.png` - 120x120 (App Icon)
- `icon-60@3x.png` - 180x180 (App Icon)

### iPad
- `icon-20.png` - 20x20 (Notification)
- `icon-20@2x.png` - 40x40 (Notification)
- `icon-29.png` - 29x29 (Settings)
- `icon-29@2x.png` - 58x58 (Settings)
- `icon-40.png` - 40x40 (Spotlight)
- `icon-40@2x.png` - 80x80 (Spotlight)
- `icon-76.png` - 76x76 (App Icon)
- `icon-76@2x.png` - 152x152 (App Icon)
- `icon-83.5@2x.png` - 167x167 (iPad Pro App Icon)

### App Store
- `icon-1024.png` - 1024x1024 (App Store)

## Icon Guidelines

1. **No transparency** - iOS app icons cannot have transparent backgrounds
2. **No rounded corners** - iOS automatically applies rounded corners
3. **Simple design** - Icons should be recognizable at small sizes
4. **Consistent style** - Match the game's visual style

## Generating Icons

You can use the following tools to generate all required sizes from a single 1024x1024 source image:

### Using ImageMagick (command line)
```bash
# Install ImageMagick
brew install imagemagick

# Generate all sizes from icon-1024.png
convert icon-1024.png -resize 180x180 icon-60@3x.png
convert icon-1024.png -resize 120x120 icon-60@2x.png
convert icon-1024.png -resize 120x120 icon-40@3x.png
convert icon-1024.png -resize 87x87 icon-29@3x.png
convert icon-1024.png -resize 80x80 icon-40@2x.png
convert icon-1024.png -resize 60x60 icon-20@3x.png
convert icon-1024.png -resize 58x58 icon-29@2x.png
convert icon-1024.png -resize 40x40 icon-20@2x.png
convert icon-1024.png -resize 40x40 icon-40.png
convert icon-1024.png -resize 29x29 icon-29.png
convert icon-1024.png -resize 20x20 icon-20.png
convert icon-1024.png -resize 167x167 icon-83.5@2x.png
convert icon-1024.png -resize 152x152 icon-76@2x.png
convert icon-1024.png -resize 76x76 icon-76.png
```

### Using Online Tools
- [App Icon Generator](https://appicon.co/)
- [MakeAppIcon](https://makeappicon.com/)

## Suggested Icon Design

For Dashy Dude, consider an icon featuring:
- The player character in a dynamic pose
- Bright, eye-catching colors matching the game palette
- Simple background (solid color or gradient)
- The character's distinctive features visible at small sizes