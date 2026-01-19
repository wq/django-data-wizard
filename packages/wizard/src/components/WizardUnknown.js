import React from "react";
import { useComponents, withWQ, createFallbackComponents } from "@wq/react";
import { useWizardContext } from "../hooks";

const WizardUnknownFallback = {
    components: {
        ...createFallbackComponents(
            ["ScrollView", "Typography"],
            "@wq/material",
        ),
        ...createFallbackComponents(
            ["FormContainer"],
            "@wq/form",
            "FormProvider",
        ),
    },
};

function WizardUnknown() {
    const { ScrollView, Typography, FormContainer } = useComponents(),
        { step } = useWizardContext();

    return (
        <ScrollView>
            <FormContainer>
                <Typography variant="h6">Unexpected step: {step}</Typography>
            </FormContainer>
        </ScrollView>
    );
}

export default withWQ(WizardUnknown, { fallback: WizardUnknownFallback });
