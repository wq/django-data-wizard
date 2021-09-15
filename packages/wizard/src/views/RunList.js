import React from 'react';
import { useComponents, useList, useReverse } from '@wq/react';

export default function RunList() {
    const {
            Typography,
            Link,
            Table,
            TableHead,
            TableBody,
            TableRow,
            TableTitle,
            TableCell,
            Center,
        } = useComponents(),
        { list, empty } = useList(),
        reverse = useReverse();

    return (
        <Center>
            <Typography variant="h4">Django Data Wizard</Typography>
            <Table>
                <TableHead>
                    <TableRow>
                        <TableTitle>Run</TableTitle>
                        <TableTitle>Serializer</TableTitle>
                        <TableTitle>Records</TableTitle>
                        <TableTitle>Last Update</TableTitle>
                    </TableRow>
                </TableHead>
                <TableBody>
                    {empty && (
                        <TableCell colspan={4}>No previous runs.</TableCell>
                    )}
                    {list.map(
                        ({
                            id,
                            label,
                            serializer_label,
                            record_count,
                            last_update,
                        }) => (
                            <TableRow key={id}>
                                <TableCell>
                                    <Link to={reverse('run_detail', id)}>
                                        {label}
                                    </Link>
                                </TableCell>
                                <TableCell>{serializer_label || '-'}</TableCell>
                                <TableCell>
                                    {typeof record_count === 'number'
                                        ? record_count
                                        : record_count || '-'}
                                </TableCell>
                                <TableCell>
                                    {last_update
                                        ? new Date(last_update).toLocaleString()
                                        : '-'}
                                </TableCell>
                            </TableRow>
                        )
                    )}
                </TableBody>
            </Table>
        </Center>
    );
}
