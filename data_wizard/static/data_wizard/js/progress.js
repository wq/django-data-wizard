/* django-data-wizard 1.2.0 - progress.js
 * Simple AJAX polling for HTML5 <progress> element
 * (c) 2014-2019, S. Andrew Sheppard
 * https://wq.io/license
 */

/* global $ */

(function() {

var progress = {
    'name': 'progress',
    'config': {
        'interval': 0.5 // Polling interval (in seconds)
    }
};

// Internal setInterval ids
var _timers = {};
var _last = {};

// wq/app.js plugin
progress.run = function($page) {
    var $progress = $page.find('progress'),
        $status;
    if (!$progress.length) {
        return;
    }

    if ($progress.data('wq-status')) {
        $status = $page.find('#' + $progress.data('wq-status'));
    }
    progress.start($progress, $status);
    $page.on('pagehide', function() {
        progress.stop($progress);
    });
};

// progress.start accepts a jQuery-wrapped progress element and looks for a
// data-wq-url attribute to poll (and an optional data-interval attribute)
progress.start = function($progress, $status) {
    var url = $progress.data('wq-url');
    var interval = $progress.data('wq-interval') || progress.config.interval;
    if (!url || _timers[url]) {
        return;
    }
    _timers[url] = setInterval(
        progress.timer($progress, url, $status),
        interval * 1000
    );
};

// progress.stop stops a timer started with progress.start
progress.stop = function($progress) {
    var url = $progress.data('wq-url');
    if (!url || !_timers[url]) {
        return;
    }
    clearInterval(_timers[url]);
};

// progress.complete/progress.fail stop a timer started with progress.start,
// with a hook for custom response
progress.complete = function($progress, data) {
    progress.stop($progress);
    if (progress.config.onComplete) {
        progress.config.onComplete($progress, data);
    }
};

progress.fail = function($progress, data) {
    progress.stop($progress);
    if (progress.config.onFail) {
        progress.config.onFail($progress, data);
    }
    $('.submit-row').show();
};

// progress.timer generates a function suitable for setInterval
// (with $progress and url bound to scope).
progress.timer = function($progress, url, $status) {
    var throttle = 0,
        i = 0;
    return function() {
        if (i < throttle) {
            i += 1;
            return;
        } else {
            i = 0;
        }
        fetch(url).then(function(response) {
            return response.json();
        }).then(function(data) {
            var done = false;
            if (!data.total) {
                // Set to "intermediate" state
                $progress.attr('value', null);
                $progress.attr('max', null);

                // Fallback for old browsers
                $progress.html('Loading...');

                throttle++;
            } else {
                // Set to progress level
                if (_last[url] && data.current < _last[url]) {
                    // Assume out-of order response; no update
                    /* jshint noempty: false */
                } else if (_last[url] == data.current) {
                    // No change since last check; check less often
                    throttle++;
                } else {
                    // Change since last check; check more often
                    _last[url] = data.current;
                    if (throttle > 0) {
                        throttle--;
                    }
                    $progress.attr('value', data.current);
                    $progress.attr('max', data.total);

                    // Fallback for old browsers
                    $progress.html(data.current / data.total * 100 + "%");
                }

                // Check for completion
                if (data.current == data.total) {
                    progress.complete($progress, data);
                    done = true;
                }
            }
            if (data.status == "SUCCESS" && !done) {
                progress.complete($progress, data);
                $progress.attr('value', data.total || 0);
                $progress.attr('max', data.total || 0);
                if ($status) {
                     $status.removeClass('error');
                }
                done = true;
            } else if (data.status == "FAILURE") {
                $progress.attr('value', 0);
                $progress.attr('max', data.total || 0);
                if ($status) {
                     $status.addClass('error');
                }
                progress.fail($progress, data);
            } else if (!done && progress.config.onProgress) {
                progress.config.onProgress($progress, data);
            }
            if ((data.error || data.message) && $status) {
                $status.text(data.error || data.message);
            }
            if (data.location) {
                window.location.href = data.location;
            }
        })['catch'](function(err) {
            $status.text(err).addClass('error');
            throttle += 1;
        });
    };
};

$(document).ready(function() {
    progress.run($('body'));
});

window.data_wizard = {
    'progress': progress
};

})();
