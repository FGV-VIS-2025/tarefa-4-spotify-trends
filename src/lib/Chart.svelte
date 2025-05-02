<script>
  import { createEventDispatcher, onMount } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];
  export let limit = 10; // Número máximo de folhas (nós) a serem exibidas no Treemap

  let nodes = [];
  let images = {};
  let hoveredId = null;
  let selectedId = null;

  const width = 1000;
  const height = 600;

  const dispatch = createEventDispatcher();

  function play(trackId) {
    const trackUrl = `https://open.spotify.com/embed/track/${trackId}`;
    dispatch('playtrack', trackUrl);
  }

  function select(trackId) {
    selectedId = trackId;
    play(trackId);

    const node = nodes.find(n => n.data.trackId === trackId);
    if (node) {
      dispatch('showtrend', {
        title: node.data.title,
        artist: node.parent.data.name 
      });
    }
  }

  // Transformando os dados em formato adequado para o d3.treemap()
  $: if (data.length > 0) {
    //console.log('Dados recebidos:', data);

    const artistData = [];

    data.forEach(artist => {
      const artistName = artist.name;
      const songData = {};

      artist.children.forEach(song => {
        const songTitle = song.title;
        if (songData[songTitle]) {
          songData[songTitle].total_streams += song.total_streams;
        } else {
          songData[songTitle] = {
            title: songTitle,
            total_streams: song.total_streams,
            trackId: song.trackId
          };
        }
      });

      artistData.push({
        name: artistName,
        children: Object.values(songData)
      });
    });

    const treeData = {
      children: artistData.map(artist => ({
        name: artist.name,
        children: artist.children.map(song => ({
          title: song.title,
          total_streams: song.total_streams,
          trackId: song.trackId
        }))
      }))
    };

    let allSongs = [];
    treeData.children.forEach(artist => {
      allSongs = allSongs.concat(artist.children); 
    });

    allSongs.sort((a, b) => b.total_streams - a.total_streams);
    const topSongs = allSongs.slice(0, limit);

    const topTreeData = {
      children: treeData.children.map(artist => {
        const topSongsForArtist = artist.children.filter(song => {
          return topSongs.some(topSong => topSong.trackId === song.trackId);
        });

        return {
          name: artist.name,
          children: topSongsForArtist
        };
      }).filter(artist => artist.children.length > 0)
    };

    // Aplica o layout de Treemap para calcular as posições
    const root = d3.hierarchy(topTreeData)
      .sum(d => d.total_streams) 
      .sort((a, b) => b.total_streams - a.total_streams); 

    d3.treemap()
      .size([width, height])
      .padding(1)
      (root);

    nodes = root.leaves().slice(0, limit); 
  }

  let tooltipEl;

  function showTooltip(event, node) {
    tooltipEl.style.left = `${event.pageX + 12}px`;
    tooltipEl.style.top = `${event.pageY + 12}px`;
    tooltipEl.style.display = 'block';
    tooltipEl.innerHTML = `
      <strong>${node.data.title}</strong><br>
      Artista: ${node.parent.data.name}<br>
      Streams: ${node.data.total_streams.toLocaleString()}<br>
      <em>Clique para ouvir</em>
    `;
  }

  // Esconde o tooltip
  function hideTooltip() {
    tooltipEl.style.display = 'none';
  }
</script>

<svg width={width} height={height} xmlns="http://www.w3.org/2000/svg">
  <defs>
    {#each nodes as node (node.data.trackId)}
      <clipPath id={`clip-${node.data.trackId}`}>
        <rect
          x="0"
          y="0"
          width={node.x1 - node.x0}
          height={node.y1 - node.y0}
        />
      </clipPath>
    {/each}
  </defs>

  <!-- quadrados das músicas -->
  {#each nodes as node (node.data.trackId)}
    <g 
      transform={`translate(${node.x0},${node.y0})`} 
      on:mouseover={(e) => {
        hoveredId = node.data.trackId;
        showTooltip(e, node);
      }}
      on:mousemove={(e) => showTooltip(e, node)}
      on:mouseout={() => {
        hoveredId = null;
        hideTooltip();
      }}
      on:click={() => select(node.data.trackId)}
      style="cursor: pointer;"
      clip-path={`url(#clip-${node.data.trackId})`}
    >
      <rect
        width={node.x1 - node.x0}
        height={node.y1 - node.y0}
        fill="#222"
        stroke={(hoveredId === node.data.trackId || selectedId === node.data.trackId) ? "#1DB954" : "#aaa"}
        stroke-width={(hoveredId === node.data.trackId || selectedId === node.data.trackId) ? 3 : 1}
        style="transition: all 0.2s ease;"
      />

      {#if node.data.thumbnail}
        <image
          href={node.data.thumbnail}
          width={node.x1 - node.x0}
          height={node.y1 - node.y0}
          preserveAspectRatio="xMidYMid slice"
        />
      {/if}

      <rect
        width={node.x1 - node.x0}
        height={node.y1 - node.y0}
        fill={(hoveredId === node.data.trackId || selectedId === node.data.trackId) ? "rgba(0,0,0,0.2)" : "rgba(0,0,0,0.7)"}
        style="transition: all 0.2s ease;"
      />

      {#if (node.x1 - node.x0) > 60 && (node.y1 - node.y0) > 40}
        <text 
          x={(node.x1 - node.x0) / 2}
          y={(node.y1 - node.y0) / 2 - 5}
          fill="white"
          font-size="10"
          text-anchor="middle"
          font-weight="bold"
          style="text-shadow: 0 1px 2px rgba(0,0,0,0.8);"
        >
          {node.data.title}
        </text>

        <text 
          x={(node.x1 - node.x0) / 2}
          y={(node.y1 - node.y0) / 2 + 10}
          fill="#1DB954"
          font-size="9"
          text-anchor="middle"
          style="text-shadow: 0 1px 2px rgba(0,0,0,0.8);"
        >
          {node.data.total_streams.toLocaleString()} streams
        </text>
      {/if}
    </g>
  {/each}
  
  {#each Array.from(new Set(nodes.map(n => n.parent))) as parent (parent.data.name)}
    {#if parent}
      <g transform={`translate(${parent.x0},${parent.y0})`}>
        <rect
          width={parent.x1 - parent.x0}
          height={parent.y1 - parent.y0}
          fill="none"
          stroke="#1DB954"
          stroke-width="3"
          style="transition: all 0.3s ease;"
        />
        
        {#if (parent.x1 - parent.x0) > 100 && (parent.y1 - parent.y0) > 40}
          <text
            x={(parent.x1 - parent.x0) / 2}
            y="12" 
            fill="#1DB954"
            font-size="10"
            font-weight="bold"
            text-anchor="middle"
            style="text-shadow: 0 1px 2px black;"
          >
            {parent.data.name}
          </text>
        {/if}
      </g>
    {/if}
  {/each}
</svg>

<div bind:this={tooltipEl} class="tooltip" />

<style>
  .tooltip {
    position: absolute;
    background: #121212;
    color: white;
    border: 1px solid #1DB954;
    border-radius: 4px;
    padding: 8px 10px;
    font-size: 12px;
    pointer-events: none;
    white-space: nowrap;
    display: none;
    z-index: 10;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5);
  }
</style>