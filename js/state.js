// Flea Circus State Management
// Syncs between operator console and audience display
// Supports both localStorage (local) and HTTP server (network)

class ShowState {
    constructor() {
        this.stateKey = 'fleaCircusState';
        this.listeners = [];
        this.lastUpdate = 0;
        this.useServer = false;
        this.serverUrl = this.getServerUrl();
        this.currentState = this.defaultState();

        this.detectServer();
    }

    getServerUrl() {
        // Try to detect if we should use server mode
        const params = new URLSearchParams(window.location.search);
        if (params.get('server') === 'true') return window.location.origin;

        // Check if running under a server
        if (window.location.protocol !== 'file:') {
            return window.location.origin;
        }
        return null;
    }

    detectServer() {
        if (!this.serverUrl) {
            this.useServer = false;
            this.poll();
            return;
        }

        fetch(`${this.serverUrl}/api/state`)
            .then(() => {
                this.useServer = true;
                console.log('🎪 Connected to server mode');
                this.pollServer();
            })
            .catch(() => {
                console.log('📱 Using local mode (no server detected)');
                this.useServer = false;
                this.poll();
            });
    }

    getState() {
        return this.currentState;
    }

    setState(updates) {
        const newState = {
            ...this.currentState,
            ...updates,
            lastUpdate: Date.now()
        };
        this.currentState = newState;

        if (this.useServer) {
            this.sendToServer(newState);
        } else {
            try {
                localStorage.setItem(this.stateKey, JSON.stringify(newState));
            } catch (e) {
                console.warn('localStorage not available:', e);
            }
        }

        this.notify(newState);
    }

    sendToServer(state) {
        fetch(`${this.serverUrl}/api/state`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(state)
        }).catch(e => console.warn('Server sync error:', e));
    }

    defaultState() {
        return {
            displayMode: 'intro',
            currentCue: null,
            videoUrl: null,
            videoPlaying: false,
            audioUrl: null,
            audioPlaying: false,
            audioVolume: 1,
            overlayText: '',
            overlayType: null,
            timerDuration: 0,
            timerActive: false,
            messageText: '',
            lastUpdate: 0,
            connectionStatus: 'connected'
        };
    }

    subscribe(callback) {
        this.listeners.push(callback);
        callback(this.currentState);
        return () => {
            this.listeners = this.listeners.filter(l => l !== callback);
        };
    }

    notify(state) {
        this.listeners.forEach(listener => listener(state));
    }

    poll() {
        setInterval(() => {
            try {
                const stored = localStorage.getItem(this.stateKey);
                const state = stored ? JSON.parse(stored) : this.currentState;
                if (state.lastUpdate > this.lastUpdate) {
                    this.lastUpdate = state.lastUpdate;
                    this.currentState = state;
                    this.notify(state);
                }
            } catch (e) {
                // localStorage might be unavailable
            }
        }, 100);
    }

    pollServer() {
        setInterval(() => {
            if (!this.useServer) return;

            fetch(`${this.serverUrl}/api/state`)
                .then(res => res.json())
                .then(state => {
                    if (state.lastUpdate > this.lastUpdate) {
                        this.lastUpdate = state.lastUpdate;
                        this.currentState = state;
                        this.notify(state);
                    }
                })
                .catch(e => {
                    if (this.useServer) {
                        console.warn('Server connection lost');
                        this.useServer = false;
                        this.poll();
                    }
                });
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
