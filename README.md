# mini-project
Python Mini projects for learning

## Video Highlights

A simple static page for collecting highlight videos with descriptions.

- Open locally: open `highlights/index.html` in your browser
- On GitHub Pages: enable Pages for this repo and set the source folder to `/highlights`

Live URL format: `https://guhankarthick2.github.io/mini-project/`

### Adding highlights

**Option 1 — Video link**
1. Choose the **Video link** tab
2. Paste a YouTube, Vimeo, or direct video URL
3. Add a description and click **Add Highlight**

**Option 2 — Upload from your computer**
1. Choose the **Upload from computer** tab
2. Pick or drag in a video file (MP4, WebM, MOV, etc.)
3. Add a description and click **Add Highlight**

Uploaded videos are stored in your browser (IndexedDB) so they persist when you revisit the page.

To publish uploaded videos on GitHub:
1. Click **Download video** on each uploaded highlight
2. Put the files in `highlights/videos/`
3. Click **Download JSON** and replace `highlights/highlights.json`
4. Commit and push both the JSON and video files
