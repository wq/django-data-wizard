import React from 'react';
import { ScrollView } from '@wq/material';
import PropTypes from 'prop-types';

export default function Center({ children }) {
    return (
        <ScrollView>
            <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
                <div
                    style={{
                        width: '100%',
                        maxWidth: '70em',
                        padding: '1em',
                        boxSizing: 'border-box',
                    }}
                >
                    {children}
                </div>
            </div>
        </ScrollView>
    );
}

Center.propTypes = {
    children: PropTypes.node,
};
