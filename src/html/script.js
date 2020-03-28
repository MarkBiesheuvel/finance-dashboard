(function(){

  const ticker = 'AMZN'
  const width = 1110
  const height = 500
  const margin = {
      top: 20,
      right: 50,
      bottom: 80,
      left: 50
  }

  const main = d3.select("#main")

  const svg = main.append("svg")
    .attr("width", width)
    .attr("height", height)

  const area = svg.append("g")
    .attr("stroke-linecap", "round")
    .attr("stroke", "black")

  d3.json(`stock/${ticker}`).catch(error => {
    console.error(error)
  }).then(data => {

    const xScale = d3.scaleBand()
      .domain(data.map(row => row.Date))
      .range([margin.left, width - margin.right])
      .padding(0.667)

    const yScale = d3.scaleLinear()
      .domain([d3.min(data, row => row.Low), d3.max(data, row => row.High)])
      .rangeRound([height - margin.bottom, margin.top])

    const xAxis = d3.axisBottom()
      .scale(xScale)
      .tickValues(xScale.domain().filter((row, i) => !(i%7)))
      .tickSizeOuter(0)

    const yAxis = d3.axisLeft()
      .scale(yScale)
      .ticks(6)
      .tickSizeOuter(0)

    svg.append("g")
      .attr("transform", `translate(0,${height - margin.bottom})`)
      .call(xAxis)

    svg.append("g")
      .attr("transform", `translate(${margin.left},0)`)
      .call(yAxis)

    const candles = area.selectAll("g")
      .data(data)
      .join("g")
      .attr("transform", row => `translate(${xScale(row.Date)},0)`)

    candles.append("line")
      .attr("y1", row => yScale(row.Low))
      .attr("y2", row => yScale(row.High))

    candles.append("line")
      .attr("y1", row => yScale(row.Open))
      .attr("y2", row => yScale(row.Close))
      .attr("stroke-width", xScale.bandwidth())
      .attr("stroke", row => row.Open > row.Close ? d3.schemeSet1[0] : d3.schemeSet1[2]);
  })
}())
