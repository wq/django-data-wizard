import React from 'react';
import {
    useRenderContext,
    useRouteInfo,
    useComponents,
    useReverse,
} from '@wq/react';

export default function SourceDetail() {
    const reverse = useReverse(),
        context = useRenderContext(),
        { page, item_id, page_config } = useRouteInfo(),
        {
            ScrollView,
            PropertyTable,
            Form,
            SubmitButton,
            Fab,
            HorizontalView,
            View,
        } = useComponents(),
        form = page_config.form || [{ name: 'label' }],
        editUrl = reverse(`${page}_edit`, item_id),
        content_type_id =
            page_config.content_type_id || `sources.${page_config.name}`,
        object_id = item_id;

    return (
        <>
            <ScrollView>
                <Form
                    action="datawizard/"
                    method="POST"
                    data={{ content_type_id, object_id }}
                    backgroundSync={false}
                >
                    <PropertyTable form={form} values={context} />
                    <HorizontalView>
                        <View />

                        <SubmitButton icon="wizard">
                            Start Data Wizard
                        </SubmitButton>
                    </HorizontalView>
                </Form>
            </ScrollView>
            {page_config.can_change !== false && (
                <Fab icon="edit" to={editUrl} />
            )}
        </>
    );
}
