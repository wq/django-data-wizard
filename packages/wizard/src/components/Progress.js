import React from 'react';
import LinearProgress from '@material-ui/core/LinearProgress';
import { useProgress } from '../hooks';

export default function Progress() {
    const progress = useProgress();
    return <LinearProgress {...progress} />;
}
