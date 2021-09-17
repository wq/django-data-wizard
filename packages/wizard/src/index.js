import * as components from './components/index';
import * as inputs from './inputs/index';
import * as views from './views/index';
import * as icons from './icons';

const wizard = {
    name: 'wizard',
    components: { ...components },
    inputs: { ...inputs },
    views: { ...views },
    icons: { ...icons },
    async context(ctx, routeInfo) {
        const { page, mode, full_path } = routeInfo;
        if (
            page === 'run' &&
            mode &&
            !['list', 'detail', 'edit', 'auto', 'data'].includes(mode)
        ) {
            const response = await fetch(full_path, {
                    headers: { Accept: 'application/json' },
                }),
                data = await response.json();
            if (mode !== 'records') {
                await this.app.models.run.update([data]);
            }
            return data;
        }
    },
};

export default wizard;
export * from './components/index';
export * from './views/index';
export * from './hooks';
