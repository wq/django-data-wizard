import React from 'react';
import { useComponents } from '@wq/react';
import { useRunInfo } from '../hooks';

export default function RunAuto() {
    const { id, label, task_id, svc } = useRunInfo(),
        { Typography, Progress, Center } = useComponents(),
        url = `${svc}/datawizard/${id}/status.json?task=${task_id}`;
    return (
        <Center>
            <Typography variant="h5">{label}</Typography>
            <Progress url={url} />
        </Center>
    );
}
