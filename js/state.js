// Flea Circus State Management
// Syncs between operator console and audience display via localStorage

class ShowState {
    constructor() {
        this.stateKey = 'fleaCircusState';
        this.listeners = [];
        this.lastUpdate = 0;
        this.poll();
    }

    getState() {
        try {
            const stored = localStorage.getItem(this.stateKey);
            return stored ? JSON.parse(stored) : this.defaultState();
        } catch (e) {
            return this.defaultState();
        }
    }

    setState(updates) {
        const current = this.getState();
        const newState = {
            ...current,
            ...updates,
            lastUpdate: Date.now()
        };
        localStorage.setItem(this.stateKey, JSON.stringify(newState));
        this.notify(newState);
    }

    defaultState() {
        return {
            displayMode: 'intro', // intro, live, video, audio, overlay, blackout
            currentCue: null,
            videoUrl: null,
            videoPlaying: false,
            audioUrl: null,
            audioPlaying: false,
            audioVolume: 1,
            overlayText: '',
            overlayType: null, // lower-third, breaking-news, sponsor, technical
            timerDuration: 0,
            timerActive: false,
            messageText: '',
            lastUpdate: 0,
            connectionStatus: 'connected'
        };
    }

    subscribe(callback) {
        this.listeners.push(callback);
        // Immediately call with current state
        callback(this.getState());
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    notify(state) {
        this.listeners.forEach(listener => listener(state));
    }

    poll() {
        setInterval(() => {
            const state = this.getState();
            if (state.lastUpdate > this.lastUpdate) {
                this.lastUpdate = state.lastUpdate;
                this.notify(state);
            }
        }, 100);
    }

    // Cue actions
    cueIntro() {
        this.setState({
            displayMode: 'intro',
            currentCue: 'Intro',
            videoPlaying: false,
            audioPlaying: false,
            overlayType: null
        });
    }

    cueLive() {
        this.setState({
            displayMode: 'live',
            currentCue: 'LIVE',
            videoUrl: null,
            videoPlaying: false,
            overlayType: null
        });
    }

    cueVideo(videoUrl, title = 'Video') {
        this.setState({
            displayMode: 'video',
            currentCue: title,
            videoUrl: videoUrl,
            videoPlaying: true,
            overlayType: null
        });
    }

    cueAudio(audioUrl, title = 'Audio') {
        this.setState({
            displayMode: 'audio',
            currentCue: title,
            audioUrl: audioUrl,
            audioPlaying: true
        });
    }

    cueInterview(videoUrl, title = 'Interview') {
        this.cueVideo(videoUrl, title);
        this.setState({
            overlayType: 'lower-third',
            overlayText: title
        });
    }

    cueReplay(videoUrl) {
        this.setState({
            displayMode: 'video',
            currentCue: 'REPLAY',
            videoUrl: videoUrl,
            videoPlaying: true,
            overlayType: 'replay'
        });
    }

    cueBlackout() {
        this.setState({
            displayMode: 'blackout',
            currentCue: 'BLACKOUT',
            videoPlaying: false,
            audioPlaying: false,
            overlayType: null
        });
    }

    cueMessage(text, duration = 5000) {
        this.setState({
            messageText: text,
            overlayType: 'message'
        });
        setTimeout(() => {
            this.setState({
                messageText: '',
                overlayType: null
            });
        }, duration);
    }

    startTimer(seconds) {
        this.setState({
            timerDuration: seconds,
            timerActive: true
        });
    }

    stopTimer() {
        this.setState({
            timerActive: false
        });
    }

    setAudioVolume(volume) {
        this.setState({
            audioVolume: Math.max(0, Math.min(1, volume))
        });
    }

    stopAll() {
        this.setState({
            videoPlaying: false,
            audioPlaying: false,
            timerActive: false,
            overlayType: null
        });
    }
}

// Global instance
window.showState = new ShowState();
