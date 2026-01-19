import React from "react";
import { useComponents, createFallbackComponents, withWQ } from "@wq/react";
import PropTypes from "prop-types";

const ReadOnlyFallback = {
    components: {
        ...createFallbackComponents(["Typography"], "@wq/material"),
        ...createFallbackComponents(["useField"], "@wq/form", "FormProvider"),
    },
};

function ReadOnly({ name }) {
    const { useField, Typography } = useComponents(),
        field = useField(name),
        value = field?.[1]?.value;
    return <Typography>{value}</Typography>;
}

ReadOnly.propTypes = {
    name: PropTypes.string,
};

export default withWQ(ReadOnly, {
    fallback: ReadOnlyFallback,
});
