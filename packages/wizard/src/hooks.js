import { useState, useEffect, useMemo, createContext, useContext } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";

export const WizardContext = createContext({
    apiUrl: "",
    returnPath: "",
    step: "",
    setStep: () => null,
    taskId: null,
    setTaskId: () => null,
});

export function useWizardContext() {
    return useContext(WizardContext);
}

function emptyInfo(label) {
    return {
        label,
        serializer_label: label,
        record_count: null,
        last_update: null,
    };
}

export function useWizardInfo() {
    const { apiUrl } = useWizardContext(),
        { data, isPending, isError, error } = useQuery({
            queryKey: [apiUrl],
            async queryFn() {
                const response = await fetch(apiUrl, {
                    headers: {
                        Accept: "application/json",
                    },
                });
                if (!response.ok) {
                    throw new Error("Error loading data.");
                }
                return response.json();
            },
        });
    if (isPending) {
        return emptyInfo("Loading...");
    } else if (isError) {
        return emptyInfo(`Error: ${error.message}`);
    } else {
        return {
            ...emptyInfo("Unknown"),
            ...data,
        };
    }
}

export function useWizardQuery(path, resultKey = "result") {
    const { apiUrl } = useWizardContext(),
        { data, isPending, isError, error } = useQuery({
            queryKey: [apiUrl, path],
            async queryFn() {
                const response = await fetch(`${apiUrl}/${path}`, {
                    headers: {
                        Accept: "application/json",
                    },
                });
                if (!response.ok) {
                    throw new Error("Error loading results.");
                }
                const data = await response.json();
                return data[resultKey];
            },
        });
    return { data, isPending, isError, error };
}

function getCsrfToken() {
    return document.cookie
        .split("; ")
        .find((row) => row.startsWith("csrftoken="))
        ?.split("=")[1];
}

export function useSubmitForm() {
    const { apiUrl, setStep, setTaskId } = useWizardContext(),
        { mutateAsync } = useMutation({
            async mutationFn({ action, data }) {
                const response = await fetch(`${apiUrl}/${action}`, {
                    method: "POST",
                    body: JSON.stringify(data),
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                });
                if (!response.ok) {
                    const error = new Error("Error submitting form.");
                    try {
                        error.detail = await response.json();
                    } catch {
                        error.detail = `${response.status} ${response.statusText}`;
                    }
                    throw error;
                }
                return response.json();
            },
            onSuccess(result, _variables, _context, fnContext) {
                const { client: queryClient } = fnContext;
                queryClient?.invalidateQueries([apiUrl]);
                queryClient?.setQueryData([apiUrl], (lastResult) => ({
                    ...lastResult,
                    ...result,
                }));
                if (result?.current_mode) {
                    setStep(result.current_mode);
                }
                if (result?.task_id) {
                    setTaskId(result.task_id);
                }
            },
        });
    return mutateAsync;
}

export function useProgress() {
    const [progress, setProgress] = useState(null),
        [value, setValue] = useState(null),
        [status, setStatus] = useState(null),
        [error, setError] = useState(false),
        [data, setData] = useState(null),
        { apiUrl, taskId, setStep } = useWizardContext();

    useEffect(() => {
        const updateStatus = (data) => {
            setData(data);
            if (data.error || data.message) {
                setStatus(data.error || data.message);
            }
        };
        if (!apiUrl || !taskId) {
            setStatus("Missing task id");
            return;
        }
        const url = `${apiUrl}/status.json?task=${taskId}`;
        const progress = new Progress({
            url,
            onIndeterminate: updateStatus,
            onProgress(data) {
                setValue((data.current / data.total) * 100);
                updateStatus(data);
            },
            onComplete(data) {
                setValue(100);
                setError(false);
                updateStatus(data);
            },
            onFail(data) {
                setValue(0);
                setError(true);
                updateStatus(data);
            },
            onError(err) {
                setError(true);
                setStatus("" + err);
            },
            onNavigate(data) {
                const action = data.location.split("/").pop();
                setStep(action);
            },
        });
        progress.start();
        setProgress(progress);
        return () => progress.stop();
    }, [apiUrl, taskId]);

    return useMemo(() => {
        return { progress, value, status, error, data };
    }, [progress, value, status, error, data]);
}

class Progress {
    constructor(config) {
        this.config = {
            interval: 0.5,
            ...config,
        };
        if (!this.config.url) {
            throw new Error("No URL specified!");
        }
    }
    start() {
        this._throttle = 0;
        this._throttleCount = 0;
        this._lastProgress = null;
        this._timer = setInterval(
            () => this.update(),
            this.config.interval * 1000,
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
            if (e.name === "AbortError") {
                this.onError(new Error("Timeout while requesting status"));
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

        if (data.status == "SUCCESS" && !done) {
            this.onComplete(data);
        } else if (data.status == "FAILURE") {
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
