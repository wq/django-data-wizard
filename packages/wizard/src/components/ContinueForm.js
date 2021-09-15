import React from 'react';
import { useComponents } from '@wq/react';
import { useRunInfo } from '../hooks';
import PropTypes from 'prop-types';

export default function ContinueForm({ children, submitLabel = 'Continue' }) {
    const { id, label } = useRunInfo(),
        { ScrollView, Form, Typography, SubmitButton, HorizontalView, View } =
            useComponents();
    return (
        <ScrollView>
            <Form
                action={`datawizard/${id}/auto`}
                method="POST"
                backgroundSync={false}
            >
                <Typography variant="h5">{label}</Typography>
                {children}
                <HorizontalView>
                    <View />
                    <SubmitButton icon="continue">{submitLabel}</SubmitButton>
                </HorizontalView>
            </Form>
        </ScrollView>
    );
}

ContinueForm.propTypes = {
    children: PropTypes.node,
    submitLabel: PropTypes.string,
};
