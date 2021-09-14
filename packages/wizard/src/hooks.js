import { useState, useEffect } from 'react';
import { Progress } from '@wq/progress';

export function useProgress() {
    const [progress, setProgress] = useState(null);

    useEffect(() => {
        const progress = new Progress({ url: '/FIXME' });
        progress.start();
        setProgress(progress);
        return () => progress.stop();
    }, []);

    return progress;
}
