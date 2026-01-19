import React from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import ReadOnly from "./ReadOnly";
import PropTypes from "prop-types";

const MappingSelectDefaults = {
        components: { ReadOnly },
    },
    MappingSelectFallback = {
        components: createFallbackComponents(
            ["Select", "useField"],
            "@wq/form",
            "FormProvider",
        ),
    };

function MappingSelect(props) {
    const { name } = props,
        { Select, ReadOnly, useField } = useComponents(),
        typeField = useField(name.replace("mapping", "type")),
        type = typeField?.[1]?.value;

    if (type === "unknown") {
        return <Select {...props} label="" placeholder="(No Selection)" />;
    } else {
        return <ReadOnly {...props} />;
    }
}

MappingSelect.propTypes = {
    name: PropTypes.string,
};

export default withWQ(MappingSelect, {
    defaults: MappingSelectDefaults,
    fallback: MappingSelectFallback,
});
