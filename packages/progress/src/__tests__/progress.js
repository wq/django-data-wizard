import { Progress } from '../progress';
import mockFetch from 'jest-fetch-mock';

beforeAll(() => {
    global.fetch = mockFetch;
});

test('progress api', async () => {
    mockFetch.mockResponse(
        JSON.stringify({
            status: 'PROGRESS',
            current: 50,
            total: 100,
        })
    );

    let state = {};

    const progress = new Progress({
        url: 'test.json',
        onProgress(s) {
            Object.assign(state, s);
        },
    });

    progress.start();

    await new Promise((res) => setTimeout(res, 1000));

    expect(state.current).toEqual(50);
    expect(state.total).toEqual(100);

    progress.stop();
});
