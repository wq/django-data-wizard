import React from 'react';
import { useComponents, useReverse } from '@wq/react';
import { useRunInfo } from '../hooks';

export default function RunDetail() {
    const {
            ScrollView,
            Typography,
            Table,
            TableBody,
            TableRow,
            TableCell,
            Link,
            Center,
            ContinueForm,
        } = useComponents(),
        runInfo = useRunInfo(),
        { id, label, serializer_label, record_count, last_update } = runInfo,
        reverse = useReverse();
    if (record_count !== null) {
        return (
            <Center>
                <Typography variant="h5">{label}</Typography>
                <Table>
                    <TableBody>
                        <TableRow>
                            <TableCell>Serializer</TableCell>
                            <TableCell>
                                {typeof serializer_label === 'function'
                                    ? serializer_label.call(runInfo)
                                    : serializer_label}
                            </TableCell>
                        </TableRow>
                        <TableRow>
                            <TableCell>Records</TableCell>
                            <TableCell>
                                <Link to={reverse('run_records', id)}>
                                    {record_count} record
                                    {record_count === 1 ? '' : 's'} imported.
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
            </Center>
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
