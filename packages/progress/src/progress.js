export class Progress {
    constructor(config) {
        this.config = {
            interval: 0.5,
            ...config,
        };
        if (!this.config.url) {
            throw new Error('No URL specified!');
        }
    }
    start() {
        this._throttle = 0;
        this._throttleCount = 0;
        this._lastProgress = null;
        this._timer = setInterval(
            () => this.update(),
            this.config.interval * 1000
        );
    }
    stop() {
        if (this._timer) {
            clearInterval(this._timer);
        }
        delete this._throttle;
        delete this._throttleCount;
        delete this._lastProgress;
        delete this._timer;
    }
    async update() {
        if (this._pending) {
            return;
        }
        if (this._throttleCount < this._throttle) {
            this._throttleCount += 1;
            return;
        } else {
            this._throttleCount = 0;
        }
        let data;
        try {
            this._pending = true;
            const controller = new AbortController(),
                timeout = setTimeout(() => controller.abort(), 10000),
                response = await fetch(this.config.url, {
                    signal: controller.signal,
                });

            clearTimeout(timeout);
            data = await response.json();
            this._pending = false;
        } catch (e) {
            this._pending = false;
            if (e.name === 'AbortError') {
                this.onError(new Error('Timeout while requesting status'));
            } else {
                this.onError(e);
            }
            return;
        }

        let done = false;
        if (!data.total) {
            this.onIndeterminate(data);
            this._throttle++;
        } else {
            // Set to progress level
            if (this._lastProgress && data.current < this._lastProgress) {
                // Assume out-of order response; no update
                /* jshint noempty: false */
            } else if (this._lastProgress == data.current) {
                // No change since last check; check less often
                this._throttle++;
            } else {
                // Change since last check; check more often
                this._lastProgress = data.current;
                if (this._throttle > 0) {
                    this._throttle--;
                }
            }

            if (data.current == data.total) {
                this.onComplete(data);
                done = true;
            }
        }

        if (data.status == 'SUCCESS' && !done) {
            this.onComplete(data);
        } else if (data.status == 'FAILURE') {
            this.onFail(data);
        } else if (!done) {
            this.onProgress(data);
        }

        if (data.location) {
            this.onNavigate(data);
        }
    }

    onIndeterminate(data) {
        if (this.config.onIndeterminate) {
            this.config.onIndeterminate(data);
        }
    }

    onProgress(data) {
        if (this.config.onProgress) {
            this.config.onProgress(data);
        }
    }

    onError(error) {
        if (this.config.onError) {
            this.config.onError(error);
        }
    }

    onComplete(data) {
        if (this.config.onComplete) {
            this.config.onComplete(data);
        }
        this.stop();
    }

    onFail(data) {
        this.stop();
        if (this.config.onFail) {
            this.config.onFail(data);
        }
    }

    onNavigate(data) {
        this.stop();
        if (this.config.onNavigate) {
            this.config.onNavigate(data);
        }
    }
}
