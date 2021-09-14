import $ from 'jquery';
import { Progress } from '@wq/progress';

// Active progress instances
var _timers = {};

export function run($page) {
    var $progress = $page.find('progress'),
        $status;
    if (!$progress.length) {
        return;
    }

    if ($progress.data('wq-status')) {
        $status = $page.find('#' + $progress.data('wq-status'));
    }
    // Look for a data-wq-url attribute to poll (and an optional data-interval attribute)
    const url = $progress.data('wq-url'),
        interval = $progress.data('wq-interval') || 0.5;

    if (!url || _timers[url]) {
        return;
    }
    function updateStatus(data) {
        if ((data.error || data.message) && $status) {
            $status.text(data.error || data.message);
        }
    }
    _timers[url] = new Progress({
        url,
        interval,
        onIndeterminate(data) {
            // Set to "intermediate" state
            $progress.attr('value', null);
            $progress.attr('max', null);

            // Fallback for old browsers
            $progress.html('Loading...');
            updateStatus(data);
        },
        onProgress(data) {
            $progress.attr('value', data.current);
            $progress.attr('max', data.total);

            // Fallback for old browsers
            $progress.html((data.current / data.total) * 100 + '%');
            updateStatus(data);
        },
        onComplete(data) {
            $progress.attr('value', data.total || 0);
            $progress.attr('max', data.total || 0);
            if ($status) {
                $status.removeClass('error');
            }
            updateStatus(data);
        },
        onFail(data) {
            $progress.attr('value', 0);
            $progress.attr('max', data.total || 0);
            if ($status) {
                $status.addClass('error');
            }
            updateStatus(data);
            $('.submit-row').show();
        },
        onError(err) {
            if ($status) {
                $status.text(err).addClass('error');
            } else {
                console.error(err);
            }
        },
        onNavigate(data) {
            window.location.href = data.location;
        },
    });
    _timers[url].start();
}

$(document).ready(function () {
    run($('body'));
});
