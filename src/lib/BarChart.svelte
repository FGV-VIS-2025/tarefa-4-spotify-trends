<script>
    import { onMount, createEventDispatcher } from 'svelte';
    import * as d3 from 'd3';
  
    export let data = []; // top 50
    export let chartLimit = 10; // número de barras visíveis
  
    const width = 1000;
    const height = 600;
    const margin = { top: 40, right: 20, bottom: 80, left: 100 };
  
    const dispatch = createEventDispatcher();
  
    let svgEl;
  
    $: if (data.length > 0) {
      const topSongs = data.slice(0, chartLimit);
  
      const x = d3.scaleLinear()
        .domain([0, d3.max(topSongs, d => d.total_streams)])
        .range([0, width - margin.left - margin.right]);
  
      const y = d3.scaleBand()
        .domain(topSongs.map(d => d.title))
        .range([0, height - margin.top - margin.bottom])
        .padding(0.1);
  
      const svg = d3.select(svgEl);
      svg.selectAll('*').remove();
  
      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);
  
      g.append('g')
        .call(d3.axisLeft(y).tickSize(0))
        .selectAll('text')
        .style('font-size', '12px')
        .style('fill', '#fff');
  
      g.append('g')
        .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format("~s")))
        .selectAll('text')
        .style('font-size', '12px')
        .style('fill', '#fff');
  
      g.selectAll('.bar')
        .data(topSongs)
        .enter()
        .append('rect')
        .attr('class', 'bar')
        .attr('y', d => y(d.title))
        .attr('width', d => x(d.total_streams))
        .attr('height', y.bandwidth())
        .attr('fill', '#1DB954')
        .style('cursor', 'pointer')
        .on('click', d => {
          dispatch('playtrack', d.trackId);
          dispatch('showtrend', { title: d.title, artist: d.artist });
        });
    }
</script>
  
<svg bind:this={svgEl} width={width} height={height} />
  