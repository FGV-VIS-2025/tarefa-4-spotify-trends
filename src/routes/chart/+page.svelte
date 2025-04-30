<script>
  import { onMount } from 'svelte';
  import Chart from '../../lib/Chart.svelte';
  import * as d3 from 'd3';

  let start = '';
  let end = '';
  let title = '';
  let artist = '';
  let region = '';
  let rank = '';
  let limit = 10;
  let datajson = [];
  let datagraph = []; 
  let loading = false;
  let currentTrack = '';
  let controller;

  function formatDate(str) {
    return str.split('T')[0];
  }

  async function getCSV() {
    if (!limit || limit < 1) limit = 1;
    if (limit > 50) limit = 50;

    loading = true;
    
    // Carregar o arquivo CSV
    const csvData = await d3.csv('/charts_global.csv');
    
    // Filtragem dos dados
    const filteredData = csvData.filter(d => {
      let valid = true;

      if (start && end) {
        valid = valid && new Date(d.date) >= new Date(start) && new Date(d.date) <= new Date(end);
      } else if (start) {
        valid = valid && new Date(d.date) >= new Date(start);
      } else if (end) {
        valid = valid && new Date(d.date) <= new Date(end);
      }

      if (title) valid = valid && d.title.toLowerCase().includes(title.toLowerCase());
      if (artist) valid = valid && d.artist.toLowerCase().includes(artist.toLowerCase());
      if (region) valid = valid && d.region.toLowerCase().includes(region.toLowerCase());
      if (rank) {
        const [minRank, maxRank] = rank.split('-').map(Number);
        valid = valid && ((minRank && d.rank >= minRank) || (maxRank && d.rank <= maxRank));
      }

      return valid;
    });


    // Atualizar dados para a tabela
    datajson = filteredData;

    // Preparar dados para o gráfico
    const graphData = d3.group(filteredData, d => d.artist);
    datagraph = Array.from(graphData, ([artist, songs]) => ({
      name: artist,
      children: songs.map(song => ({
        title: song.title,
        total_streams: +song.streams, // A soma de streams
        trackId: song.url, // Se você precisar disso para o ícone, etc.
      }))
    }));

    loading = false;
  }

  function onStart(e) { start = e.target.value; getCSV(); }
  function onEnd(e) { end = e.target.value; getCSV(); }
  function onTitle(e) { title = e.target.value; getCSV(); }
  function onArtist(e) { artist = e.target.value; getCSV(); }
  function onRegion(e) { region = e.target.value; getCSV(); }
  function onRank(e) { rank = e.target.value; getCSV(); }

  function play(id) {
    currentTrack = `https://open.spotify.com/embed/track/${id}`;
  }

  onMount(getCSV);
</script>

<svelte:head>
  <title>Charts Top</title>
</svelte:head>

<div class="filters">
  <input type="date" bind:value={start} on:input={onStart} placeholder="Data início" />
  <input type="date" bind:value={end} on:input={onEnd} placeholder="Data fim" />
  <input placeholder="Música" bind:value={title} on:input={onTitle} />
  <input placeholder="Artista" bind:value={artist} on:input={onArtist} />
  <input placeholder="Região" bind:value={region} on:input={onRegion} />
  <input placeholder="Rank (intervalo '1-50')" bind:value={rank} on:input={onRank} />
  <input placeholder="Qtd. Músicas" type="number" min="1" bind:value={limit} on:input={getCSV} />
</div>

{#if loading}
  <p>Carregando…</p>
{:else}
  <div class="chart-container">
    <h2>Top Músicas por Streams</h2>
    <Chart data={datagraph} on:playtrack={(e) => currentTrack = e.detail} {limit} />
  </div>


{/if}

{#if currentTrack}
  <iframe
    src={currentTrack}
    width="300"
    height="80"
    frameborder="0"
    allowtransparency="true"
    allow="encrypted-media"
    style="position: fixed; bottom: 10px; left: 10px;"
  ></iframe>
{/if}


<style>
.filters {
    display: flex;
    gap: 10px;
    margin-bottom: 1rem;
    align-items: center;
    flex-wrap: wrap;
  }

  .filters input {
    flex: 1;
    padding: 0.75rem 1rem;
    background-color: #121212;
    color: white;
    border: none;
    border-radius: 500px; 
    font-size: 14px;
    outline: none;
    min-width: 200px;
  }

  .filters input::placeholder {
    color: #b3b3b3; 
  }

  .filters input:focus {
    background-color: #2a2a2a;
  }

  .filters input {
    box-shadow: inset 0 0 0 1px #535353;
  }
  .grid {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }
  .card {
    width: 150px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    text-align: center;
    cursor: pointer;
    transition: .2s;
  }
  .card:hover {
    background: #f0f0f0;
  }
  .chart-container {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 8px;
  }
</style>