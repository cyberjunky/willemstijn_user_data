/*
* consp@github.com
* Mar 6th 2014
* Lineair regression curve
*/
var log = require('../../core/log');

var Indicator = function(settings) {
  this.depth = settings;
  this.result = false;
  this.age = 0;
  this.history = new Array();
  this.x = new Array();
  /*
* Do not use array(depth) as it might not be implemented
*/
  for (var i = 0; i < this.depth; i++) {
      this.history.push(0.0);
      this.x.push(i);
  }

  // log.debug("Created LRC indicator with h: ", this.depth);
}

Indicator.prototype.update = function(price) {
  
  // We need sufficient history to get the right result.
  if(this.result === false || this.age < this.depth) {
    this.age++;
    this.result = price;
    // log.debug("Waiting for sufficient age: ", this.age, " out of ", this.depth);
    return this.result;
  }

  this.age++;
  // shift history
  for (var i = 0; i < (this.depth - 1); i++) {
      this.history[i] = this.history[i+1];
  }
  this.history[this.depth-1] = price;

  this.calculate(price);


  // log.debug("Checking LRC: ", this.result.toFixed(8), "\tH: ", this.age);
  return this.result;
}

/*
* Least squares linear regression fitting.
*/
function linreg(values_x, values_y) {
    var sum_x = 0;
    var sum_y = 0;
    var sum_xy = 0;
    var sum_xx = 0;
    var count = 0;

    /*
* We'll use those variables for faster read/write access.
*/
    var x = 0;
    var y = 0;
    var values_length = values_x.length;

    if (values_length != values_y.length) {
        throw new Error('The parameters values_x and values_y need to have same size!');
    }

    /*
* Nothing to do.
*/
    if (values_length === 0) {
        return [ [], [] ];
    }

    /*
* Calculate the sum for each of the parts necessary.
*/
    for (var v = 0; v < values_length; v++) {
        x = values_x[v];
        y = values_y[v];
        sum_x += x;
        sum_y += y;
        sum_xx += x*x;
        sum_xy += x*y;
        count++;
    }

    /*
* Calculate m and b for the formula:
* y = x * m + b
*/
    var m = (count*sum_xy - sum_x*sum_y) / (count*sum_xx - sum_x*sum_x);
    var b = (sum_y/count) - (m*sum_x)/count;

    return [m, b];
}


/*
* Handle calculations
*/
Indicator.prototype.calculate = function(price) {

    // get the reg
    var reg = linreg(this.x, this.history);

    // y = a * x + b
    this.result = (this.depth * reg[0]) + reg[1];
}

module.exports = Indicator;
