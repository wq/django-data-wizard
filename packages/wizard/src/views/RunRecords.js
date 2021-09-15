import React from 'react';
import { useComponents } from '@wq/react';
import { useRunInfo } from '../hooks';
import PropTypes from 'prop-types';

export default function RunRecords() {
    const {
            Typography,
            Table,
            TableHead,
            TableBody,
            TableRow,
            TableTitle,
            TableCell,
            Center,
            CloseWizard,
        } = useComponents(),
        runInfo = useRunInfo(),
        { label, records } = runInfo,
        hasRecords = records && records.length > 0;

    return (
        <Center>
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
                        <TableCell colspan={2}>No records imported.</TableCell>
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
            <CloseWizard />
        </Center>
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
                {fail_reason || 'Unknown Error'}
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
