import React from "react";
import { useComponents, withWQ, createFallbackComponents } from "@wq/react";
import { useWizardInfo, useWizardContext } from "../hooks";
import ContinueForm from "./ContinueForm";

const WizardStartDefaults = {
    components: { ContinueForm },
};

const WizardStartFallback = {
    components: {
        ...createFallbackComponents(
            [
                "ScrollView",
                "Typography",
                "Table",
                "TableBody",
                "TableRow",
                "TableCell",
                "Link",
            ],
            "@wq/material",
        ),
        ...createFallbackComponents(
            ["FormContainer"],
            "@wq/form",
            "FormProvider",
        ),
    },
};

function WizardStart() {
    const {
            ScrollView,
            Typography,
            Table,
            TableBody,
            TableRow,
            TableCell,
            Link,
            FormContainer,
            ContinueForm,
        } = useComponents(),
        { label, serializer_label, record_count, last_update } =
            useWizardInfo(),
        { setStep } = useWizardContext();
    if (record_count !== null) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h5">{label}</Typography>
                    <Table>
                        <TableBody>
                            <TableRow>
                                <TableCell>Serializer</TableCell>
                                <TableCell>{serializer_label}</TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Records</TableCell>
                                <TableCell>
                                    <Link
                                        component="button"
                                        onClick={() => setStep("records")}
                                    >
                                        {record_count} record
                                        {record_count === 1 ? "" : "s"}{" "}
                                        imported.
                                    </Link>
                                </TableCell>
                            </TableRow>
                            <TableRow>
                                <TableCell>Last Updated</TableCell>
                                <TableCell>
                                    {new Date(last_update).toLocaleString()}
                                </TableCell>
                            </TableRow>
                        </TableBody>
                    </Table>
                </FormContainer>
            </ScrollView>
        );
    } else {
        return (
            <ScrollView>
                <ContinueForm submitLabel="Start Import">
                    <Typography variant="h6">
                        Click to start the import wizard.
                    </Typography>
                </ContinueForm>
            </ScrollView>
        );
    }
}

export default withWQ(WizardStart, {
    defaults: WizardStartDefaults,
    fallback: WizardStartFallback,
});
