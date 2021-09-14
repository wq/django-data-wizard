import React from 'react';
import { DefaultDetail, useComponents } from '@wq/react';
import { View } from '@wq/material';

export default function RunData() {
    const { Progress } = useComponents();
    return (
        <View>
            <DefaultDetail />
            <Progress />
        </View>
    );
}
