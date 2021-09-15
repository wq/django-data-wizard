import React, { useMemo } from 'react';
import { useComponents } from '@wq/react';
import { useRunInfo } from '../hooks';

export default function RunColumns() {
    const {
            id,
            label,
            result: { unknown_count, columns },
        } = useRunInfo(),
        [form, data] = useMemo(() => processFormData(columns), [columns]),
        {
            ScrollView,
            Typography,
            AutoForm,
            TableRow,
            TableCell,
            ContinueForm,
            MappingFieldsetArray,
        } = useComponents();

    if (!unknown_count) {
        return (
            <ScrollView>
                <ContinueForm>
                    <Typography variant="h6">Mapped Columns</Typography>
                    <Typography>The following columns are mapped.</Typography>
                    <MappingFieldsetArray
                        label={form[0].label}
                        subform={form[0].children}
                    >
                        {data.columns.map(({ id, column, name, mapping }) => (
                            <TableRow key={id}>
                                <TableCell>{column}</TableCell>
                                <TableCell>{name}</TableCell>
                                <TableCell>{mapping}</TableCell>
                            </TableRow>
                        ))}
                    </MappingFieldsetArray>
                </ContinueForm>
            </ScrollView>
        );
    } else {
        return (
            <ScrollView>
                <AutoForm
                    action={`datawizard/${id}/updatecolumns`}
                    method="POST"
                    backgroundSync={false}
                    form={form}
                    data={data}
                >
                    <Typography variant="h5">{label}</Typography>
                    <Typography variant="h6">Unknown Columns</Typography>
                    <Typography>
                        This file contains {unknown_count} column
                        {unknown_count > 1 ? 's' : ''} that{' '}
                        {unknown_count > 1 ? 'are' : 'is'} not yet recognized by
                        this database.
                    </Typography>
                </AutoForm>
            </ScrollView>
        );
    }
}

function processFormData(columns) {
    const column = (columns || []).find((column) => column.types),
        types = column ? column.types : [],
        mappingChoices = [];

    types.forEach(({ name: group, choices }) => {
        choices.forEach(({ id: name, label }) => {
            mappingChoices.push({ name, label, group });
        });
    });

    const form = [
        {
            type: 'repeat',
            name: 'columns',
            label: 'Columns',
            control: { appearance: 'mapping-fieldset-array' },
            children: [
                {
                    type: 'string',
                    name: 'column',
                    label: 'Column',
                    control: { appearance: 'read-only' },
                },
                {
                    type: 'select one',
                    name: 'type',
                    label: 'Type',
                    choices: [
                        { name: 'attribute', label: 'EAV Column' },
                        { name: 'meta', label: 'Column/Header' },
                        { name: 'instance', label: 'FK Value' },
                        { name: 'unresolved', label: 'Unresolved' },
                        { name: 'unknown', label: 'Unknown' },
                    ],
                    control: { appearance: 'hidden' },
                },
                {
                    type: 'string',
                    name: 'name',
                    label: 'Spreadsheet Value',
                    control: { appearance: 'read-only' },
                },
                {
                    type: 'select one',
                    name: 'mapping',
                    label: 'Mapping',
                    choices: mappingChoices,
                    control: { appearance: 'mapping-select' },
                },
            ],
        },
    ];
    const data = {
        columns: columns.map(({ rel_id: id, column, type, name, mapping }) => ({
            id,
            column,
            type,
            name,
            mapping,
        })),
    };
    return [form, data];
}
