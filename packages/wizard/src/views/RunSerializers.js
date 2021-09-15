import React, { useMemo } from 'react';
import { useComponents } from '@wq/react';
import { useRunInfo } from '../hooks';

export default function RunSerializers() {
    const { id, label, serializer, serializer_label, serializer_choices } =
            useRunInfo(),
        form = useMemo(
            () => [
                {
                    type: 'select one',
                    name: 'serializer',
                    label: 'Select Format',
                    choices: serializer_choices,
                    control: { appearance: 'radio' },
                },
            ],
            [serializer_choices]
        ),
        { ScrollView, Typography, AutoForm, ContinueForm, Center } =
            useComponents();
    if (serializer) {
        return (
            <ScrollView>
                <ContinueForm>
                    <Typography variant="h6">Data Format</Typography>
                    <Typography>
                        This dataset will be parsed as &ldquo;{serializer_label}
                        &rdquo;.
                    </Typography>
                </ContinueForm>
            </ScrollView>
        );
    } else if (!serializer_choices) {
        return (
            <Center>
                <Typography variant="h6" color="error">
                    No serializers registered.
                </Typography>
                <Typography>
                    See{' '}
                    <a href="https://github.com/wq/django-data-wizard#target-model-registration">
                        https://github.com/wq/django-data-wizard#target-model-registration
                    </a>{' '}
                    for more information.
                </Typography>
            </Center>
        );
    } else {
        return (
            <ScrollView>
                <AutoForm
                    action={`datawizard/${id}/updateserializer`}
                    method="POST"
                    backgroundSync={false}
                    form={form}
                >
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6">
                        Select a format to continue
                    </Typography>
                </AutoForm>
            </ScrollView>
        );
    }
}
