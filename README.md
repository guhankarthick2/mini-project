# mini-project
Python Mini projects for learning

## Video Highlights

A static highlights gallery hosted from the repo root on GitHub Pages.

**Live URL:** https://guhankarthick2.github.io/mini-project/

### GitHub Pages setup

1. Go to **Settings → Pages**
2. Source: branch `main`, folder **`/ (root)`**
3. Save

### Public view

Anyone visiting the site sees all highlights from `highlights.json` and videos in `videos/`.

### Admin (add highlight links)

Only you can add or remove highlights:

1. Click **Admin** at the bottom of the page (or visit `?admin`)
2. Log in with password: `guhan-highlights-admin`
3. Add YouTube/Vimeo links or repo video paths (e.g. `videos/clip.mp4`)
4. Click **Download JSON**, replace `highlights.json` in the repo, and push

Change the admin password by editing `ADMIN_PASSWORD_HASH` in `index.html` (SHA-256 hash of your new password).
