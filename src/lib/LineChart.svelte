<script>
  import { afterUpdate } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];

  let svg;

  const margin = { top: 20, right: 100, bottom: 50, left: 50 };
  const width = 1000;
  const height = 400;

  afterUpdate(() => {
    if (!data || data.length === 0) return;

    // Converte strings para Date/Number
    const parsed = data.map(d => ({
      ...d,
      date: new Date(d.date),
      streams: +d.streams,
      rank: +d.rank
    }));

    const x = d3.scaleTime()
      .domain(d3.extent(parsed, d => d.date))
      .range([0, width]);

    const yStreams = d3.scaleLinear()
      .domain([0, d3.max(parsed, d => d.streams)]).nice()
      .range([height, 0]);

    const yRank = d3.scaleLinear()
      .domain([1, 200]) // Eixo Y fixo de Rank entre 1 e 200
      .range([0, height]); 

    const lineStreams = d3.line()
      .x(d => x(d.date))
      .y(d => yStreams(d.streams))
      .curve(d3.curveMonotoneX); 

    const lineRank = d3.line()
      .x(d => x(d.date))
      .y(d => yRank(d.rank))
      .curve(d3.curveMonotoneX); 

    // Limpa SVG antigo
    d3.select(svg).selectAll("*").remove();

    const g = d3.select(svg)
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .style('width', '100%')
      .style('height', 'auto')
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Eixo X (Data)
    const xAxisGroup = g.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x).tickFormat(d3.timeFormat('%b %Y')))
      .append('text') 
      .attr('x', width / 2)
      .attr('y', margin.bottom - 15)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .style("font-size", "16px")
      .text('Data');

    // Eixo Y (Streams)
    g.append('g')
      .call(d3.axisLeft(yStreams).tickFormat(d3.format('~s')))
      .append('text') 
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', -40)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .style("font-size", "16px")
      .text('Streams');

    // Eixo Y (Rank)
    g.append('g')
      .attr('transform', `translate(${width}, 0)`)
      .call(d3.axisRight(yRank).tickFormat(d3.format('~s')))
      .append('text') 
      .attr('transform', 'rotate(-90)')
      .attr('x', -height / 2)
      .attr('y', 40)
      .attr('fill', 'currentColor')
      .attr('text-anchor', 'middle')
      .style("font-size", "16px")
      .text('Rank');

    // Linha para Streams
    g.append('path')
      .datum(parsed)
      .attr('fill', 'none')
      .attr('stroke', '#1db954') 
      .attr('stroke-width', 3)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-linecap', 'round')
      .attr('d', lineStreams)
      .attr('filter', 'url(#drop-shadow)');

    // Linha para Rank
    g.append('path')
      .datum(parsed)
      .attr('fill', 'none')
      .attr('stroke', '#ff6600') // Cor de linha para Rank
      .attr('stroke-width', 3)
      .attr('stroke-linejoin', 'round')
      .attr('stroke-linecap', 'round')
      .attr('d', lineRank)
      .attr('filter', 'url(#drop-shadow)'); // Adiciona sombra

    // Definindo o filtro para sombra
    g.append('defs')
      .append('filter')
      .attr('id', 'drop-shadow')
      .append('feDropShadow')
      .attr('dx', 2)
      .attr('dy', 2)
      .attr('stdDeviation', 3);

    // Tooltip
    const focus = g.append('g').style('display', 'none');

    focus.append('circle')
      .attr('r', 4.5)
      .attr('fill', 'white')
      .attr('stroke', '#1db954');

    focus.append('rect')
      .attr('width', 160)
      .attr('height', 60)
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

    focus.append('text')
      .attr('x', 18)
      .attr('y', 32)
      .attr('fill', 'white')
      .attr('id', 'tooltip-rank');

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

        const xPos = x(d.date);
        const yPos = yStreams(d.streams);
        const tooltipWidth = 160;
        const offset = 20;
        
        if (xPos + tooltipWidth + offset > width) {
            // Posiciona à esquerda do ponto
            focus.attr('transform', `translate(${xPos},${yPos})`);
            focus.select('rect').attr('x', -170);
            focus.selectAll('text').attr('x', -162);
        } else {
            // Posiciona à direita do ponto (padrão)
            focus.attr('transform', `translate(${xPos},${yPos})`);
            focus.select('rect').attr('x', 10);
            focus.selectAll('text').attr('x', 18);
        }
        
        focus.select('#tooltip-date').text(d3.timeFormat('%d/%m/%Y')(d.date));
        focus.select('#tooltip-streams').text(`${d.streams.toLocaleString()} streams`);
        focus.select('#tooltip-rank').text(`Rank: ${d.rank}`);
    });

    // Legenda
    const legend = g.append('g')
      .attr('transform', `translate(${width + 30}, 30)`);

    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 0)
      .attr('r', 6)
      .attr('fill', '#1db954');

    legend.append('text')
      .attr('x', 10)
      .attr('y', 0)
      .attr('dy', '.35em')
      .text('Streams')
      .style('font-size', '14px')
      .style('fill', 'currentColor');

    legend.append('circle')
      .attr('cx', 0)
      .attr('cy', 20)
      .attr('r', 6)
      .attr('fill', '#ff6600');

    legend.append('text')
      .attr('x', 10)
      .attr('y', 20)
      .attr('dy', '.35em')
      .text('Rank')
      .style('font-size', '14px')
      .style('fill', 'currentColor');
  });
</script>