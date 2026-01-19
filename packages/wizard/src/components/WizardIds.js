import React, { useMemo } from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import ContinueForm from "./ContinueForm";
import MappingFieldsetArray from "./MappingFieldsetArray";
import MappingSelect from "./MappingSelect";
import ReadOnly from "./ReadOnly";
import { useSubmitForm, useWizardInfo, useWizardQuery } from "../hooks";

const WizardIdsDefaults = {
        components: {
            ContinueForm,
            MappingFieldsetArray,
            MappingSelect,
            ReadOnly,
        },
    },
    WizardIdsFallback = {
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
                ["AutoForm", "FormContainer"],
                "@wq/form",
                "FormProvider",
            ),
        },
    };

function WizardIds() {
    const { label } = useWizardInfo(),
        { data: result, isPending, isError, error } = useWizardQuery("ids"),
        [form, data] = useMemo(
            () => processFormData(result?.types || []),
            [result],
        ),
        unknown_count = result?.unknown_count || 0,
        submitForm = useSubmitForm(),
        {
            ScrollView,
            Typography,
            AutoForm,
            FormContainer,
            TableRow,
            TableCell,
            ContinueForm,
            MappingFieldsetArray,
        } = useComponents();
    if (isPending) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6">Loading identifiers...</Typography>
                </FormContainer>
            </ScrollView>
        );
    } else if (isError) {
        return (
            <ScrollView>
                <FormContainer>
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6" color="error">
                        Error: {error.message}
                    </Typography>
                </FormContainer>
            </ScrollView>
        );
    } else if (!unknown_count) {
        return (
            <ScrollView>
                <ContinueForm>
                    <Typography variant="h6">Mapped Identifiers</Typography>
                    <Typography>
                        The following identifiers are mapped.
                    </Typography>
                    {form.map(({ name, label, children }) => (
                        <MappingFieldsetArray
                            key={name}
                            label={label}
                            subform={children}
                        >
                            {data[name].map(({ id, name, count, mapping }) => (
                                <TableRow key={id}>
                                    <TableCell>{name}</TableCell>
                                    <TableCell>{count}</TableCell>
                                    <TableCell>{mapping}</TableCell>
                                </TableRow>
                            ))}
                        </MappingFieldsetArray>
                    ))}
                </ContinueForm>
            </ScrollView>
        );
    } else {
        return (
            <ScrollView>
                <AutoForm
                    action="updateids"
                    onSubmit={submitForm}
                    form={form}
                    data={data}
                >
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6">Unknown Identifiers</Typography>
                    <Typography>
                        This file contains {unknown_count} identifier
                        {unknown_count > 1 ? "s" : ""} that{" "}
                        {unknown_count > 1 ? "are" : "is"} not yet recognized by
                        this database.
                    </Typography>
                </AutoForm>
            </ScrollView>
        );
    }
}

function processFormData(types) {
    const form = [],
        data = {};

    types.forEach(({ type_id, type_label, ids }) => {
        const fieldName = type_id.replace(".", "_"),
            id = (ids || []).find((id) => id.choices),
            choices = id
                ? id.choices.map(({ id: name, label }) => ({ name, label }))
                : [];

        form.push({
            type: "repeat",
            name: fieldName,
            label: `${type_label} Identifiers`,
            control: { appearance: "mapping-fieldset-array" },
            children: [
                {
                    type: "string",
                    name: "name",
                    label: "Identifier",
                    control: { appearance: "read-only" },
                },
                {
                    type: "select one",
                    name: "type",
                    label: "Type",
                    choices: [
                        { name: "mapped", label: "Mapped" },
                        { name: "unknown", label: "Unknown" },
                    ],
                    control: { appearance: "hidden" },
                },
                {
                    type: "int",
                    name: "count",
                    label: "Occurrences",
                    control: { appearance: "read-only" },
                },
                {
                    type: "select one",
                    name: "mapping",
                    label: type_label,
                    choices,
                    control: { appearance: "mapping-select" },
                },
            ],
        });

        data[fieldName] = ids.map(
            ({
                ident_id: id,
                value: name,
                count,
                match: mapping,
                unknown,
            }) => ({
                id,
                name,
                type: unknown ? "unknown" : "resolved",
                count,
                mapping,
            }),
        );
    });

    return [form, data];
}

export default withWQ(WizardIds, {
    defaults: WizardIdsDefaults,
    fallback: WizardIdsFallback,
});
