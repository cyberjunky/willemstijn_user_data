// helpers
var _ = require('lodash');
var log = require('../core/log.js');

// configuration
var config = require('../core/util.js').getConfig();
var settings = config.CCI;
var pposettings = config.PPO;


// let's create our own method
var method = {};

// teach our trading method events
var Util = require('util');

// prepare everything our method needs
method.init = function() {
  this.currentTrend;
  this.requiredHistory = config.tradingAdvisor.historySize;

  this.age = 0;
  this.trend = {
    direction: 'undefined',
    duration: 0,
    persisted: false,
    adviced: false
  };
  this.historySize = config.tradingAdvisor.historySize;
  this.uplevel = config.CCI.thresholds.up;
  this.downlevel = config.CCI.thresholds.down;
  this.persisted = config.CCI.thresholds.persistence;

  // log.debug("CCI started with:\nup:\t", this.uplevel, "\ndown:\t", this.downlevel, "\npersistence:\t", this.persisted);
  // define the indicators we need
  this.addIndicator('alli', 'Alligator', config.Alligator);
}

// what happens on every new candle?
method.update = function(candle) {
}

// for debugging purposes: log the last calculated
// EMAs and diff.
method.log = function() {
    var alli = this.indicators.alli;
    if (typeof(alli.result) == 'boolean') {
        log.debug('Insufficient data available. Age: ', alli.size, ' of ', alli.maxSize);
//        log.debug('ind: ', cci.TP.result, ' ', cci.TP.age, ' ', cci.TP.depth);
        return;
    }

    log.debug('calculated Alligator state for candle:');
    log.debug('\t', 'Price:\t\t\t', this.lastPrice);
    log.debug('\t', 'SSMAJaws:\t', alli.SSMAJaws.toFixed(8));
    log.debug('\t', 'SSMATeeth:\t', alliSSMA.Teeth.toFixed(8));
    log.debug('\t', 'SSMALips/n:\t', alli.SSMALips.toFixed(8));
    if (typeof(cci.result) == 'boolean' )
        log.debug('\t In sufficient data available.');
    else
        log.debug('\t', 'Alli:\t', cci.result.toFixed(2));
}

/*
 * 
 */
method.check = function() {


  var price = this.lastPrice;


    this.age++;
    var alli = this.indicators.alli;

    if (typeof(alli.result) == 'number') {

        // overbought?
        if (alli.result >= this.uplevel && (this.trend.persisted || this.persisted == 0) && !this.trend.adviced && this.trend.direction == 'overbought' ) {
            this.trend.adviced = true;
            this.trend.duration++;
            this.advice('short');
        } else if (alli.result >= this.uplevel && this.trend.direction != 'overbought') {
            this.trend.duration = 1;
            this.trend.direction = 'overbought';
            this.trend.persisted = false;
            this.trend.adviced = false;
            if (this.persisted == 0) {
                this.trend.adviced = true;
                this.advice('short');
            }
        } else if (alli.result >= this.uplevel) {
            this.trend.duration++;
            if (this.trend.duration >= this.persisted) {
                this.trend.persisted = true;
            }
        } else if (alli.result <= this.downlevel && (this.trend.persisted || this.persisted == 0) && !this.trend.adviced && this.trend.direction == 'oversold') {
            this.trend.adviced = true;
            this.trend.duration++;
            this.advice('long');
        } else if (alli.result <= this.downlevel && this.trend.direction != 'oversold') {
            this.trend.duration = 1;
            this.trend.direction = 'oversold';
            this.trend.persisted = false;
            this.trend.adviced = false;
            if (this.persisted == 0) {
                this.trend.adviced = true;
                this.advice('long');
            }
        } else if (alli.result <= this.downlevel) {
            this.trend.duration++;
            if (this.trend.duration >= this.persisted) {
                this.trend.persisted = true;
            }
        } else {
            if( this.trend.direction != 'nodirection') {
                this.trend = {
                    direction: 'nodirection',
                    duration: 0,
                    persisted: false,
                    adviced: false
                };
            } else {
                this.trend.duration++;
            }
            this.advice();
        }
                
    } else {
        this.advice();
    }

    log.debug("Trend: ", this.trend.direction, " for ", this.trend.duration);
}

module.exports = method;
