import React from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import { useWizardContext, useWizardInfo, useWizardQuery } from "../hooks";
import PropTypes from "prop-types";

const WizardRecordsFallback = {
    components: {
        ...createFallbackComponents(
            [
                "Typography",
                "Table",
                "TableHead",
                "TableBody",
                "TableRow",
                "TableTitle",
                "TableCell",
                "Link",
                "ScrollView",
                "HorizontalView",
                "View",
            ],
            "@wq/material",
        ),
        ...createFallbackComponents(
            ["FormContainer", "CancelButton"],
            "@wq/form",
            "FormProvider",
        ),
    },
};

function WizardRecords() {
    const {
            Typography,
            Table,
            TableHead,
            TableBody,
            TableRow,
            TableTitle,
            TableCell,
            ScrollView,
            FormContainer,
            HorizontalView,
            CancelButton,
            View,
        } = useComponents(),
        { returnPath } = useWizardContext(),
        { label } = useWizardInfo(),
        {
            data: records,
            isPending,
            isError,
            error,
        } = useWizardQuery("records", "records"),
        hasRecords = records && records.length > 0;

    return (
        <ScrollView>
            <FormContainer>
                <Typography variant="h5">{label}</Typography>
                <Typography variant="h6">Imported Records</Typography>
                <Typography>Import Complete!</Typography>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableTitle>Row</TableTitle>
                            <TableTitle>Record</TableTitle>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {!hasRecords && (
                            <TableCell colspan={2}>
                                {isPending ? (
                                    "Loading..."
                                ) : isError ? (
                                    <Typography color="error">
                                        Error: {error.message}
                                    </Typography>
                                ) : (
                                    "No records imported."
                                )}
                            </TableCell>
                        )}
                        {hasRecords &&
                            records.map((record) => (
                                <TableRow key={record.row}>
                                    <TableCell>{record.row}</TableCell>
                                    <TableCell>
                                        <RecordLink {...record} />
                                    </TableCell>
                                </TableRow>
                            ))}
                    </TableBody>
                </Table>
                {returnPath && (
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

function RecordLink({ success, object_url, object_label, fail_reason }) {
    const { Link, Typography } = useComponents();
    if (success) {
        if (object_url) {
            return <Link to={object_url}>{object_label}</Link>;
        } else {
            return object_label;
        }
    } else {
        return (
            <Typography color="error">
                {fail_reason || "Unknown Error"}
            </Typography>
        );
    }
}

RecordLink.propTypes = {
    success: PropTypes.bool,
    object_url: PropTypes.string,
    object_label: PropTypes.string,
    fail_reason: PropTypes.string,
};

export default withWQ(WizardRecords, { fallback: WizardRecordsFallback });
