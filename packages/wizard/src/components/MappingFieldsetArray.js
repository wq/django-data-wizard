import React from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import PropTypes from "prop-types";

const MappingFieldsetArrayFallback = {
    components: {
        ...createFallbackComponents(
            [
                "Table",
                "TableHead",
                "TableBody",
                "TableRow",
                "TableTitle",
                "TableCell",
            ],
            "@wq/material",
        ),
        ...createFallbackComponents(["Fieldset"], "@wq/form", "FormProvider"),
    },
};

function MappingFieldsetArray({ label, subform, children }) {
    const { Table, TableHead, TableBody, TableRow, TableTitle, Fieldset } =
        useComponents();
    return (
        <Fieldset label={label}>
            <Table>
                <TableHead>
                    <TableRow>
                        {subform
                            .filter(
                                (field) =>
                                    field.control.appearance !== "hidden",
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

const MappingFieldsetArrayWQ = withWQ(MappingFieldsetArray, {
    fallback: MappingFieldsetArrayFallback,
});

MappingFieldsetArrayWQ.Fieldset = function Fieldset({ children }) {
    const { TableRow, TableCell } = useComponents();
    return (
        <TableRow>
            {React.Children.toArray(children)
                .filter((child) => child.props.control.appearance !== "hidden")
                .map((child) => (
                    <TableCell key={child.props.name}>{child}</TableCell>
                ))}
        </TableRow>
    );
};
MappingFieldsetArrayWQ.Fieldset.propTypes = {
    children: PropTypes.node,
};

export default MappingFieldsetArrayWQ;
