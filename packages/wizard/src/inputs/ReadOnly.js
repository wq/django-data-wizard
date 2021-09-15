import React from 'react';
import { useField } from 'formik';
import { useComponents } from '@wq/react';
import PropTypes from 'prop-types';

export default function ReadOnly({ name }) {
    const [, { value }] = useField(name),
        { Typography } = useComponents();
    return <Typography>{value}</Typography>;
}

ReadOnly.propTypes = {
    name: PropTypes.string,
};
