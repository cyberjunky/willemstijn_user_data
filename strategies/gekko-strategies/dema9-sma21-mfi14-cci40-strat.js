// Determine generic variables through the script
// e.g. the limit that has to cross before taking action
var ccilimit = 0 // 43 is goed
var mfilimit = 43 // 43 is goed
var strat = {};

// Configure the indicators to use in this strategy
strat.init = function () {
  this.addTulipIndicator('dema', 'dema', {
    optInTimePeriod: 9
  })
  this.addTulipIndicator('sma', 'sma', {
    optInTimePeriod: 21
  })
  this.addTulipIndicator('cci', 'cci', {
    optInTimePeriod: 40
  })
  this.addTulipIndicator('mfi', 'mfi', {
    optInTimePeriod: 14
  })
}

// Start the actual strategy and check this on each candle.
// See config.js for the timeframe this candle is.
strat.check = function (candle) {
  // Configure the indicators for calculation in the strategy
  var day = candle.start.format()
  var dema = this.tulipIndicators.dema.result.result
  var sma = this.tulipIndicators.sma.result.result
  var cci = this.tulipIndicators.cci.result.result
  var mfi = this.tulipIndicators.mfi.result.result

  // === CONSOLE OUTPUT CONFIGURATION ===
  // Rounding the numbers for easier checking of the indicators on the console
  // Do not use rounded numbers when backtesting, they give worse results
  var candleclose = candle.close.toFixed(2)
  var demanum = Number(dema); demaround = demanum.toFixed(2);
  var smanum = Number(sma); smaround = smanum.toFixed(2);
  var ccinum = Number(cci); cciround = ccinum.toFixed(2);
  var mfinum = Number(mfi); mfiround = mfinum.toFixed(2);

  console.log("Date: " + day + "\n \t ClosePrice: " + candleclose + "\n \t dema: " + demaround + "\t sma: " + smaround + "\n \t cci: " + cciround + "\t mfi: " + mfiround)

  // Determine here under which circumstanses you want to go long
  if (dema > sma && mfi > mfilimit && cci > ccilimit) {
    this.advice('long')
  }
  // If the circumstanses do not meet, go short (do nothing...) 
  else {
    this.advice('short')
  }
}

module.exports = strat;