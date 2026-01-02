# Deploying Dashy Dude to the Web

This guide explains how to host Dashy Dude online so people can play it in a browser.

## Option 1: Pygbag (Recommended - Easiest)

Pygbag compiles your Pygame game to WebAssembly, allowing it to run directly in browsers.

### Step 1: Install Pygbag

```bash
uv add pygbag
# or
pip install pygbag
```

### Step 2: Build for Web

From the project root directory, run:

```bash
pygbag main.py
```

This will:
1. Start a local development server at `http://localhost:8000`
2. Build the game to the `build/web` folder

### Step 3: Test Locally

Open `http://localhost:8000` in your browser to test the game.

### Step 4: Deploy to itch.io (Free Hosting)

1. **Create an itch.io account** at https://itch.io
2. **Create a new project** → Choose "HTML" as the kind of project
3. **Build for production**:
   ```bash
   pygbag --build main.py
   ```
4. **Zip the build folder**: Compress the contents of `build/web/`
5. **Upload to itch.io**: Upload the zip file and check "This file will be played in the browser"
6. **Set viewport size**: 800x600 (or your game's resolution)
7. **Publish!**

### Step 5: Share Your Game

Your game will be available at: `https://yourusername.itch.io/dashy-dude`

---

## Option 2: GitHub Pages (Free)

After building with Pygbag:

1. Create a GitHub repository
2. Copy the contents of `build/web/` to the repository
3. Enable GitHub Pages in repository settings
4. Your game will be at: `https://yourusername.github.io/repository-name/`

---

## Option 3: Replit

1. Create a Replit account at https://replit.com
2. Create a new Python repl
3. Upload your game files
4. Replit will automatically host it with a shareable URL

---

## Troubleshooting

### Game doesn't load in browser
- Make sure all assets are in the correct paths
- Check browser console for errors (F12 → Console)
- Ensure `await asyncio.sleep(0)` is in your main game loop

### Sound doesn't work
- Browsers require user interaction before playing audio
- The game should work after the user clicks/taps

### Performance issues
- WebAssembly is slower than native Python
- Consider reducing particle effects or simplifying graphics for web

---

## File Structure for Web Build

```
build/
└── web/
    ├── index.html      # Main HTML file
    ├── main.js         # JavaScript loader
    ├── main.wasm       # WebAssembly binary
    └── assets/         # Game assets
```

---

## Quick Commands Reference

```bash
# Install pygbag
uv add pygbag

# Run development server (builds and serves)
pygbag main.py

# Build for production only
pygbag --build main.py

# Build with custom archive name
pygbag --archive --build main.py