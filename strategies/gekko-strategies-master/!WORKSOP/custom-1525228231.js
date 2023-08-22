// If you want to use your own trading methods you can
// write them here. For more information on everything you
// can use please refer to this document:
// 
// https://github.com/askmike/gekko/blob/stable/docs/trading_methods.md
// 
// The example below is pretty stupid: on every new candle there is
// a 10% chance it will recommand to change your position (to either
// long or short).

var config = require('../core/util.js').getConfig();
var settings = config.custom;

// Let's create our own strat
var strat = {};

// Prepare everything our method needs
strat.init = function() {
  this.currentTrend = 'long';
  this.requiredHistory = 0;
}

// What happens on every new candle?
strat.update = function(candle) {

  // Get a random number between 0 and 1.
  this.randomNumber = Math.random();

  // There is a 10% chance it is smaller than 0.1
  this.toUpdate = randomNumber < 0.1;
}

// For debugging purposes.
strat.log = function() {
  log.write('calculated random number:');
  log.write('\t', this.randomNumber.toFixed(3));
}

// Based on the newly calculated
// information, check if we should
// update or not.
strat.check = function() {

  // Only continue if we have a new update.
  if(!this.toUpdate)
    return;

  if(this.currentTrend === 'long') {

    // If it was long, set it to short
    this.currentTrend = 'short';
    this.advice('short');

  } else {

    // If it was short, set it to long
    this.currentTrend = 'long';
    this.advice('long');

  }
}

module.exports = strat;