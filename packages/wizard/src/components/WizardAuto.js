import React from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import { useWizardContext, useWizardInfo, useProgress } from "../hooks";

const WizardAutoFallback = {
    components: {
        ...createFallbackComponents(
            ["Typography", "LinearProgress", "ScrollView", "HorizontalView"],
            "@wq/material",
        ),
        ...createFallbackComponents(
            ["FormContainer", "CancelButton"],
            "@wq/form",
            "FormProvider",
        ),
    },
};

function WizardAuto() {
    const { returnPath } = useWizardContext(),
        { label } = useWizardInfo(),
        { value, error, status } = useProgress(),
        {
            Typography,
            LinearProgress,
            ScrollView,
            FormContainer,
            HorizontalView,
            CancelButton,
            View,
        } = useComponents();
    return (
        <ScrollView>
            <FormContainer>
                <Typography variant="h5">{label}</Typography>
                <LinearProgress
                    style={{ marginTop: 16, marginBottom: 16 }}
                    variant={value === null ? "indeterminate" : "determinate"}
                    value={value}
                />
                {status && (
                    <Typography color={error ? "error" : "textSecondary"}>
                        {status}
                    </Typography>
                )}
                {value === 0 && error && returnPath && (
                    <HorizontalView>
                        <CancelButton
                            to={returnPath}
                            variant="outlined"
                            color="secondary"
                        >
                            Back
                        </CancelButton>
                        <View />
                    </HorizontalView>
                )}
            </FormContainer>
        </ScrollView>
    );
}

export default withWQ(WizardAuto, { fallback: WizardAutoFallback });
