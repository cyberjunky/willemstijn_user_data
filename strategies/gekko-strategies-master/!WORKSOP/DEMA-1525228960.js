// helpers
var _ = require('lodash');
var log = require('../core/log.js');

// let's create our own method
var method = {};

// prepare everything our method needs
method.init = function() {
  this.name = 'DEMA';

  this.currentTrend;
  this.requiredHistory = this.tradingAdvisor.historySize;

  // define the indicators we need
  this.addIndicator('dema', 'DEMA', this.settings);
}

// what happens on every new candle?
method.update = function(candle) {
  // nothing!
}

// for debugging purposes: log the last calculated
// EMAs and diff.
method.log = function() {
  var dema = this.indicators.dema;

  log.debug('calculated DEMA properties for candle:');
  log.debug('\t', 'long ema:', dema.long.result.toFixed(8));
  log.debug('\t', 'short ema:', dema.short.result.toFixed(8));
  log.debug('\t diff:', dema.result.toFixed(5));
  log.debug('\t DEMA age:', dema.short.age, 'candles');
}

method.check = function(candle) {
  var dema = this.indicators.dema;
  var diff = dema.result;
  var price = candle.close;

  var message = '@ ' + price.toFixed(8);

  if(diff > this.settings.thresholds.up) {
    log.debug('we are currently in uptrend', message);

    if(this.currentTrend !== 'up') {
      this.currentTrend = 'up';
      this.advice('long');
      log.debug('bought', message);
    } else
      this.advice();

  } else if(diff < this.settings.thresholds.down) {
    log.debug('we are currently in a downtrend', message);

    if(this.currentTrend !== 'down') {
      this.currentTrend = 'down';
      this.advice('short');
      log.debug('sold', message);
    } else
      this.advice();

  } else {
    log.debug('we are currently not in an up or down trend', message);
    this.advice();
  }
}

module.exports = method;
