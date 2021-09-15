import React from 'react';
import { useComponents } from '@wq/react';
import PropTypes from 'prop-types';

export default function MappingFieldsetArray({ label, subform, children }) {
    const { Fieldset, Table, TableHead, TableBody, TableRow, TableTitle } =
        useComponents();
    return (
        <Fieldset label={label}>
            <Table>
                <TableHead>
                    <TableRow>
                        {subform
                            .filter(
                                (field) => field.control.appearance !== 'hidden'
                            )
                            .map((field) => (
                                <TableTitle key={field.name}>
                                    {field.label}
                                </TableTitle>
                            ))}
                    </TableRow>
                </TableHead>
                <TableBody>{children}</TableBody>
            </Table>
        </Fieldset>
    );
}

MappingFieldsetArray.propTypes = {
    label: PropTypes.string,
    subform: PropTypes.arrayOf(PropTypes.object),
    children: PropTypes.node,
};

MappingFieldsetArray.Fieldset = function Fieldset({ children }) {
    const { TableRow, TableCell } = useComponents();
    return (
        <TableRow>
            {React.Children.toArray(children)
                .filter((child) => child.props.control.appearance !== 'hidden')
                .map((child) => (
                    <TableCell key={child.props.name}>{child}</TableCell>
                ))}
        </TableRow>
    );
};
MappingFieldsetArray.Fieldset.propTypes = {
    children: PropTypes.node,
};
