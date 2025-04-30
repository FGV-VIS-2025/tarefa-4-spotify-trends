<script>
  import { createEventDispatcher } from 'svelte';
  import * as d3 from 'd3';

  export let data = [];
  export let limit = 10;

  let nodes = [];
  let images = {};
  let hoveredId = null;
  let selectedId = null;

  const width = 1000;
  const height = 600;

  const dispatch = createEventDispatcher();

  async function fetchThumbnail(trackId) {
    if (!trackId) return null;
    if (images[trackId]) return images[trackId];

    try {
      const response = await fetch(`/chart?thumbnail=true&trackId=${trackId}`);
      if (response.ok) {
        const json = await response.json();
        images[trackId] = json.thumbnail;
        return json.thumbnail;
      }
    } catch (error) {
      console.error('Erro ao buscar thumbnail:', error);
    }
    return null;
  }

  function play(trackId) {
    const trackUrl = `https://open.spotify.com/embed/track/${trackId}`;
    dispatch('playtrack', trackUrl);
  }

  function select(trackId) {
    selectedId = trackId;
    play(trackId);
  }

  $: if (data.length > 0) {
    console.log('Dados recebidos:', data);

    const artistData = [];

    // Agrupar as músicas por artista e somar os streams
    data.forEach(artist => {
      const artistName = artist.name;
      const songData = {};

      // Para cada música do artista, somar os streams por título
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

      // Agrupar as músicas somadas para esse artista
      artistData.push({
        name: artistName,
        children: Object.values(songData)  // Criar o array de músicas agregadas
      });
    });

    // Agora transformamos o artistaData em uma hierarquia para o gráfico de Treemap
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

    console.log(treeData);

    // Criar a hierarquia e aplicar o treemap
    const root = d3.hierarchy(treeData)
      .sum(d => d.total_streams)  // Somar os streams para gerar o tamanho dos nós
      .sort((a, b) => b.value - a.value);  // Ordenar do maior para o menor

    d3.treemap()
      .size([width, height])
      .paddingInner(2)
      .paddingOuter(4)
      (root);

    // Processar os nós e buscar as imagens dos álbuns (por exemplo)
    //Promise.all(
      //root.leaves().map(async node => {
        //const thumbnail = await fetchThumbnail(node.data.trackId);
        //if (thumbnail) {
        //  node.data.thumbnail = thumbnail;
        //}
        //return node;
      //})
    //).then(finalNodes => {
      //nodes = finalNodes.slice(0, limit); // Limitar o número de nós a serem mostrados
    //});
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
      on:mouseover={() => hoveredId = node.data.trackId}
      on:mouseout={() => hoveredId = null}
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
          {node.data.total_streams.toLocaleString()} 
        </text>
      {/if}
    </g>
  {/each}
</svg>
