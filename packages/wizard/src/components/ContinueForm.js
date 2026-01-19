import React from "react";
import { useComponents } from "@wq/react";
import { useWizardInfo, useSubmitForm } from "../hooks";
import PropTypes from "prop-types";

export default function ContinueForm({ children, submitLabel = "Continue" }) {
    const { label } = useWizardInfo(),
        submitForm = useSubmitForm(),
        {
            ScrollView,
            Form,
            Typography,
            SubmitButton,
            HorizontalView,
            View,
            FormContainer,
        } = useComponents();
    return (
        <ScrollView>
            <FormContainer>
                <Form action="auto" onSubmit={submitForm}>
                    <Typography variant="h5">{label}</Typography>
                    {children}
                    <HorizontalView>
                        <View />
                        <SubmitButton icon="continue">
                            {submitLabel}
                        </SubmitButton>
                    </HorizontalView>
                </Form>
            </FormContainer>
        </ScrollView>
    );
}

ContinueForm.propTypes = {
    children: PropTypes.node,
    submitLabel: PropTypes.string,
};
