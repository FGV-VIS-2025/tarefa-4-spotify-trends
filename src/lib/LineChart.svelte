<script>
  import { onMount } from 'svelte';
  import * as d3 from 'd3';
  export let data = [];

  let svg;
  const margin = { top: 20, right: 30, bottom: 30, left: 40 };
  const width = 800 - margin.left - margin.right;
  const height = 300 - margin.top - margin.bottom;

  onMount(() => {
    if (!data.length) return;

    d3.select(svg).selectAll('*').remove(); // limpar anterior

    const svgElement = d3.select(svg)
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime()
      .domain(d3.extent(data, d => d.date))
      .range([0, width]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.streams)]).nice()
      .range([height, 0]);

    const line = d3.line()
      .x(d => x(d.date))
      .y(d => y(d.streams));

    svgElement.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x));

    svgElement.append('g')
      .call(d3.axisLeft(y));

    svgElement.append('path')
      .datum(data)
      .attr('fill', 'none')
      .attr('stroke', '#1db954')
      .attr('stroke-width', 2)
      .attr('d', line);
  });
</script>

<svg bind:this={svg}></svg>
