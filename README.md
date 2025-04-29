# Spotify Trends 🎧📊

Este projeto faz parte da Tarefa 4 da disciplina de Visualização de Dados (FGV, 2025), onde desenvolvemos uma visualização interativa baseada nos dados de streaming do Spotify para entender as tendências musicais globais e no Brasil.

---

## Integrantes

- Gustavo Bianchi 

- João Machado 

- Vinícius Nascimento 

---

## 🎯 Objetivo

Nosso objetivo é permitir que o usuário explore facilmente as músicas mais ouvidas por região, período, artista e ranking, promovendo insights sobre popularidade musical e tendências culturais globais.

---

## 🧩 Justificativa das Decisões de Design

Tomamos diversas decisões de design para tornar a visualização clara, acessível e visualmente atraente:

### Codificações Visuais:
- **Cores:** Utilizamos um tema escuro (modo *Dark*) para combinar com a identidade do Spotify e facilitar a leitura prolongada.
- **Cartões com capa do álbum:** Tornam a navegação mais visual e engajante do que listas ou tabelas.
- **Textos destacados:** Nome do artista, música e número de streams em verde para reforçar o sucesso da música.

### Interações:
- Filtros por **data**, **região**, **rank** e **artista**, permitindo que o usuário explore os dados por diferentes dimensões.
- Link lateral com navegação simples entre páginas ("Home", "Global", "Brasil", "Github").

### Técnicas Consideradas:
- Inicialmente exploramos gráficos de linha e barras (para evolução de streams), mas percebemos que, para o escopo desta tarefa, uma visualização por cartões com filtros seria mais direta e acessível ao público geral.
- Por fim, escolhemos treemap pois seria mais esteticamente "bonito" e interativo, como de modo a clicar nas capas para ouvirmos a música.
---

## 🛠️ Processo de Desenvolvimento

### Tempo Estimado:
- **Total estimado:** Aproximadamente 24 horas (8 horas por membro)
- **Tarefas que levaram mais tempo:**
  - Ajustes de layout e responsividade.
  - Implementação de filtros funcionais e compatibilidade com múltiplos critérios.
  - Implementação do treemap em D3.

---

## 📦 Fontes e Inspirações

- **Fonte dos dados:** [Kaggle - Spotify Charts](https://www.kaggle.com/datasets/dhruvildave/spotify-charts)
- **Inspiração visual:** Interface do próprio Spotify Web 

---

## 🤖 Uso de GPT / IA

Utilizamos o ChatGPT para:
- Revisar conceitos de codificações visuais e boas práticas de design de interação.
- Refatorar pequenos trechos de código Svelte para manter legibilidade.
- Nos ajudar a interpretar erros de codificação no caminho.

Todas as respostas foram revisadas e adaptadas para garantir consistência e autenticidade.
