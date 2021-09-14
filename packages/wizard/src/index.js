import * as components from './components/index';
import * as views from './views/index';

const wizard = {
    name: 'wizard',
    components: { ...components },
    views: { ...views },
};

export default wizard;
export * from './components/index';
export * from './views/index';
