import React from 'react';
import { LinearProgress } from '@mui/material';
import { useComponents } from '@wq/react';
import { useProgress } from '../hooks';
import PropTypes from 'prop-types';

export default function Progress({ url }) {
    const { value, error, status } = useProgress(url),
        { Typography, CloseWizard } = useComponents();
    return (
        <>
            <LinearProgress
                style={{ marginTop: 16, marginBottom: 16 }}
                variant={value === null ? 'indeterminate' : 'determinate'}
                value={value}
            />
            {status && (
                <Typography color={error ? 'error' : 'textSecondary'}>
                    {status}
                </Typography>
            )}
            {value === 0 && error && <CloseWizard />}
        </>
    );
}

Progress.propTypes = {
    url: PropTypes.string,
};
