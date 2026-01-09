# Web Deployment Setup Guide

This guide will help you deploy Dashy Dude to GitHub Pages with Firebase for global leaderboards.

## How Storage Works

### Dual Storage System

**Local Storage (localStorage):**
- Stores your personal data: settings, full run history, all-time stats
- Persists in your browser between sessions
- Works offline
- Private to your browser/device

**Firebase (Optional - Global Leaderboard):**
- Stores top scores from ALL players worldwide
- Public leaderboard visible to everyone
- Requires internet connection
- Only stores high scores, not personal settings

**Without Firebase:** Game works perfectly with local scores only
**With Firebase:** Players compete on a global leaderboard

## Prerequisites

- GitHub account
- Firebase account (free tier is sufficient) - **Optional but recommended**
- Repository pushed to GitHub

## Step 1: Configure GitHub Pages

1. Go to your repository on GitHub
2. Navigate to **Settings** > **Pages**
3. Under **Source**, select **GitHub Actions**
4. The workflow is already configured in `.github/workflows/deploy.yml`

## Step 2: Set Up Firebase for Global Leaderboard

**Note:** Skip this section if you only want local scores. The game works fine without Firebase.

### Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **Add Project**
3. Name it (e.g., "dashy-dude-game")
4. Disable Google Analytics (optional)
5. Click **Create Project**

### Enable Realtime Database

1. In your Firebase project, go to **Build** > **Realtime Database**
2. Click **Create Database**
3. Choose a location closest to your users
4. Start in **test mode** (for development)
   - **Note**: For production, set up proper security rules

### Get Firebase Configuration

1. In Firebase Console, click the gear icon (⚙️) > **Project Settings**
2. Scroll down to **Your apps** section
3. Click the **Web** icon (`</>`) to add a web app
4. Register your app with a nickname
5. Copy the Firebase configuration object

### Update index.html

1. Open `index.html` in your repository
2. Find the `firebaseConfig` object (around line 84)
3. Replace the placeholder values with your Firebase config:

```javascript
const firebaseConfig = {
    apiKey: "YOUR_ACTUAL_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    databaseURL: "https://your-project.firebaseio.com",
    projectId: "your-project-id",
    storageBucket: "your-project-id.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef123456"
};
```

### Configure Database Rules (Important for Production)

1. In Firebase Console, go to **Realtime Database** > **Rules**
2. For testing, you can use:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

3. For production with spam protection:

```json
{
  "rules": {
    "high_scores": {
      ".read": true,
      ".write": true,
      ".indexOn": ["score"],
      "$score_id": {
        ".validate": "newData.hasChildren(['score', 'name', 'date'])",
        "score": {
          ".validate": "newData.isNumber() && newData.val() >= 0"
        },
        "name": {
          ".validate": "newData.isString() && newData.val().length <= 20"
        }
      }
    }
  }
}
```

**What gets stored in Firebase:**
- High scores only (score, player name, date, basic stats)
- Top 100 scores are kept, older ones auto-deleted
- Visible to all players globally

**What stays local (localStorage):**
- Your full run history (last 50 runs)
- All-time personal statistics
- Game settings and customization
- Everything else not explicitly pushed to Firebase

## Step 3: Deploy

### Automatic Deployment (Recommended)

The game will automatically deploy whenever you push to the `main` branch.

1. Commit your changes:
```bash
git add .
git commit -m "Configure for web deployment"
git push origin main
```

2. Go to your repository on GitHub
3. Click the **Actions** tab
4. Watch the deployment workflow run
5. Once complete, your game will be live at:
   `https://YOUR_USERNAME.github.io/dashy-dude-game/`

### Manual Deployment (Alternative)

You can also trigger deployment manually:

1. Go to **Actions** tab on GitHub
2. Select **Deploy to GitHub Pages** workflow
3. Click **Run workflow**
4. Select `main` branch
5. Click **Run workflow**

## Step 4: Test Your Game

1. Visit your GitHub Pages URL
2. Wait for the game to load (first load may take 30-60 seconds)
3. Test the controls:
   - **SPACE**: Jump / Double Jump / Helicopter Glide
   - **ESC**: Pause
4. Play a game and check if scores are saved
5. Open browser console (F12) to check for any errors

## Troubleshooting

### Game doesn't load
- Check the Actions tab for build errors
- Ensure pygbag built successfully
- Check browser console (F12) for JavaScript errors

### Scores not saving to Firebase
- Verify Firebase configuration in `index.html` (lines 135-143)
- Check Firebase Console > Realtime Database for data under `high_scores`
- Ensure database rules allow read/write
- Check browser console for Firebase errors
- Look for "Score X uploaded to global leaderboard" message in console

### How to view global leaderboard
- Open browser console (F12) while playing
- When you achieve a high score, look for upload confirmation
- In Firebase Console > Realtime Database, view all scores under `high_scores`
- To test: Type `window.dashyDude.getTopScores(10)` in console to see top 10 scores
- Note: In-game UI currently shows local scores only; Firebase stores global leaderboard

### Checking if Firebase is working
Open browser console (F12) and run:
```javascript
window.dashyDude.isFirebaseAvailable()  // Should return true if configured
window.dashyDude.getTopScores(10)      // Should return array of top scores
```

### Game is slow
- First load is always slower due to WebAssembly compilation
- Subsequent loads should be faster (cached)
- Consider optimizing assets if needed

## Local Testing

To test the web build locally before deploying:

```bash
# Install pygbag
pip install pygbag

# Build and serve locally
python -m pygbag --build .

# Visit http://localhost:8000 in your browser
```

## Updating the Game

Any time you make changes to the game:

1. Test locally (optional but recommended)
2. Commit and push to GitHub:
```bash
git add .
git commit -m "Update game features"
git push origin main
```

3. GitHub Actions will automatically rebuild and redeploy

## Notes

- **Local Storage (Always Active)**:
  - All personal data (settings, run history, stats) saved in browser localStorage
  - Works offline
  - Private to your device

- **Firebase (Optional - Global Leaderboard)**:
  - Only high scores shared publicly
  - All players can see top scores worldwide
  - Requires internet connection
  - Automatically pushed when you achieve a high score

- **Performance**: Web version may run slightly slower than native Python version due to WebAssembly overhead

- **Browser Compatibility**: Works best on Chrome, Firefox, and Safari (latest versions)

- **Data Persistence**:
  - localStorage data stays until you clear browser data
  - Firebase data is permanent (until manually deleted)

## Resources

- [Pygbag Documentation](https://pygame-web.github.io/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)

---

**Need help?** Check the repository issues or create a new one!
