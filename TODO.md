# TODO

## App

* line interpolation between points
    * Add a general settings to control how two points are joined.
    * Actual implementation it is a smooth curve. Let's add: straight connection and step (hotizontal then vertical)
* line regexp
    * Now we just split the line and call from col1 to colN
    * Add an extra option to use a regex match.
    * When regexp unmatch, just do a silence reject (treat as a message)
* filter
    * Add filters to be applied in the dataset, like moving avg, lp, hp, bp, d/dt, int and other nice filters.
    * possibility of a custom filter expression
* regression
    * add a regression applied to the data window, per curve
* y axix
    * add custom monolog, loglog
* calculated y
   * add a expression to be calculated using cols
   * the calculated y can be a normal curve to plot, to be used as a "curve operation"
* XY mode
   * for 2 perioric columns, it is easy to just add then as col1 and col2. It will just work.
   * analyse this case to see if see a separated window/param selections
* Osc functions
   * add some osc functions:
      * trigger, one shot record (record one window) and so on.
* Curve calculations
   * curve calculations and statistics like: min, max, freq, avg, stdev

## Serial

* Test software serial on OSes
    * Mac: Add code to simulate a serial port.
* Test hardware serial on OSes

## Project

* Convert this TODO into separated gh issues
* Convert the project to use venv
* Convert project to a poetry project, so the user can install using: pip3 install git+https://github.com/...
  
