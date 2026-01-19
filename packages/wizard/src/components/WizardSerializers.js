import React, { useMemo } from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import { useSubmitForm, useWizardInfo, useWizardQuery } from "../hooks";
import ContinueForm from "./ContinueForm";

const WizardSerializersDefaults = {
        components: { ContinueForm },
    },
    WizardSerializersFallback = {
        components: {
            ...createFallbackComponents(
                [
                    "ScrollView",
                    "Typography",
                    "SubmitButton",
                    "HorizontalView",
                    "View",
                    "FormContainer",
                ],
                "@wq/material",
            ),
            ...createFallbackComponents(
                ["AutoForm"],
                "@wq/form",
                "FormProvider",
            ),
        },
    };

function WizardSerializers() {
    const { label, serializer, serializer_label } = useWizardInfo(),
        {
            data: result,
            isPending,
            isError,
            error,
        } = useWizardQuery("serializers"),
        { serializer_choices = [] } = result || {},
        form = useMemo(
            () => [
                {
                    type: "select one",
                    name: "serializer",
                    label: "Select Format",
                    choices: serializer_choices,
                    control: { appearance: "radio" },
                },
            ],
            [serializer_choices],
        ),
        submitForm = useSubmitForm(),
        { ScrollView, Typography, AutoForm, ContinueForm, FormContainer } =
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
    } else if (isPending) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6">Loading formats...</Typography>
                </FormContainer>
            </ScrollView>
        );
    } else if (isError) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h6">{label}</Typography>
                    <Typography color="error">
                        Error: {error.message}
                    </Typography>
                </FormContainer>
            </ScrollView>
        );
    } else if (!(serializer_choices.length > 0)) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h6" color="error">
                        No serializers registered.
                    </Typography>
                    <Typography>
                        See{" "}
                        <a href="https://django-data-wizard.wq.io/overview/setup#target-model-registration">
                            https://django-data-wizard.wq.io/overview/setup#target-model-registration
                        </a>{" "}
                        for more information.
                    </Typography>
                </FormContainer>
            </ScrollView>
        );
    } else {
        return (
            <ScrollView>
                <AutoForm
                    action="updateserializer"
                    onSubmit={submitForm}
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

export default withWQ(WizardSerializers, {
    defaults: WizardSerializersDefaults,
    fallback: WizardSerializersFallback,
});
