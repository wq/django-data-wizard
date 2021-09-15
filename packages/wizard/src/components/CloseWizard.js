import React from 'react';
import { useComponents, useReverse } from '@wq/react';

export default function CloseWizard() {
    const { CancelButton, HorizontalView, View } = useComponents(),
        reverse = useReverse();

    return (
        <HorizontalView>
            <CancelButton
                to={reverse('run_list')}
                variant="outlined"
                color="secondary"
            >
                Back
            </CancelButton>
            <View />
        </HorizontalView>
    );
}
