import React from 'react';
import { useField } from 'formik';
import { useInputComponents } from '@wq/react';
import PropTypes from 'prop-types';

export default function MappingSelect(props) {
    const { name } = props,
        [, { value: type }] = useField(name.replace('mapping', 'type')),
        { Select, ReadOnly } = useInputComponents();

    if (type === 'unknown') {
        return <Select {...props} label="" placeholder="(No Selection)" />;
    } else {
        return <ReadOnly {...props} />;
    }
}

MappingSelect.propTypes = {
    name: PropTypes.string,
};
