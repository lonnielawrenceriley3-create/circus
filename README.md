# 🎪 Professor Percival's Extraordinary Flea Circus
## Show Control System - MVP

A browser-based theatrical show control system. No installation, no servers, no subscriptions. Copy the folder, open in browser, control a live show.

---

## Quick Start

### Setup
1. Open `index.html` in your browser
2. Open **Audience Display** in fullscreen on your main screen (projector/TV)
3. Open **Operator Console** on a control device (tablet/laptop)
4. Both will sync automatically via localStorage

### Operator Console
Control everything from the console:
- **LIVE** - Show the arena
- **Interview** - Interview mode with lower third
- **Video** - Play any video
- **Audio** - Play background music
- **Replay** - Show a replay with badge
- **Applause** - Display "APPLAUSE!" message
- **Cannon** - Display cannon fire effect
- **Finale** - End of show with confetti
- **Blackout** - Black screen
- **Stop All** - Emergency stop
- **Media Library** - Click any media to play
- **Master Volume** - Control audio level
- **Timer** - Countdown timer

### Audience Display
The audience sees:
- Professional broadcast-quality display
- No browser UI, menus, or technical elements
- Full-screen immersive experience
- Smooth transitions between scenes
- Overlays and graphics
- Timer display (when active)

---

## Architecture

```
circus/
├── index.html              # Landing page (links to display/control)
├── display.html            # Audience screen (fullscreen)
├── control.html            # Operator console (tablet/touch-friendly)
├── js/
│   └── state.js            # Shared state management (localStorage sync)
├── media/
│   ├── video/              # Place video files here (.mp4)
│   │   ├── arena.mp4
│   │   ├── interview.mp4
│   │   └── replay.mp4
│   ├── audio/              # Place audio files here (.mp3, .wav)
│   │   ├── music.mp3
│   │   ├── applause.mp3
│   │   └── drumroll.mp3
│   └── images/             # Place images here (.png, .jpg)
│       └── title.png
├── config/
│   └── config.json         # Show configuration
└── README.md               # This file
```

---

## Media Management

### Adding Media
Simply copy files into the appropriate directories:
- **Videos** → `/media/video/` (`.mp4`, `.webm`)
- **Audio** → `/media/audio/` (`.mp3`, `.wav`, `.ogg`)
- **Images** → `/media/images/` (`.png`, `.jpg`, `.gif`)

Refresh the operator console to see new media in the library.

### Media Examples
Test media files are referenced in the code. To use your own:

```
/media/video/intro.mp4          → "Intro" button
/media/video/interview.mp4      → "Interview" button
/media/audio/circus_music.mp3   → Background music
```

---

## System Architecture

### State Management
The app uses **localStorage** for real-time synchronization:
- Operator console → Updates state in localStorage
- Audience display → Monitors localStorage for changes
- No server required
- Works offline and on local networks

### Display Modes
```
- intro        → Intro screen with logo
- live         → Arena view with host commentary
- video        → Play video files
- audio        → Audio playback + visualization
- blackout     → Black screen (technical pause)
- finale       → End credits with confetti
```

### Cues
Each button/action is a "Cue" that changes the display:

```javascript
showState.cueLive()           // Go to LIVE
showState.cueVideo(url)       // Play video
showState.cueMessage(text)    // Show message
showState.cueBlackout()       // Black screen
showState.startTimer(seconds) // Start countdown
```

---

## Configuration

Edit `config/config.json` to customize:

```json
{
  "show": {
    "title": "Professor Percival's Extraordinary Flea Circus",
    "theme": "broadcast",
    "duration": 2700
  },
  "display": {
    "resolution": "16:9",
    "fullscreen": true
  },
  "cues": [
    {
      "name": "LIVE",
      "type": "live",
      "description": "Show the arena"
    },
    {
      "name": "Interview",
      "type": "interview",
      "media": "video/interview.mp4"
    }
  ]
}
```

---

## Networking

### Local Network
Both devices must be on the same network:
1. Operator console connects to `localhost:8000` (or your IP)
2. Audience display connects to `localhost:8000/display.html`
3. State syncs via localStorage (works without server)

### Offline Mode
Works completely offline:
- Copy the entire folder to any device
- Open files locally
- No internet needed

### Future: WebSocket Mode
For remote operation:
- Replace localStorage with WebSocket connection
- Operator and audience can be anywhere
- Add authentication and multi-user support

---

## Browser Compatibility

Tested on:
- ✅ Chrome/Chromium
- ✅ Safari (macOS/iOS)
- ✅ Edge
- ✅ Firefox
- ✅ iPad Safari
- ✅ Android Chrome

---

## Features (MVP)

✅ **Operator Console**
- Touch-friendly button grid
- Media library browser
- Master volume control
- Timer control
- Dark mode (optimized for stage lighting)

✅ **Audience Display**
- Full-screen broadcast view
- No browser UI visible
- Smooth transitions
- Overlay system (lower thirds, messages)
- Animated finale with confetti
- Professional appearance

✅ **State Sync**
- Real-time operator → audience sync
- No server required
- Offline capable
- localStorage-based

✅ **Media Support**
- Video playback
- Audio playback
- Image display
- Automatic media library loading

✅ **Cue System**
- Pre-built cues (Live, Interview, Video, Replay, etc.)
- Instant triggering
- No timelines or sequences

---

## Future Enhancements

### Phase 2
- [ ] Cue editor (drag-and-drop sequences)
- [ ] More overlay types
- [ ] Audio fade in/out
- [ ] Video crossfade
- [ ] Custom themes
- [ ] QR code pairing

### Phase 3
- [ ] WebSocket for remote operation
- [ ] Raspberry Pi GPIO control
- [ ] Lighting integration (DMX)
- [ ] Stream Deck support
- [ ] OBS integration
- [ ] NDI output

### Phase 4
- [ ] Multi-user support
- [ ] User authentication
- [ ] Cloud sync (optional)
- [ ] AI voice announcements
- [ ] Live subtitle support
- [ ] Audience voting

---

## Troubleshooting

### Display Not Syncing
- Check both devices are on same network
- Try refreshing both browsers
- Check browser console for errors (F12)

### Media Not Playing
- Verify files exist in `/media/` directories
- Check file format is supported (MP4, MP3, PNG, JPG)
- Try using a smaller file size
- Check browser console for codec errors

### Fullscreen Issues
- Press F11 or Cmd+Control+F for fullscreen
- On iPad: Use Safari's reader mode or fullscreen gesture
- Some projectors require fullscreen for best results

### Audio Not Working
- Check master volume slider
- Verify audio file exists
- Check browser audio permissions
- Try different audio format (MP3 often most compatible)

---

## Documentation

- **Operator Manual** - How to use the console (coming soon)
- **Technical Guide** - How the system works (coming soon)
- **Venue Setup** - How to set up for different venues (coming soon)
- **Media Guide** - Best practices for media files (coming soon)

---

## License

This software is provided as-is for theatrical productions.

---

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review browser console errors (F12)
3. Verify media files exist and are correct format
4. Try refreshing both browsers
5. Restart the show from the intro screen

---

## Design Philosophy

This system is designed to feel like:
- 📺 **Television Control Room** - Not PowerPoint
- 🏟️ **Sports Broadcast** - Not a slideshow
- 🚀 **Mission Control** - Everything on demand

Not like:
- ❌ Presentation software
- ❌ Video players
- ❌ Timelines or sequences

Every action should feel immediate and responsive, like calling a live sporting event.

---

**Built for Professor Percival's Extraordinary Flea Circus** 🎪
