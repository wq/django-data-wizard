import progress from '../progress';
import $ from 'jquery';
import mockFetch from 'jest-fetch-mock';

beforeAll(() => {
    global.fetch = mockFetch;
});

test('progress bar', async () => {
    const el = document.createElement('progress');
    el.dataset.wqUrl = 'test.json';
    document.body.appendChild(el);

    mockFetch.mockResponse(
        JSON.stringify({
            status: 'PROGRESS',
            current: 50,
            total: 100
        })
    );

    progress.run($('body'));

    await new Promise(res => setTimeout(res, 1000));

    expect(el.value).toEqual(50);
    expect(el.max).toEqual(100);
});
