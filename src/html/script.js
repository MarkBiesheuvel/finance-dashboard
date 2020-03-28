(function(){

  const url = 'stock/AMZN' // Even though CORS is set to allow all oriing, it's not working
  const width = 1110
  const height = 500
  const margin = {
      top: 20,
      right: 50,
      bottom: 80,
      left: 50
  }

  d3.json(url).catch(error => {
    console.error(error)
  }).then(data => {

    data.forEach(row => {
      row.Date = Date.parse(row.Date)
    })

    const main = d3.select("#main")

    const svg = main.append("svg")
      .attr("width", width)
      .attr("height", height)

    const xScale = d3.scaleUtc()
      .domain(d3.extent(data, d => d.Date))
      .range([margin.left, width - margin.right])

    const yScale = d3.scaleLinear()
      .domain(d3.extent(data, d => d.Close))
      .rangeRound([height - margin.bottom, margin.top])

    const xAxis = d3.axisBottom()
      .scale(xScale)
      .ticks(10)
      .tickSizeOuter(0)

    const yAxis = d3.axisLeft()
      .scale(yScale)
      .ticks(6)
      .tickSizeOuter(0)

    const line = d3.line()
      .curve(d3.curveBasis)
      .x(d => xScale(d.Date))
      .y(d => yScale(d.Close))

    svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(xAxis)

    svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(yAxis)

    svg.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("stroke-width", 1)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", line)
  })
}())
