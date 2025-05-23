<script>
  import { onMount } from 'svelte';
  import Chart from '../../lib/Chart.svelte';
  import LineChart from '../../lib/LineChart.svelte';
  import BarChart from '../../lib/BarChart.svelte';
  import { base } from '$app/paths';
  import * as d3 from 'd3';
  let selectedTitle = ''; 

  // default mínimo/máximo
  let start = '2017-01-01';
  let end   = '2021-12-20';
  let title = '';
  let artist = '';
  let region = '';
  let rank = '';
  let limit = 10;
  let limitNew = 10;
  let chartLimit = 10;
  let datajson = [];
  let datagraph = []; 
  let loading = false;
  let currentTrack = '';

  const regions = [
    'Brazil', 'United States', 'Peru'
  ];

  async function getCSV() {
    if (!limitNew || limitNew < 1) limitNew = 1;
    if (limitNew > 50) limitNew = 50;
    loading = true;

    let filePath = `${base}/dados_global.json`; // padrão global
    if (region === 'Brazil') filePath = `${base}/dados_brazil.json`;
    else if (region === 'Peru') filePath = `${base}/dados_peru.json`;
    else if (region === 'United States') filePath = `${base}/dados_united_states.json`;

    const jsonData = await d3.json(filePath);

    const filteredData = jsonData.filter(d => {
      let valid = true;
      const date = new Date(d.date);

      // datas
      valid = valid
        && (!start || date >= new Date(start))
        && (!end   || date <= new Date(end));

      // prefixo
      if (title)  valid = valid && d.title.toLowerCase().startsWith(title.toLowerCase());
      if (artist) valid = valid && d.artist.toLowerCase().startsWith(artist.toLowerCase());

      // rank intervalo
      if (rank) {
        const [minR, maxR] = rank.split('-').map(Number);
        if (!isNaN(minR)) valid = valid && Number(d.rank) >= minR;
        if (!isNaN(maxR)) valid = valid && Number(d.rank) <= maxR;
      }

      return valid;
    });

    datajson = filteredData;

    const allSongs = Array.from(
      d3.rollup(
        filteredData,
        v => ({
          total_streams: d3.sum(v, d => +d.streams),
          trackId: v[0].url,
          artist: v[0].artist
        }),
        d => d.title
      ),
      ([title, { total_streams, trackId, artist }]) => ({
        title,
        total_streams,
        trackId,
        artist
      })
    );

    // Ordena e pega as top 50
    const top20Songs = allSongs
      .sort((a, b) => b.total_streams - a.total_streams)
      .slice(0, 20);

    // Pronto para qualquer gráfico (barras, treemap...)
    datagraph = top20Songs;

    loading = false;
  }

  // dispara o filtro só ao clicar
  function applyFilters() {
    getCSV();
  }

  function play(trackId) {
  if (trackId) {
    const trackUrl = `https://open.spotify.com/embed/track/${trackId.split('/').pop()}`;
    currentTrack = trackUrl;
  } else {
    console.error('Track ID inválido:', trackId);
  }
} 

  onMount(getCSV);

  let trendData = [];

  function showTrend({ title, artist }) {
    selectedTitle = title;  // ← atualiza o título
    const filtered = datajson
      .filter(d => d.title === title && d.artist === artist)
      .map(d => ({
        date: new Date(d.date),
        streams: +d.streams,
        rank: d.rank
      }))
      .sort((a, b) => a.date - b.date);
    trendData = filtered;
  }
</script>

<svelte:head>
  <title>Spotify Trends</title>
</svelte:head>

<h1>Treemap Chart</h1>

<div class="explanation">
  <p>Este treemap soma as streams de cada música que entrou no Top 200 do Spotify entre
     <strong>2017-01-01</strong> e <strong>2021-12-20</strong>. Sem filtro de região, os dados são globais;
     com filtro, considera só as streams no Top 200 daquele país. Clicando em alguma das músicas você pode não só escutá-las, 
     mas também poder observar o número de streams (e posição no top 200) que essa música teve durante o período
     de tempo definido!</p>
  <p><strong>Filtros:</strong><br>
     • <strong>Datas</strong>: Valores entre 2017-01-01 e 2021-12-20.<br>
     • <strong>Música / Artista</strong>: Busca pelo começo do nome.<br>
     • <strong>País</strong>: Playlist Top 200 do país escolhido.<br>
     • <strong>Rank</strong>: Intervalo de posição (soma só as streams de músicas desse intervalo!).<br>
     • <strong>Qtd. Músicas</strong>: Quantas folhas aparecem no treemap.</p>
</div>

<div class="filters">
  <div class="filter-item">
    <label for="filtro1">Data inicial</label>
    <input
      id="filtro1"
      type="date"
      bind:value={start}
      min="2017-01-01"
      max="2021-12-20"
      title="Entre 2017-01-01 e 2021-12-20" />
  </div>

  <div class="filter-item">
    <label for="filtro2">Data final</label>
    <input
      id="filtro2"
      type="date"
      bind:value={end}
      min="2017-01-01"
      max="2021-12-20"
      title="Entre 2017-01-01 e 2021-12-20" />
  </div>

  <div class="filter-item">
    <label for="filtro3">Música</label>
    <input
      id="filtro3"
      placeholder="Começo do título"
      bind:value={title}
      title="Busca pelo início do nome da música" />
  </div>

  <div class="filter-item">
    <label for="filtro4">Artista</label>
    <input
      id="filtro4"
      placeholder="Começo do nome"
      bind:value={artist}
      title="Busca pelo início do nome do artista" />
  </div>

  <div class="filter-item">
    <label for="filtro5">País</label>
    <select
      id = "filtro5"
      bind:value={region}
      title="Escolha o país (Global = nada filtrado)">
      <option value="">Global</option>
      {#each regions as r}
        <option value={r}>{r}</option>
      {/each}
    </select>
  </div>

  <div class="filter-item">
    <label for="filtro6">Rank (ex: 1-10)</label>
    <input
      id="filtro6"
      placeholder="1-200"
      bind:value={rank}
      title="Intervalo de posições p.ex. 1-10" />
  </div>

  <div class="filter-item">
    <label for="filtro7">Qtd. Músicas</label>
    <input
      id="filtro7"
      type="number"
      min="1"
      max="20"
      placeholder="Qtd. Músicas"
      bind:value={chartLimit}
      title="Máximo de folhas no treemap (1–50)" />
  </div>

  <div class="filter-item">
    <button on:click={applyFilters}>🔍 Aplicar filtros</button>
  </div>
</div>

{#if loading}
  <p>Carregando…</p>
{:else}
  <div class="chart-container">
    <h2>Top Músicas por Streams</h2>
    <Chart
      data={datagraph}
      on:playtrack={(e) => play(e.detail)}
      on:showtrend={(e) => showTrend(e.detail)}
      {chartLimit}
    />
  </div>
  <!-- <div>
    <BarChart
      data={datagraph} {chartLimit}/>
  </div> -->
{/if}

{#if currentTrack}
  <iframe
    title="Player de música do Spotify"
    src={currentTrack}
    width="300" height="80"
    frameborder="0" allowtransparency="true"
    allow="encrypted-media"
    style="position: fixed; bottom: 10px; left: 10px;">
  </iframe>
{/if}

{#if trendData.length}
  <h3 class="text-lg font-semibold mt-6">
    Evolução de streams de “{selectedTitle}”: 
    {trendData[0].date.toLocaleDateString()} → {trendData.at(-1).date.toLocaleDateString()}
  </h3>
  <LineChart data={trendData} />
{/if}


<style>
  .filters {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 1rem;
    align-items: center;
    flex-wrap: wrap;
  }

  .filters input:focus {
    background-color: #2a2a2a;
  }

  .filters select:focus {
    background-color: #2a2a2a;
  }

  .filters input {
    flex: 1;
    padding: 1rem 1rem;
    background-color: #121212;
    color: white;
    border: none;
    border-radius: 500px;
    font-size: 14px;
    outline: none;
    min-width: 200px;
    box-shadow: inset 0 0 0 1px #535353;
  }

  .filters select {
    flex: 1;
    padding: 1rem 1rem;
    background-color: #121212;
    color: white;
    border: none;
    border-radius: 500px;
    font-size: 14px;
    outline: none;
    min-width: 230px;
    box-shadow: inset 0 0 0 1px #535353;
  }

  .filters input::placeholder {
    color: #b3b3b3;
  }

  .filters select::placeholder {
    color: #b3b3b3;
  }

  .filter-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .filter-item label {
    font-size: 0.75rem;
    color: #b3b3b3;
    margin-bottom: 4px;
  }

  .filter-item button {
    padding: 0.75rem 1.5rem;
    margin-top: 24px;
    background: #1ed760;
    color: #121212;
    border: none;
    border-radius: 9999px;
    min-width: 230px;
    font-weight: bold;
    cursor: pointer;
  }

  .filter-item button:hover {
    opacity: 0.9;
  }

  .explanation {
    scrollbar-color: hsla(0,0%,100%,.3) transparent;
    --fallback-fonts: Helvetica Neue,helvetica,arial,Hiragino Kaku Gothic ProN,Meiryo,MS Gothic;
    --content-spacing: 16px;
    --background-base: #121212;
    --text-base: #fff;
    --encore-text-size-smaller: 1.2rem;
    cursor: default;
    user-select: none;
    box-sizing: border-box;
    font-weight: 400;
    margin-bottom: 1rem;
  }

  /*
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
  */

  .chart-container {
    margin-bottom: 2rem;
    padding: 1rem;
    border: 1px solid #eee;
    border-radius: 8px;
  }
</style>
