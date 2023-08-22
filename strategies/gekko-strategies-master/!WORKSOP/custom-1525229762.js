/*

  RSI - cykedev 14/02/2014

  (updated a couple of times since, check git history)

 */
// helpers
var _ = require('lodash');
var log = require('../core/log.js');

var RSI = require('./indicators/RSI.js');

// let's create our own method
var method = {};

// prepare everything our method needs
method.init = function() {
  this.name = 'RSI';

  this.trend = {
    direction: 'none',
    duration: 0,
    persisted: false,
    adviced: false
  };

  this.requiredHistory = this.tradingAdvisor.historySize;

  // define the indicators we need
  this.addIndicator('rsi', 'RSI', this.settings);
}

// for debugging purposes log the last
// calculated parameters.
method.log = function(candle) {
  var digits = 8;
  var rsi = this.indicators.rsi;

  log.debug('calculated RSI properties for candle:');
  log.debug('\t', 'rsi:', rsi.result.toFixed(digits));
  log.debug('\t', 'price:', candle.close.toFixed(digits));
}

method.check = function() {
  var rsi = this.indicators.rsi;
  var rsiVal = rsi.result;

  if(rsiVal > this.settings.thresholds.high) {

    // new trend detected
    if(this.trend.direction !== 'high')
      this.trend = {
        duration: 0,
        persisted: false,
        direction: 'high',
        adviced: false
      };

    this.trend.duration++;

    log.debug('In high since', this.trend.duration, 'candle(s)');

    if(this.trend.duration >= this.settings.thresholds.persistence)
      this.trend.persisted = true;

  } else if(rsiVal <= this.settings.thresholds.high && this.trend.direction === 'high' && this.trend.persisted && !this.trend.adviced) {
    this.trend.adviced = true;
    this.advice('short');
    log.debug('Go short');
  } else if(rsiVal < this.settings.thresholds.low) {

    // new trend detected
    if(this.trend.direction !== 'low')
      this.trend = {
        duration: 0,
        persisted: false,
        direction: 'low',
        adviced: false
      };

    this.trend.duration++;

    log.debug('In low since', this.trend.duration, 'candle(s)');

    if(this.trend.duration >= this.settings.thresholds.persistence)
      this.trend.persisted = true;


  } else if(rsiVal >= this.settings.thresholds.low && this.trend.direction === 'low' && this.trend.persisted && !this.trend.adviced) {
    this.trend.adviced = true;
    this.advice('long');
    log.debug('Go long');
  } else {

    log.debug('In no trend');
    this.advice();
  }
}

module.exports = method;
