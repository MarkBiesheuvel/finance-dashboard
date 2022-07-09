/* global d3 */
(() => {
  const protocol = 'https'
  const domain = 'finance.demo.training'

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
      d3.json(`${protocol}://${domain}/stock/${ticker}?start=${start}&end=${end}`)
        .then(data => {
          data.forEach((row) => {
            row.Low = parseFloat(row.Low)
            row.Open = parseFloat(row.Open)
            row.Close = parseFloat(row.Close)
            row.High = parseFloat(row.High)
          })
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

  class Form {

    constructor (main) {
      this.start = main.select('#start-date')
      this.end =  main.select('#end-date')
      this.buttonGroup = main.select('#button-group')
    }

    init ()  {
      d3.json(`${protocol}://${domain}/stock/`)
        .then(stocks => {
          this.createButtons(stocks)
          this.firstLoad()
          this.bindEvents()
        })
        .catch(console.error)
    }

    createButtons(stocks) {
      this.buttons = this.buttonGroup.selectAll('button')
        .data(stocks, stock => stock.Ticker)
        .join(
          enter => enter
            .append('button')
            .attr('class', 'btn btn-default btn-dark')
            .attr('title', stock => stock.Name)
            .text(stock => stock.Ticker)
        )
    }

    firstLoad() {
      const activeButton = this.buttons.filter(":first-child")
      activeButton.classed('active', true)

      this.activeTicker = activeButton.text()
      this.selectedStartDate = this.start.property('value')
      this.selectedEndDate = this.end.property('value')

      this.reload(data => {
        // Set the date fields after fetching the initial series
        this.start.property('value', data[0]['Date'])
        this.end.property('value', data[data.length - 1]['Date'])
      })
    }

    bindEvents() {
      this.start.on('change', () => {
        this.selectedStartDate = this.start.property('value')
        this.reload()
      })

      this.end.on('change', () => {
        this.selectedEndDate = this.end.property('value')
        this.reload()
      })

      this.buttons.on('click', (event) => {
        const activeButton = d3.select(event.target)

        this.buttons.classed('active', false)
        activeButton.classed('active', true)

        this.activeTicker = activeButton.text()
        this.reload()
      })
    }

    reload(callback) {
      chart.load(
        this.activeTicker,
        this.selectedStartDate,
        this.selectedEndDate,
        callback
      )
    }
  }

  const main = d3.select('#main')

  const chart = new Chart(main)
  const form = new Form(main)

  form.init()
})()
