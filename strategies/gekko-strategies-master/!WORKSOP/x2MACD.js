/*
  
  MACD, double-EMA variant
  by kuzetsa 2014 June 26
  (CEXIO lizards variant)

  only change is x2EMA instead of (x1)EMA

 */

// helpers
var _ = require('lodash');
var log = require('../core/log.js');

// configuration
var config = require('../core/util.js').getConfig();
var settings = config.x2MACD;

// let's create our own method
var method = {};

// prepare everything our method needs
method.init = function() {

  this.name = 'x2MACD';

  // keep state about the current trend
  // here, on every new candle we use this
  // state object to check if we need to
  // report it.
  this.trend = {
    direction: 'none',
    duration: 0
  };

  // how many candles do we need as a base
  // before we can start giving advice?
  this.requiredHistory = config.tradingAdvisor.historySize;

  // define the indicators we need
  this.addIndicator('x2macd', 'x2MACD', settings);

}

// what happens on every new candle?
method.update = function(candle) {
  // nothing!
}

// for debugging purposes: log the last calculated
// EMAs and diff.
method.log = function() {
  var digits = 8;
  var x2macd = this.indicators.x2macd;

  var diff = x2macd.diff;
  var signal = x2macd.signal.result;

  log.debug('calculated MACD properties for candle:');
  log.info('\t', 'short:', x2macd.short.result.toFixed(digits));
  log.info('\t', 'long:', x2macd.long.result.toFixed(digits));
  log.info('\t', 'macd:', diff.toFixed(digits));
  log.info('\t', 'signal:', signal.toFixed(digits));
  log.info('\t', 'macdiff:', x2macd.result.toFixed(digits));  
}

method.check = function() {
  var price = this.lastPrice;
  var x2macd = this.indicators.x2macd;

  var long = x2macd.long.result;
  var short = x2macd.short.result;
  var signal = x2macd.signal.result;
  var macddiff = x2macd.result;

  if(macddiff > settings.thresholds.up) {

    // new trend detected
    if(this.trend.direction !== 'up')
      // reset the state for the new trend
      this.trend = {
        duration: 0,
        direction: 'up',
      };

    this.trend.duration++;

    log.info('In uptrend since', this.trend.duration, 'candle(s)');

      this.advice('long');

  } else {

      this.trend = {
        duration: 0,
        direction: 'lizards',
      };


    this.advice('lizards');

  }
}

module.exports = method;
