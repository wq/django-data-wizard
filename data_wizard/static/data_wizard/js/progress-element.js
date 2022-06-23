/*
 * @wq/progress-element 2.0.0
 * fetch()-powered auto-updating HTML5 <progress> element
 * (c) 2014-2021, S. Andrew Sheppard
 * https://wq.io/license
 */

(function (global, factory) {
typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports, require('jquery')) :
typeof define === 'function' && define.amd ? define(['exports', 'jquery'], factory) :
(global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global['/progress-element'] = {}, global.$));
}(this, (function (exports, $) { 'use strict';

function _interopDefaultLegacy (e) { return e && typeof e === 'object' && 'default' in e ? e : { 'default': e }; }

var $__default = /*#__PURE__*/_interopDefaultLegacy($);

function asyncGeneratorStep(gen, resolve, reject, _next, _throw, key, arg) {
  try {
    var info = gen[key](arg);
    var value = info.value;
  } catch (error) {
    reject(error);
    return;
  }

  if (info.done) {
    resolve(value);
  } else {
    Promise.resolve(value).then(_next, _throw);
  }
}

function _asyncToGenerator(fn) {
  return function () {
    var self = this,
        args = arguments;
    return new Promise(function (resolve, reject) {
      var gen = fn.apply(self, args);

      function _next(value) {
        asyncGeneratorStep(gen, resolve, reject, _next, _throw, "next", value);
      }

      function _throw(err) {
        asyncGeneratorStep(gen, resolve, reject, _next, _throw, "throw", err);
      }

      _next(undefined);
    });
  };
}

function _defineProperty(obj, key, value) {
  if (key in obj) {
    Object.defineProperty(obj, key, {
      value: value,
      enumerable: true,
      configurable: true,
      writable: true
    });
  } else {
    obj[key] = value;
  }

  return obj;
}

function ownKeys(object, enumerableOnly) {
  var keys = Object.keys(object);

  if (Object.getOwnPropertySymbols) {
    var symbols = Object.getOwnPropertySymbols(object);
    if (enumerableOnly) symbols = symbols.filter(function (sym) {
      return Object.getOwnPropertyDescriptor(object, sym).enumerable;
    });
    keys.push.apply(keys, symbols);
  }

  return keys;
}

function _objectSpread2(target) {
  for (var i = 1; i < arguments.length; i++) {
    var source = arguments[i] != null ? arguments[i] : {};

    if (i % 2) {
      ownKeys(Object(source), true).forEach(function (key) {
        _defineProperty(target, key, source[key]);
      });
    } else if (Object.getOwnPropertyDescriptors) {
      Object.defineProperties(target, Object.getOwnPropertyDescriptors(source));
    } else {
      ownKeys(Object(source)).forEach(function (key) {
        Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key));
      });
    }
  }

  return target;
}

class Progress {
  constructor(config) {
    this.config = _objectSpread2({
      interval: 0.5
    }, config);

    if (!this.config.url) {
      throw new Error('No URL specified!');
    }
  }

  start() {
    this._throttle = 0;
    this._throttleCount = 0;
    this._lastProgress = null;
    this._timer = setInterval(() => this.update(), this.config.interval * 1000);
  }

  stop() {
    if (this._timer) {
      clearInterval(this._timer);
    }

    delete this._throttle;
    delete this._throttleCount;
    delete this._lastProgress;
    delete this._timer;
  }

  update() {
    var _this = this;

    return _asyncToGenerator(function* () {
      if (_this._pending) {
        return;
      }

      if (_this._throttleCount < _this._throttle) {
        _this._throttleCount += 1;
        return;
      } else {
        _this._throttleCount = 0;
      }

      var data;

      try {
        _this._pending = true;
        var controller = new AbortController(),
            timeout = setTimeout(() => controller.abort(), 10000),
            response = yield fetch(_this.config.url, {
          signal: controller.signal
        });
        clearTimeout(timeout);
        data = yield response.json();
        _this._pending = false;
      } catch (e) {
        _this._pending = false;

        if (e.name === 'AbortError') {
          _this.onError(new Error('Timeout while requesting status'));
        } else {
          _this.onError(e);
        }

        return;
      }

      var done = false;

      if (!data.total) {
        _this.onIndeterminate(data);

        _this._throttle++;
      } else {
        // Set to progress level
        if (_this._lastProgress && data.current < _this._lastProgress) ; else if (_this._lastProgress == data.current) {
          // No change since last check; check less often
          _this._throttle++;
        } else {
          // Change since last check; check more often
          _this._lastProgress = data.current;

          if (_this._throttle > 0) {
            _this._throttle--;
          }
        }

        if (data.current == data.total) {
          _this.onComplete(data);

          done = true;
        }
      }

      if (data.status == 'SUCCESS' && !done) {
        _this.onComplete(data);
      } else if (data.status == 'FAILURE') {
        _this.onFail(data);
      } else if (!done) {
        _this.onProgress(data);
      }

      if (data.location) {
        _this.onNavigate(data);
      }
    })();
  }

  onIndeterminate(data) {
    if (this.config.onIndeterminate) {
      this.config.onIndeterminate(data);
    }
  }

  onProgress(data) {
    if (this.config.onProgress) {
      this.config.onProgress(data);
    }
  }

  onError(error) {
    if (this.config.onError) {
      this.config.onError(error);
    }
  }

  onComplete(data) {
    if (this.config.onComplete) {
      this.config.onComplete(data);
    }

    this.stop();
  }

  onFail(data) {
    this.stop();

    if (this.config.onFail) {
      this.config.onFail(data);
    }
  }

  onNavigate(data) {
    this.stop();

    if (this.config.onNavigate) {
      this.config.onNavigate(data);
    }
  }

}

var _timers = {};
function run($page) {
  var $progress = $page.find('progress'),
      $status;

  if (!$progress.length) {
    return;
  }

  if ($progress.data('wq-status')) {
    $status = $page.find('#' + $progress.data('wq-status'));
  } // Look for a data-wq-url attribute to poll (and an optional data-interval attribute)


  var url = $progress.data('wq-url'),
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
      $progress.attr('max', null); // Fallback for old browsers

      $progress.html('Loading...');
      updateStatus(data);
    },

    onProgress(data) {
      $progress.attr('value', data.current);
      $progress.attr('max', data.total); // Fallback for old browsers

      $progress.html(data.current / data.total * 100 + '%');
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
      $__default['default']('.submit-row').show();
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
    }

  });

  _timers[url].start();
}
$__default['default'](document).ready(function () {
  run($__default['default']('body'));
});

exports.run = run;

Object.defineProperty(exports, '__esModule', { value: true });

})));
//# sourceMappingURL=progress-element.js.map
