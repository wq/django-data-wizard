import { useState, useEffect, useMemo } from 'react';
import { Progress } from '@wq/progress';
import { useRenderContext, useModel, useNav, useConfig } from '@wq/react';

export function useRunInfo() {
    const context = useRenderContext(),
        instance = useModel('run', context.id || -1);
    return {
        ...context,
        ...instance,
    };
}

export function useProgress(url) {
    const [progress, setProgress] = useState(null),
        [value, setValue] = useState(null),
        [status, setStatus] = useState(null),
        [error, setError] = useState(false),
        [data, setData] = useState(null),
        nav = useNav(),
        config = useConfig();

    useEffect(() => {
        const updateStatus = (data) => {
            setData(data);
            if (data.error || data.message) {
                setStatus(data.error || data.message);
            }
        };
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
                setStatus('' + err);
            },
            onNavigate(data) {
                const path = data.location.replace(
                    config.router.base_url + '/',
                    ''
                );
                nav(path);
            },
        });
        progress.start();
        setProgress(progress);
        return () => progress.stop();
    }, [url]);

    return useMemo(() => {
        return { progress, value, status, error, data };
    }, [progress, value, status, error, data]);
}
