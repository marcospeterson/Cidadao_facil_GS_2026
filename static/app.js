'use strict';
// Cidadão Fácil GS 2026.2 — sem frameworks, sem imagens externas.
const $ = (id) => document.getElementById(id);
const ROUTES = {
  '/': ['Visão geral', 'Início', 'Início'], '/servicos': ['Explorar', 'Serviços', 'Serviços'],
  '/assistente': ['Atendimento', 'Assistente IA', 'Assistente'],
  '/guias': ['Orientações', 'Guias práticos', 'Guias'], '/simulador': ['Preparação', 'Simulador', 'Simulador'],
  '/indicadores': ['Projeto', 'Indicadores', 'Indicadores'], '/transparencia': ['Projeto', 'Transparência', 'Transparência']
};
let SERVICOS = [];
let filtroCategoria = 'Todos';
let servicoGuia = '';
let guiaAtual = null;
let chatServico = '';
let chatContexto = '';
let chatHistorico = [];
let chatOcupado = false;
let simEtapa = 1;
let simEstado = {servico:'',situacao:'',modalidade:''};
let reconhecimento = null;
let toastTimer;

function node(tag, cls='', text) {
  const el = document.createElement(tag);
  if (cls) el.className = cls;
  if (text !== undefined) el.textContent = String(text);
  return el;
}
function clear(el) { if (el) el.replaceChildren(); }
function text(id, value) { if ($(id)) $(id).textContent = value; }
function showError(id, message) { const el=$(id); if (!el) return; el.textContent=message||''; el.hidden=!message; }
function toast(message) {
  const el=$('toast'); el.textContent=message;el.hidden=false;
  if(toastTimer) clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>el.hidden=true,4200);
}
function apiUrl(url){ return '/api'+url; }
async function fetchJson(url, options) {
  const response=await fetch(url,{cache:'no-store',...(options||{})});
  let dados;
  try { dados=await response.json(); } catch { throw new Error('Resposta inválida do servidor.'); }
  if (!response.ok) throw new Error(dados.erro||`Erro HTTP ${response.status}`);
  return dados;
}
function button(label, cls, handler, type='button') {
  const e=node('button',cls,label);e.type=type;if(handler)e.addEventListener('click',handler);return e;
}
function link(label, href, cls='') {
  const e=node('a',cls,label);e.href=href;
  if(href.startsWith('/'))e.dataset.link='';
  return e;
}
function fonteValida(url) {
  try { const u=new URL(url);return u.protocol==='https:' && ['gov.br','tse.jus.br'].some(d=>u.hostname===d||u.hostname.endsWith('.'+d)); }
  catch { return false; }
}
function createSources(fontes) {
  const wrap=node('div','source-links');
  const vistos=new Set();
  for(const f of fontes||[]) {
    if(!f || !fonteValida(f.url) || vistos.has(f.url))continue;
    vistos.add(f.url);
    const a=link(f.titulo+' ↗',f.url,'source-link');a.target='_blank';a.rel='noopener noreferrer';
    wrap.append(a);
  }
  return wrap;
}
function serviceSymbol(s) {
  const dict={'Documentos':'▧','Saúde':'✚','Trabalho':'▣','Cidadania':'☆','Assistência social':'♧','Serviços digitais':'◎'};
  return dict[s.categoria]||'▦';
}
function navigate(path, replace=false) {
  const parsed=new URL(path,location.origin);
  const rota=ROUTES[parsed.pathname]?parsed.pathname:'/';
  const url=rota+parsed.search;
  if(replace)history.replaceState({},'',url);else if(location.pathname+location.search!==url)history.pushState({},'',url);
  setRoute(rota,parsed.searchParams);
  window.scrollTo({top:0,behavior:'instant'});
}
function setRoute(rota,params=new URLSearchParams()){
  for(const el of document.querySelectorAll('[data-page]'))el.hidden=el.dataset.page!==rota;
  for(const a of document.querySelectorAll('[data-route]')){
    const ativo=a.dataset.route===rota;a.classList.toggle('active',ativo);
    if(ativo)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');
  }
  text('breadcrumb',ROUTES[rota][0]); text('breadcrumb-detail',ROUTES[rota][1]);
  document.title=ROUTES[rota][2]+' | Cidadão Fácil';
  closeMenu();
  if(rota==='/guias') selectGuide(params.get('servico')||servicoGuia||(SERVICOS[0]?.id||''));
  if(rota==='/assistente' && params.has('servico')) preselectChat(params.get('servico'));
  if(rota==='/indicadores') renderMetrics();
  const heading=document.querySelector(`[data-page="${rota}"] h1`);
  if(heading){heading.setAttribute('tabindex','-1');heading.focus({preventScroll:true});}
}
function closeMenu(){ $('sidebar').classList.remove('is-open'); $('sidebar-backdrop').hidden=true;$('menu-trigger').setAttribute('aria-expanded','false'); }
function initNavigation(){
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[data-link]');
    if(!a || event.defaultPrevented || event.button!==0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey)return;
    const u=new URL(a.href,location.origin);
    if(u.origin!==location.origin)return;
    event.preventDefault(); navigate(u.pathname+u.search);
  });
  window.addEventListener('popstate',()=>setRoute(ROUTES[location.pathname]?location.pathname:'/',new URLSearchParams(location.search)));
  $('menu-trigger').addEventListener('click',()=>{
    const aberto=$('sidebar').classList.toggle('is-open'); $('sidebar-backdrop').hidden=!aberto;
    $('menu-trigger').setAttribute('aria-expanded',String(aberto));
  });
  $('sidebar-backdrop').addEventListener('click',closeMenu);
  document.addEventListener('keydown',e=>{ if(e.key==='Escape')closeMenu(); });
}

// Catálogo e atalhos.
function serviceCard(s){
  const card=node('article','service-card');
  const top=node('div','service-card-top');
  top.append(node('span','service-icon',serviceSymbol(s)),node('span','service-tag',s.categoria));
  const title=node('h3','',s.nome);const p=node('p','',s.descricao);
  const actions=node('div','service-actions');
  actions.append(link('Ver guia ↗','/guias?servico='+encodeURIComponent(s.id),'service-action-primary'),
                 link('Perguntar à IA →','/assistente?servico='+encodeURIComponent(s.id),'service-action-secondary'));
  card.append(top,title,p,actions);return card;
}
function renderHomeServices(){
  const el=$('home-services');clear(el);
  for(const s of SERVICOS.slice(0,4))el.append(serviceCard(s));
}
function renderFilters(){
  const el=$('service-filters');clear(el);
  const cats=['Todos',...new Set(SERVICOS.map(x=>x.categoria))];
  for(const c of cats){const b=button(c,'filter-chip'+(c===filtroCategoria?' selected':''),()=>{
    filtroCategoria=c;renderFilters();renderCatalog();
  });b.setAttribute('aria-pressed',String(c===filtroCategoria));el.append(b);}
}
function renderCatalog(){
  const termo=$('service-search').value.trim().toLocaleLowerCase('pt-BR').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const filtrados=SERVICOS.filter(s=>{
    const matchCat=filtroCategoria==='Todos'||s.categoria===filtroCategoria;
    const conteudo=(s.nome+' '+s.descricao+' '+s.categoria).toLocaleLowerCase('pt-BR').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
    return matchCat&&conteudo.includes(termo);
  });
  text('service-count',String(SERVICOS.length).padStart(2,'0'));
  text('service-result-count',`${filtrados.length} ${filtrados.length===1?'serviço encontrado':'serviços encontrados'}`);
  const target=$('services-catalog');clear(target);
  if(!filtrados.length){const vazio=node('div','empty-state','Não encontramos serviços com esses filtros. Tente outra palavra.');target.append(vazio);return;}
  for(const s of filtrados)target.append(serviceCard(s));
}

// Guias: progresso somente local e sem dados pessoais.
const PROGRESS_KEY='cidadao_facil_passos_v8';
function getProgress(){
  try {const dado=JSON.parse(localStorage.getItem(PROGRESS_KEY)||'{}');return dado&&typeof dado==='object'&&!Array.isArray(dado)?dado:{};}
  catch{return {};}
}
function setProgress(id,items){
  try {const all=getProgress();all[id]=items;localStorage.setItem(PROGRESS_KEY,JSON.stringify(all));}
  catch{toast('O navegador não permitiu salvar o progresso. Você pode continuar nesta sessão.');}
}
function drawGuideSelector(){
  const target=$('guide-selector');clear(target);
  for(const s of SERVICOS){
    const b=button(serviceSymbol(s)+'  '+s.nome,'guide-select'+(s.id===servicoGuia?' selected':''),()=>selectGuide(s.id));
    b.setAttribute('aria-pressed',String(s.id===servicoGuia)); target.append(b);
  }
}
async function selectGuide(id){
  if(!SERVICOS.length)return;
  if(!SERVICOS.some(s=>s.id===id))id=SERVICOS[0].id;
  servicoGuia=id;drawGuideSelector();
  if(location.pathname==='/guias')history.replaceState({},'', '/guias?servico='+encodeURIComponent(id));
  const area=$('guide-details');
  area.replaceChildren(node('div','empty-detail','Carregando guia…'));
  try {guiaAtual=await fetchJson(apiUrl('/servicos/'+encodeURIComponent(id)));if(servicoGuia!==id)return;renderGuide(guiaAtual);}
  catch(e){area.replaceChildren(node('p','field-error',e.message));}
}
function renderGuide(s){
  const area=$('guide-details');clear(area);
  const header=node('div','guide-header');
  header.append(node('span','eyebrow','SEU GUIA PRÁTICO'),node('h2','',s.nome),node('p','',s.descricao));
  const section=node('div','guide-progress-section');
  const linha=node('div','progress-title');
  const count=node('strong'),hint=node('span');linha.append(count,hint);
  const progress=node('progress','guide-progress');progress.max=s.orientacoes.length;progress.value=0;
  const campos=node('ol','guide-steps');
  let checked=getProgress()[s.id];
  if(!Array.isArray(checked))checked=[];
  const estados=s.orientacoes.map((_,i)=>checked.includes(i));
  function atualizar(){
    const total=estados.filter(Boolean).length;count.textContent=`${total} de ${estados.length} etapas concluídas`;
    hint.textContent=`${Math.round(100*total/estados.length)}%`;progress.value=total;
    setProgress(s.id,estados.map((ok,i)=>ok?i:-1).filter(i=>i>=0));
  }
  s.orientacoes.forEach((orientacao,i)=>{
    const li=node('li','guide-step'+(estados[i]?' is-done':''));
    const label=node('label','guide-step-label');
    const check=node('input');check.type='checkbox';check.checked=estados[i];
    const conteudo=node('span','guide-step-content');
    conteudo.append(node('span','guide-step-number',`ETAPA ${String(i+1).padStart(2,'0')}`),node('span','guide-step-text',orientacao));
    label.append(check,conteudo);li.append(label);campos.append(li);
    check.addEventListener('change',()=>{estados[i]=check.checked;li.classList.toggle('is-done',check.checked);atualizar();});
  });
  section.append(linha,progress,campos); atualizar();
  const aviso=node('div','guide-warning');aviso.append(node('strong','','Atenção antes de continuar'),node('p','',s.observacoes));
  const sources=node('div','guide-source-section');sources.append(node('h3','','Confira nos canais oficiais'),createSources(s.fontes));
  const actions=node('div','guide-actions');
  actions.append(button('↻ Limpar marcações','button button-secondary',()=>{setProgress(s.id,[]);renderGuide(s);}),
                 link('Tirar dúvida com IA ↗','/assistente?servico='+encodeURIComponent(s.id),'button button-primary'));
  area.append(header,section,aviso,sources,actions);
}

// Conversa contextual usando a integração Groq existente.
function preselectChat(id){
  const s=SERVICOS.find(x=>x.id===id);if(!s)return;
  chatServico=s.id;
  $('chat-input').value='Como faço para acessar '+s.nome+'?';
  for(const b of document.querySelectorAll('[data-chat-servico]'))b.classList.toggle('selected',b.dataset.chatServico===id);
}
function renderChatServiceList(){
  const area=$('chat-service-list');clear(area);
  for(const s of SERVICOS){
    const b=button(serviceSymbol(s)+'  '+s.nome,'chat-service-item',()=>{preselectChat(s.id);$('chat-input').focus();});
    b.dataset.chatServico=s.id;area.append(b);
  }
}
function chatMessage(conteudo,autor='assistant',fontes=[],meta=''){
  const feed=$('chat-feed');
  const welcome=feed.querySelector('.chat-welcome');if(welcome)welcome.remove();
  const row=node('div','chat-message '+(autor==='user'?'from-user':'from-bot'));
  const avatar=node('span','message-avatar',autor==='user'?'EU':'✦');
  const bubble=node('div','message-bubble'); bubble.append(node('div','message-text',conteudo));
  if(fontes && fontes.length){const box=node('div','message-sources');box.append(node('strong','','Fontes oficiais para confirmar:'),createSources(fontes));bubble.append(box);}
  if(autor==='assistant' && meta){
    bubble.append(node('div','message-meta',meta));
    const actions=node('div','message-actions');
    actions.append(button('◖ Ouvir','reply-action',()=>speak(conteudo)),button('⧉ Copiar','reply-action',async()=>{
      try{await navigator.clipboard.writeText(conteudo);toast('Orientação copiada.');}catch{toast('Seu navegador não permitiu copiar automaticamente.');}
    }));
    const positivo=button('✓ Foi útil','reply-action'),negativo=button('× Não foi útil','reply-action');
    const feedback=async (avaliacao)=>{
      positivo.disabled=true;negativo.disabled=true;
      try{await fetchJson('/api/feedback',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({avaliacao})});
          positivo.textContent='Avaliação registrada';negativo.hidden=true;
      }catch(e){positivo.disabled=false;negativo.disabled=false;toast(e.message);}
    };
    positivo.addEventListener('click',()=>feedback('util'));
    negativo.addEventListener('click',()=>feedback('nao_util'));
    actions.append(positivo,negativo);bubble.append(actions);
  }
  row.append(avatar,bubble);feed.append(row);feed.scrollTop=feed.scrollHeight;
  return row;
}
function speak(conteudo){
  if(!('speechSynthesis' in window)){toast('Leitura em voz alta não disponível neste navegador.');return;}
  try {speechSynthesis.cancel();const voz=new SpeechSynthesisUtterance(conteudo);voz.lang='pt-BR';voz.rate=0.96;speechSynthesis.speak(voz);}
  catch {toast('Não foi possível reproduzir a leitura.');}
}
async function submitChat(value){
  if(chatOcupado)return;
  showError('chat-erro','');
  const pergunta=String(value||'').trim();
  if(pergunta.length<4){showError('chat-erro','Escreva uma pergunta com pelo menos 4 caracteres.');return;}
  if(pergunta.length>800){showError('chat-erro','Limite de 800 caracteres por pergunta.');return;}
  chatOcupado=true;$('chat-enviar').disabled=true;$('chat-enviar').textContent='Consultando…';
  chatMessage(pergunta,'user');$('chat-input').value='';
  const loading=chatMessage('Consultando orientações disponíveis…');
  try {
    const dados=await fetchJson('/api/perguntar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pergunta,servico:chatServico,contexto_servico:chatContexto,historico:chatHistorico.slice(-4)})});
    loading.remove();
    chatMessage(dados.resposta,'assistant',dados.fontes||[],dados.modo==='ia'?`${dados.modelo} · ${((dados.tempo_ms||0)/1000).toFixed(1)} s`:'Sem fontes verificadas para este assunto');
    chatHistorico.push({role:'user',content:pergunta},{role:'assistant',content:dados.resposta});
    if(chatHistorico.length>8)chatHistorico=chatHistorico.slice(-8);
    chatContexto=dados.servico||'';chatServico='';
    document.querySelectorAll('[data-chat-servico]').forEach(b=>b.classList.remove('selected'));
  }catch(err){
    loading.remove();const mensagem=err.message||'Não foi possível consultar a IA.';
    chatMessage(mensagem,'assistant');showError('chat-erro',mensagem);
  }finally{chatOcupado=false;$('chat-enviar').disabled=false;$('chat-enviar').textContent='Enviar ➜';$('chat-input').focus();}
}
function initChat(){
  $('chat-form').addEventListener('submit',e=>{e.preventDefault();submitChat($('chat-input').value);});
  $('chat-input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();submitChat($('chat-input').value);}});
  $('chat-limpar').addEventListener('click',()=>{
    chatHistorico=[];chatServico='';chatContexto='';
    $('chat-input').value='';showError('chat-erro','');
    $('chat-feed').replaceChildren();
    const welcome=node('div','chat-welcome');
    welcome.append(node('span','welcome-orb','✳'),node('h2','','Olá! Como posso ajudar?'),node('p','','Escreva uma pergunta sobre um dos serviços disponíveis.'));
    $('chat-feed').append(welcome);
    document.querySelectorAll('[data-chat-servico]').forEach(b=>b.classList.remove('selected'));
    $('chat-input').focus();
  });
  document.querySelectorAll('[data-question]').forEach(b=>b.addEventListener('click',()=>submitChat(b.dataset.question)));
  const Speech=window.SpeechRecognition||window.webkitSpeechRecognition;
  const mic=$('chat-voz');
  if(!Speech){mic.disabled=true;mic.title='Seu navegador não oferece reconhecimento de voz. Use o campo de texto.';mic.textContent='Voz indisponível';return;}
  mic.disabled=false;mic.title='Fale e confira o texto antes de enviar';
  reconhecimento=new Speech(); reconhecimento.lang='pt-BR'; reconhecimento.interimResults=false; reconhecimento.continuous=false;
  reconhecimento.onresult=(event)=>{const frase=event.results?.[0]?.[0]?.transcript||'';if(frase){$('chat-input').value=frase;$('chat-input').focus();toast('Texto reconhecido. Confira antes de enviar.');}};
  reconhecimento.onerror=(event)=>{toast(event.error==='not-allowed'?'Permissão do microfone negada.':'Não foi possível reconhecer a fala. Use o campo de texto.');};
  reconhecimento.onend=()=>{mic.classList.remove('listening');mic.setAttribute('aria-pressed','false');mic.textContent='♩ Falar';};
  mic.addEventListener('click',()=>{
    if(mic.classList.contains('listening')){reconhecimento.stop();return;}
    try{reconhecimento.start();mic.classList.add('listening');mic.setAttribute('aria-pressed','true');mic.textContent='● Ouvindo…';}
    catch{toast('Não foi possível ativar o microfone.');}
  });
}

// Simulador educativo sem coleta de dados identificáveis.
const SITUACOES=[['primeira_vez','Primeira solicitação ou primeiro acesso','Quero começar um serviço pela primeira vez.'],['segunda_via','Segunda via ou recuperação','Preciso substituir um documento ou recuperar acesso.'],['atualizacao','Atualização ou regularização','Preciso atualizar ou corrigir uma informação.'],['consulta','Apenas consultar','Quero entender o assunto antes de iniciar.']];
const MODALIDADES=[['digital','Pela internet','Quero começar por um portal ou aplicativo.'],['presencial','Presencialmente','Prefiro me informar sobre atendimento presencial.'],['indefinida','Ainda não sei','Quero conhecer as possibilidades.']];
function simOption(id,title,sub,field){
  const label=node('label','sim-option'+(simEstado[field]===id?' chosen':''));
  const radio=node('input');radio.type='radio';radio.name=field;radio.value=id;radio.checked=simEstado[field]===id;
  label.append(radio,node('span','sim-option-text'),node('span','sim-option-check','✓'));
  label.querySelector('.sim-option-text').append(node('strong','',title),node('small','',sub));
  radio.addEventListener('change',()=>{simEstado[field]=id;renderSim();});
  return label;
}
function renderSim(){
  const area=$('sim-stage');clear(area);showError('sim-error','');
  $('sim-back').hidden=simEtapa===1||simEtapa===4;
  $('sim-next').hidden=simEtapa===4;
  $('sim-next').textContent=simEtapa===3?'Gerar orientações ↗':'Continuar →';
  const marks=[...$('sim-steps').querySelectorAll('.step-mark')];
  marks.forEach((m,i)=>{m.classList.toggle('active',i+1===Math.min(simEtapa,3));m.classList.toggle('done',i+1<simEtapa);});
  if(simEtapa===4)return;
  const stepText=['Qual serviço você procura?','Qual é a sua situação?','Como prefere começar?'];
  area.append(node('p','sim-step-label',`PERGUNTA ${simEtapa} DE 3`),node('h2','',stepText[simEtapa-1]));
  const options=node('div','sim-options');
  if(simEtapa===1)for(const s of SERVICOS)options.append(simOption(s.id,s.nome,s.categoria,'servico'));
  if(simEtapa===2)for(const [id,title,sub] of SITUACOES)options.append(simOption(id,title,sub,'situacao'));
  if(simEtapa===3)for(const [id,title,sub] of MODALIDADES)options.append(simOption(id,title,sub,'modalidade'));
  area.append(options);
}
async function runSimulation(){
  $('sim-next').disabled=true;$('sim-next').textContent='Preparando…';
  try {
    const dados=await fetchJson('/api/simular',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(simEstado)});
    simEtapa=4;renderSim();renderSimulationResult(dados);
  }catch(e){showError('sim-error',e.message);$('sim-next').textContent='Gerar orientações ↗';}
  finally{$('sim-next').disabled=false;}
}
function renderSimulationResult(dados){
  const area=$('sim-stage');clear(area);
  area.append(node('span','sim-success','✓ SIMULAÇÃO CONCLUÍDA'),node('h2','','Seu caminho para '+dados.nome),node('p','sim-subtitle',dados.situacao+' · '+dados.modalidade));
  const section=node('div','simulation-section');section.append(node('h3','','Passos sugeridos'));
  const steps=node('ol','simulation-steps');for(const etapa of dados.etapas)steps.append(node('li','',etapa));section.append(steps);
  const docs=node('div','simulation-section');docs.append(node('h3','','Documentos e requisitos: o que conferir'));
  const ul=node('ul','simulation-docs');for(const d of dados.documentos)ul.append(node('li','',d));docs.append(ul);
  const warning=node('div','simulation-warning');warning.append(node('strong','','Informação importante'),node('p','',dados.observacoes),node('p','',dados.aviso));
  const refs=node('div','simulation-section');refs.append(node('h3','','Links oficiais'),createSources(dados.fontes));
  const actions=node('div','simulation-actions');
  actions.append(link('Abrir guia completo ↗','/guias?servico='+encodeURIComponent(dados.servico),'button button-primary'),button('↻ Nova simulação','button button-secondary',()=>{simEtapa=1;simEstado={servico:'',situacao:'',modalidade:''};renderSim();}));
  area.append(section,docs,warning,refs,actions);
}
function initSimulator(){
  $('sim-back').addEventListener('click',()=>{if(simEtapa>1){simEtapa--;renderSim();}});
  $('sim-next').addEventListener('click',()=>{
    const campo=['servico','situacao','modalidade'][simEtapa-1];
    if(!simEstado[campo]){showError('sim-error','Escolha uma opção para continuar.');return;}
    if(simEtapa<3){simEtapa++;renderSim();}else runSimulation();
  });
  renderSim();
}

// Indicadores genuínos a partir do CSV local; nada é inventado no frontend.
function metricCard(label,value,detail,symbol){const c=node('div','metric-card');c.append(node('span','metric-icon',symbol),node('p','metric-label',label),node('strong','metric-value',value),node('p','metric-help',detail));return c;}
async function renderMetrics(){
  const target=$('metric-cards');target.replaceChildren(node('p','loading-text','Carregando dados…'));
  try{
    const d=await fetchJson('/api/indicadores');clear(target);
    const ms=d.tempo_medio_ms;
    target.append(metricCard('Consultas concluídas',d.consultas_concluidas,'Respostas da IA entregues','✦'),
                  metricCard('Tempo médio',ms===null?'—':(ms/1000).toFixed(1)+'s',ms===null?'Ainda sem consultas':'Tempo de resposta da API e do servidor','◷'),
                  metricCard('Avaliações recebidas',d.total_avaliacoes,'Feedback voluntário de usuários','♡'),
                  metricCard('Respostas úteis',d.percentual_util===null?'—':d.percentual_util.toFixed(1)+'%',d.total_avaliacoes?'Entre as avaliações recebidas':'Sem avaliações até agora','✓'));
    const chart=$('chart-services');clear(chart);
    const max=Math.max(1,...d.por_servico.map(x=>x.total));
    for(const item of d.por_servico){
      const row=node('div','bar-row');const label=node('div','bar-label',item.nome);
      const track=node('div','bar-track');const fill=node('div','bar-fill');fill.style.width=(item.total/max*100)+'%';track.append(fill);
      row.append(label,track,node('strong','bar-count',item.total));chart.append(row);
    }
    if(!d.consultas_concluidas)chart.append(node('p','chart-empty','As barras serão preenchidas conforme as consultas forem realizadas.'));
    const feedback=$('feedback-chart');clear(feedback);
    if(!d.total_avaliacoes){feedback.append(node('div','feedback-empty','Ainda não há avaliações. Você pode avaliar a utilidade após conversar com a IA.'));}
    else {
      const ratio=node('div','feedback-ratio');ratio.append(node('strong','',d.percentual_util.toFixed(1)+'%'),node('span','','avaliaram como útil'));
      const progress=node('progress','feedback-progress');progress.max=100;progress.value=d.percentual_util;
      feedback.append(ratio,progress,node('p','feedback-label',`${d.avaliacoes_uteis} úteis · ${d.avaliacoes_nao_uteis} não úteis`));
    }
    const classifier=$('classifier-score');clear(classifier);
    const c=d.avaliacao_regras;
    const circle=node('div','classifier-score');circle.append(node('strong','',c.percentual===null?'—':c.percentual.toFixed(1)+'%'),node('span','',`${c.acertos} de ${c.total} casos de teste`));
    classifier.append(circle);
  }catch(e){target.replaceChildren(node('p','field-error','Não foi possível carregar os indicadores: '+e.message));}
}

// Transparência e fontes.
function renderSources(){
  const area=$('source-list');clear(area);
  let count=0;
  for(const s of SERVICOS){
    const box=node('div','source-item');
    const h=node('div','source-item-heading');h.append(node('span','source-dot',serviceSymbol(s)),node('strong','',s.nome));
    const links=createSources(s.fontes);count+=links.querySelectorAll('a').length;
    box.append(h,links);area.append(box);
  }
  text('source-count',`${count} referências cadastradas`);
}
function initAccess() {
  let zoom=Number(document.documentElement.dataset.zoom||0);
  function changeZoom(v){zoom=Math.max(-1,Math.min(2,v));document.documentElement.dataset.zoom=String(zoom);}
  $('font-up').addEventListener('click',()=>changeZoom(zoom+1));
  $('font-down').addEventListener('click',()=>changeZoom(zoom-1));
  $('contrast-toggle').addEventListener('click',()=>{
    const active=document.body.classList.toggle('contrast-mode');
    $('contrast-toggle').setAttribute('aria-pressed',String(active));
  });
}
async function initApp(){
  initNavigation();initChat();initSimulator();initAccess();
  $('service-search').addEventListener('input',renderCatalog);
  $('refresh-metrics').addEventListener('click',renderMetrics);
  try{
    const [servicos,status]=await Promise.all([fetchJson('/api/servicos'),fetchJson('/api/status')]);
    SERVICOS=servicos;
    const pill=$('status-api');pill.textContent=status.configurado?'Assistente disponível':'Assistente indisponível';
    pill.classList.add(status.configurado?'api-ok':'api-warn');
    pill.title=status.configurado?'Pronto para responder suas perguntas.':'O atendimento por IA está temporariamente indisponível.';
    renderHomeServices();renderFilters();renderCatalog();drawGuideSelector();renderChatServiceList();renderSources();renderSim();
  }catch(e){
    $('status-api').textContent='Servidor indisponível';
    toast('Não foi possível carregar os serviços: '+e.message);
    $('services-catalog').append(node('p','field-error','Reinicie o servidor com python main.py.'));
  }
  setRoute(ROUTES[location.pathname]?location.pathname:'/',new URLSearchParams(location.search));
}
initApp();
