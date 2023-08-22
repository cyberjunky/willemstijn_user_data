// This is a basic example strategy for Gekko.
// For more information on everything please refer
// to this document:
//
// https://gekko.wizb.it/docs/strategies/creating_a_strategy.html
//
// The example below is pretty bad investment advice: on every new candle there is
// a 10% chance it will recommend to change your position (to either
// long or short).

var log = require('../core/log');

var config = require('../core/util.js').getConfig();
var settings = config['experimenter'];

// Let's create our own strat
var strat = {};

// Prepare everything our method needs
strat.init = function() {
  this.name = 'Experimenter';
  this.requiredHistory = config.tradingAdvisor.historySize;
  console.log('experimenter init. settings:', settings)

  // dynamically build indicators
  for (let name in settings) {
    const typeParts = settings[name].type.split('.');
    if (typeParts[0] === 'talib') {
      // console.log('talib not yet implemented');
      console.log(`addTalibIndicator name=${name}, type=${typeParts[1]}, args:`, settings[name].args)
      this.addTalibIndicator(name, typeParts[1], settings[name].args);

    } else {
      if (settings[name].arg) {
        console.log(`addIndicator name=${name}, type=${typeParts[0]}, arg=${settings[name].arg}`)
        this.addIndicator(name, typeParts[0], settings[name].arg);
      } else if (settings[name].args) {
        console.log(`addIndicator name=${name}, type=${typeParts[0]}, args=${settings[name].args}`)
        this.addIndicator(name, typeParts[0], settings[name].args);
      } else {
        console.log(`addIndicator name=${name}, type=${typeParts[0]}`)
        this.addIndicator(name, typeParts[0]);
      }
    }
  }
  // this.addTalibIndicator('talibDema', 'dema', {
  //   optInTimePeriod: settings.talibDema
  // });

  // this.addIndicator('dema', 'DEMA', {
  //   short: settings.demaShort,
  //   long: settings.demaLong
  // });

  // this.addIndicator('ema', 'EMA', settings.emaWeight);
  // this.addIndicator('sma', 'SMA', settings.smaWeight);
}

// What happens on every new candle?
strat.update = function(candle) {

  // // Get a random number between 0 and 1.
  // this.randomNumber = Math.random();

  // // There is a 10% chance it is smaller than 0.1
  // this.toUpdate = this.randomNumber < 0.1;
}

// For debugging purposes.
strat.log = function() {
  log.debug('calculated random number:');
  log.debug('\t', this.randomNumber.toFixed(3));
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
