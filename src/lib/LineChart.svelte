<script>
  import { afterUpdate } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];

  let svg;

  const margin = { top: 20, right: 30, bottom: 50, left: 50 };
  const width = 1000;
  const height = 400;

  afterUpdate(() => {
    if (!data || data.length === 0) return;

    // Converte strings para Date/Number
    const parsed = data.map(d => ({
      ...d,
      date: new Date(d.date),
      streams: +d.streams
    }));

    const x = d3.scaleTime()
      .domain(d3.extent(parsed, d => d.date))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(parsed, d => d.streams)]).nice()
      .range([height, 0]);

    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.streams));

    // Limpa SVG antigo
    d3.select(svg).selectAll("*").remove();

    const g = d3.select(svg)
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .style('width', '100%')
      .style('height', 'auto')
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%b %Y')))
      .append('text') 
      .attr('x', width / 2)
      .attr('y', margin.bottom - 15)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .text('Data');

    g.append('g')
      .call(d3.axisLeft(y).tickFormat(d3.format('~s')))
      .append('text') 
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -40)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .text('Streams');

    g.append('path')
      .datum(parsed)
      .attr('fill', 'none')
      .attr('stroke', '#1db954')
      .attr('stroke-width', 2)
      .attr('d', line);

    // Tooltip
    const focus = g.append('g').style('display', 'none');

    focus.append('circle')
      .attr('r', 4.5)
      .attr('fill', 'white')
      .attr('stroke', '#1db954');

    focus.append('rect')
      .attr('width', 160)
      .attr('height', 50)
      .attr('x', 10)
      .attr('y', -22)
      .attr('rx', 4)
      .attr('ry', 4)
      .attr('fill', 'black')
      .attr('opacity', 0.8);

    focus.append('text')
      .attr('x', 18)
      .attr('y', -2)
      .attr('fill', 'white')
      .attr('id', 'tooltip-date');

    focus.append('text')
      .attr('x', 18)
      .attr('y', 16)
      .attr('fill', 'white')
      .attr('id', 'tooltip-streams');

    g.append('rect')
      .attr('class', 'overlay')
      .attr('width', width)
      .attr('height', height)
      .attr('fill', 'none')
      .attr('pointer-events', 'all')
      .on('mouseover', () => focus.style('display', null))
      .on('mouseout', () => focus.style('display', 'none'))
      .on('mousemove', function (event) {
        const bisect = d3.bisector(d => d.date).left;
        const mouseX = d3.pointer(event, this)[0];
        const x0 = x.invert(mouseX);
        const i = bisect(parsed, x0, 1);
        const d0 = parsed[i - 1];
        const d1 = parsed[i];
        const d = x0 - d0.date > d1.date - x0 ? d1 : d0;

        focus.attr('transform', `translate(${x(d.date)},${y(d.streams)})`);
        focus.select('#tooltip-date').text(d3.timeFormat('%d/%m/%Y')(d.date));
        focus.select('#tooltip-streams').text(`${d.streams.toLocaleString()} streams`);
      });
  });
</script>

<style>
  .tooltip text {
    font-size: 12px;
    pointer-events: none;
  }
</style>

<svg bind:this={svg}></svg>
