/* global d3 */
(function () {
  class Chart {
    duration = 600

    width = 1140

    height = 500

    margin = {
        top: 5,
        right: 50,
        bottom: 30,
        left: 50
    }

    protocol = 'https'

    domain = 'finance.demo.training'

    first = true

    constructor (main) {
      this.svg = main.append('svg')
        .attr('class', 'mx-n3 my-5')
        .attr('width', this.width)
        .attr('height', this.height)

      this.area = this.svg.append('g')
        .attr('stroke-linecap', 'round')
        .attr('stroke', 'black')

      // Avoid binding issues
      this.setAttrStick = this.setAttrStick.bind(this)
      this.setAttrCandle = this.setAttrCandle.bind(this)
    }

    load (ticker, start, end, callback) {
      d3.json(`${this.protocol}://${this.domain}/stock/${ticker}?start=${start}&end=${end}`)
        .then(data => {
          if (callback) {
            callback(data)
          }
          this.update(data)
          this.draw(data)
        })
        .catch(console.error)
    }

    update (data) {
      this.xScale = d3.scaleBand()
        .domain(data.map(row => row.Date))
        .range([this.margin.left, this.width - this.margin.right])
        .padding(0.667)

      this.yScale = d3.scaleLinear()
        .domain([d3.min(data, row => row.Low), d3.max(data, row => row.High)])
        .rangeRound([this.height - this.margin.bottom, this.margin.top])

      this.xAxis = d3.axisBottom()
        .scale(this.xScale)
        .tickValues(this.xScale.domain().filter((row, i) => i % 7 === 0))
        .tickSizeOuter(0)

      this.yAxis = d3.axisLeft()
        .scale(this.yScale)
        .ticks(6)
        .tickSizeOuter(0)
    }

    draw (data) {
      const t = this.svg
        .transition()
        .duration(this.duration)

      if (this.first) {
        this.first = false

        this.domXAxis = this.svg.append('g')
          .attr('transform', `translate(0,${this.height - this.margin.bottom})`)
          .call(this.xAxis)

        this.domYAxis = this.svg.append('g')
          .attr('transform', `translate(${this.margin.left},0)`)
          .call(this.yAxis)
      } else {
        this.domXAxis
          .transition(t)
          .call(this.xAxis)

        this.domYAxis
          .transition(t)
          .call(this.yAxis)
      }

      this.area.selectAll('line.stick')
        .data(data, row => row.Date)
        .join(
          enter => enter
            .append('line')
            .attr('class', 'stick')
            .call(this.setAttrStick),
          update => update
            .transition(t)
            .call(this.setAttrStick),
          exit => exit
            .remove()
        )

      this.area.selectAll('line.candle')
        .data(data, row => row.Date)
        .join(
          enter => enter
            .append('line')
            .attr('class', 'candle')
            .call(this.setAttrCandle),
          update => update
            .transition(t)
            .call(this.setAttrCandle),
          exit => exit
            .remove()
        )
    }

    setAttrStick (selection) {
      selection
        .attr('transform', row => `translate(${this.xScale(row.Date)},0)`)
        .attr('y1', row => this.yScale(row.Low))
        .attr('y2', row => this.yScale(row.High))
    }

    setAttrCandle (selection) {
      selection
        .attr('transform', row => `translate(${this.xScale(row.Date)},0)`)
        .attr('stroke-width', this.xScale.bandwidth())
        .attr('stroke', row => row.Open > row.Close ? d3.schemeSet1[0] : d3.schemeSet1[2])
        .attr('y1', row => this.yScale(row.Open))
        .attr('y2', row => this.yScale(row.Close))
    }
  }

  const main = d3.select('#main')
  const start = main.select('#start-date')
  const end = main.select('#end-date')
  const buttons = main.selectAll('button')
  const chart = new Chart(main)

  const load = (callback) => {
    const activeTicker = buttons.filter('.active').property('value')
    const selectedStartDate = start.property('value')
    const selectedEndDate = end.property('value')
    chart.load(
      activeTicker,
      selectedStartDate,
      selectedEndDate,
      callback
    )
  }

  buttons.on('click', () => {
    buttons.classed('active', false)
    d3.select(d3.event.toElement).classed('active', true)
    load()
  })

  start.on('change', () => {
    load()
  })

  end.on('change', () => {
    load()
  })

  load(data => {
    start.property('value', data[0]['Date'])
    end.property('value', data[data.length - 1]['Date'])
  })
}())
