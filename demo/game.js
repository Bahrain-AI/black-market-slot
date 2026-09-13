/* BLACK MARKET — reference-matched audience demo.
 * Local virtual-credit outcomes only. Production math is not final.
 */
(function(){
'use strict';
var SYMBOLS=['watch','diamond','ace','gold','cash','passport','bag','bust','wild','vip'];
var PREMIUM=['watch','diamond','gold','cash','vip'];
var LOW=['ace','passport','bag','bust'];
var SPECIALS=['scatter','buyer','wild-case','multiplier','red-phone','printer','vault-key','emp'];
var MODIFIERS=['counterfeit-printer','golden-key','inside-man','emp','red-phone','double-agent','marked-lot'];
var INITIAL_BOARD=['watch','diamond','ace','gold','cash','passport','bag','bust','wild','vip','gold','cash','watch','diamond','passport','bust','wild','vip','bag','ace'];
var INITIAL_TILES=['tile-00-watch','tile-01-diamond','tile-02-ace','tile-03-gold','tile-04-cash','tile-05-passport','tile-06-bag','tile-07-bust','tile-08-wild','tile-09-vip','tile-10-gold','tile-11-cash','tile-12-watch','tile-13-diamond','tile-14-passport','tile-15-bust','tile-16-wild','tile-17-vip','tile-18-bag','tile-19-ace'];
var BUY_MODES={
  backroom:{name:'BACKROOM PASS',costMult:60,spins:6,startMult:1,specialRate:.78,mods:[]},
  vault:{name:'VAULT ACCESS',costMult:100,spins:8,startMult:1,specialRate:.58,mods:['random']},
  black:{name:'BLACK CARD',costMult:200,spins:10,startMult:3,specialRate:.72,mods:['random','random']}
};
var BALANCE=991.30,BET=1.00,BET_STEPS=[.10,.20,.50,1,2,5,10];
function el(id){return document.getElementById(id);} function choice(a){return a[Math.floor(Math.random()*a.length)];} function rand(){return Math.floor(Math.random()*20);} function money(v){return '$'+Number(v).toFixed(2);}
var spinBtn=el('btnSpin'),minusBtn=el('btnMinus'),plusBtn=el('btnPlus'),turboBtn=el('btnTurbo'),autoBtn=el('btnAutoplay'),menuBtn=el('btnMenu'),buyBtn=el('btnBuy');
var balanceEl=el('balance'),betEl=el('bet'),gridEl=el('reelGrid'),messageEl=el('message'),modalEl=el('modal'),modalClose=el('modalClose');
var bonusModal=el('bonusModal'),bonusClose=el('bonusClose'),bonusCards=[].slice.call(document.querySelectorAll('.bonus-card')),buyConfirm=el('buyConfirm'),confirmName=el('confirmName'),confirmCost=el('confirmCost'),confirmBuy=el('confirmBuy');
var bonusStatus=el('bonusStatus'),bonusModeEl=el('bonusMode'),bonusSpinsEl=el('bonusSpins'),bonusMultiplierEl=el('bonusMultiplier'),featureSplash=el('featureSplash'),featureSplashLabel=el('featureSplashLabel');
var board=INITIAL_BOARD.slice(),cells=[],spinning=false,turbo=false,autoplay=false,autoplaySpins=0,messageTimer=null,selectedBuy=null;
var bonusActive=false,bonusEnding=false,bonusMode=null,bonusSpins=0,bonusMultiplier=1,bonusTotal=0,bonusMods=[],bonusSpecialRate=.55;

function drawBoard(grid,tiles){
  gridEl.innerHTML='';cells=[];var base=tiles?'./assets/tiles/':'./assets/symbols/';
  grid.forEach(function(sym){var d=document.createElement('div');d.className='cell';var img=document.createElement('img');img.src=base+sym+'.webp';img.alt=sym;img.draggable=false;d.appendChild(img);gridEl.appendChild(d);cells.push(d);});
}
function updateHUD(){balanceEl.textContent=money(BALANCE);betEl.textContent=money(BET);if(bonusActive){bonusModeEl.textContent=bonusMode.name;bonusSpinsEl.textContent=bonusSpins;bonusMultiplierEl.textContent='×'+bonusMultiplier;bonusStatus.classList.add('active');}else bonusStatus.classList.remove('active');}
function pick(){if(Math.random()<.05)return'wild';return choice(SYMBOLS.filter(function(s){return s!=='wild';}));}
function evaluate(g){var won={},mult=0;function line(ids){SYMBOLS.forEach(function(s){if(s==='wild')return;var m=ids.filter(function(i){return g[i]===s||g[i]==='wild';});if(m.length>=3){m.forEach(function(i){won[i]=true;});mult+=m.length===5?8:(m.length===4?4:1.5);}});}for(var r=0;r<4;r++)line([r*5,r*5+1,r*5+2,r*5+3,r*5+4]);for(var c=0;c<5;c++)line([c,5+c,10+c,15+c]);return{won:won,mult:mult};}
function showMessage(t,d){if(messageTimer)clearTimeout(messageTimer);messageEl.textContent=t;messageEl.classList.add('show');messageTimer=setTimeout(function(){messageEl.classList.remove('show');},d||1300);}
function splash(t,d){featureSplashLabel.textContent=t;featureSplash.classList.add('show');setTimeout(function(){featureSplash.classList.remove('show');},d||850);}
function clearWins(){cells.forEach(function(c){c.classList.remove('win');});}
function showSpecial(name){var i=rand(),n=document.createElement('span');n.className='special-token '+name;if(cells[i])cells[i].appendChild(n);return n;}
function forcePremium(g,n){for(var i=0;i<n;i++)g[rand()]=choice(PREMIUM);}
function rerollLow(g,n){var ids=[];g.forEach(function(s,i){if(LOW.indexOf(s)>=0)ids.push(i);});while(n--&&ids.length){var k=Math.floor(Math.random()*ids.length),i=ids.splice(k,1)[0];g[i]=choice(PREMIUM.concat(['wild']));}}
function duplicatePremium(g){var p=g.filter(function(s){return PREMIUM.indexOf(s)>=0;});if(!p.length)return;var s=choice(p);g[rand()]=s;g[rand()]=s;}
function spawnWilds(g,n){while(n--)g[rand()]='wild';}
function applyMods(g){var boost=1;if(bonusMods.indexOf('golden-key')>=0)forcePremium(g,1);if(bonusMods.indexOf('emp')>=0)rerollLow(g,2);if(bonusMods.indexOf('counterfeit-printer')>=0)duplicatePremium(g);if(bonusMods.indexOf('marked-lot')>=0){var col=Math.floor(Math.random()*5);for(var r=0;r<4;r++)if(Math.random()<.55)g[r*5+col]=choice(PREMIUM);}if(bonusMods.indexOf('red-phone')>=0&&Math.random()<.28)boost*=2;return boost;}
function applySpecial(g,name){var boost=1,label='';if(name==='scatter'){bonusSpins+=2;label='SCATTER · +2 SPINS';}else if(name==='buyer'){spawnWilds(g,2);label='BUYER · 2 WILDS';}else if(name==='wild-case'){spawnWilds(g,3);label='WILD CASE · 3 WILDS';}else if(name==='multiplier'){bonusMultiplier=Math.min(25,bonusMultiplier*2);label='MULTIPLIER · ×'+bonusMultiplier;}else if(name==='red-phone'){boost=choice([2,3,5]);label='RED PHONE · ×'+boost;}else if(name==='printer'){duplicatePremium(g);label='COUNTERFEIT · DUPLICATE';}else if(name==='vault-key'){forcePremium(g,2);label='VAULT KEY · PREMIUM';}else if(name==='emp'){rerollLow(g,4);label='EMP · LOW VALUES REMOVED';}return{boost:boost,label:label};}
function modLabel(m){var map={'counterfeit-printer':'COUNTERFEIT PRINTER','golden-key':'GOLDEN KEY','inside-man':'INSIDE MAN','emp':'EMP','red-phone':'RED PHONE','double-agent':'DOUBLE AGENT','marked-lot':'MARKED LOT'};return map[m]||m.toUpperCase();}

function finishOutcome(g,boost){
  gridEl.classList.remove('spinning');drawBoard(g,false);board=g;var result=evaluate(g),applied=bonusActive?bonusMultiplier*(boost||1):1,win=BET*result.mult*applied;
  if(win>0){BALANCE+=win;if(bonusActive)bonusTotal+=win;Object.keys(result.won).forEach(function(i){if(cells[+i])cells[+i].classList.add('win');});showMessage('WIN '+money(win)+(applied>1?' · ×'+applied:''),1500);}
  spinning=false;spinBtn.disabled=false;spinBtn.classList.remove('spinning');
  if(bonusActive){bonusSpins--;updateHUD();if(bonusSpins<=0)setTimeout(endBonus,turbo?450:1000);else setTimeout(spin,turbo?300:850);}else{updateHUD();settleAutoplay();}
}
function resolveBonus(next){
  var g=next.slice(),boost=applyMods(g),rate=bonusSpecialRate+(bonusMods.indexOf('inside-man')>=0?.15:0),special=Math.random()<Math.min(.92,rate)?choice(SPECIALS):null;
  if(!special){finishOutcome(g,boost);return;}
  drawBoard(g,false);var token=showSpecial(special),wait=turbo?180:520;
  setTimeout(function(){if(token&&token.parentNode)token.parentNode.removeChild(token);var one=applySpecial(g,special);boost*=one.boost;if(bonusMods.indexOf('double-agent')>=0){var second=choice(SPECIALS.filter(function(s){return s!==special;})),two=applySpecial(g,second);boost*=two.boost;splash(one.label+' + '+two.label,turbo?450:780);}else splash(one.label,turbo?420:720);updateHUD();setTimeout(function(){finishOutcome(g,boost);},turbo?120:360);},wait);
}
function spin(){
  if(spinning||bonusEnding)return;if(!bonusActive&&BALANCE<BET){showMessage('INSUFFICIENT BALANCE',1400);stopAutoplay();return;}spinning=true;clearWins();spinBtn.disabled=true;spinBtn.classList.add('spinning');if(!bonusActive)BALANCE-=BET;updateHUD();gridEl.classList.add('spinning');setTimeout(function(){var next=Array.from({length:20},pick);if(bonusActive)resolveBonus(next);else finishOutcome(next,1);},turbo?250:760);
}
function settleAutoplay(){if(!autoplay)return;if(autoplaySpins>0)autoplaySpins--;if(autoplaySpins<=0||BALANCE<BET){stopAutoplay();return;}autoBtn.textContent='AUTO · '+autoplaySpins;setTimeout(spin,350);}
function startAutoplay(){if(spinning||autoplay||bonusActive)return;if(BALANCE<BET){showMessage('INSUFFICIENT BALANCE',1400);return;}autoplay=true;autoplaySpins=10;autoBtn.classList.add('active');autoBtn.textContent='AUTO · '+autoplaySpins;spin();}
function stopAutoplay(){autoplay=false;autoplaySpins=0;autoBtn.classList.remove('active');autoBtn.textContent='AUTOPLAY';}
function shiftBet(d){if(spinning||bonusActive)return;var i=BET_STEPS.indexOf(BET);if(i<0)i=3;BET=BET_STEPS[Math.max(0,Math.min(BET_STEPS.length-1,i+d))];updateHUD();if(selectedBuy)renderBuy(selectedBuy);}
function lockControls(v){minusBtn.disabled=v;plusBtn.disabled=v;autoBtn.disabled=v;buyBtn.disabled=v;}

function openBuy(){if(spinning||bonusActive)return;stopAutoplay();selectedBuy=null;buyConfirm.hidden=true;bonusCards.forEach(function(c){c.classList.remove('selected');});bonusModal.classList.add('open');bonusModal.setAttribute('aria-hidden','false');}
function closeBuy(){if(bonusActive)return;bonusModal.classList.remove('open');bonusModal.setAttribute('aria-hidden','true');selectedBuy=null;}
function renderBuy(key){var cfg=BUY_MODES[key];if(!cfg)return;selectedBuy=key;bonusCards.forEach(function(c){c.classList.toggle('selected',c.getAttribute('data-mode')===key);});confirmName.textContent=cfg.name;confirmCost.textContent=money(BET*cfg.costMult);confirmBuy.disabled=BALANCE<BET*cfg.costMult;confirmBuy.textContent=confirmBuy.disabled?'INSUFFICIENT BALANCE':'CONFIRM PURCHASE';buyConfirm.hidden=false;}
function chooseMods(cfg){var r=[];cfg.mods.forEach(function(m){if(m!=='random'){r.push(m);return;}var pool=MODIFIERS.filter(function(x){return r.indexOf(x)<0;});r.push(choice(pool));});return r;}
function startBonus(key){var cfg=BUY_MODES[key];if(!cfg)return;var cost=BET*cfg.costMult;if(BALANCE<cost){showMessage('INSUFFICIENT BALANCE',1500);renderBuy(key);return;}BALANCE-=cost;bonusModal.classList.remove('open');bonusModal.setAttribute('aria-hidden','true');bonusActive=true;bonusEnding=false;bonusMode=cfg;bonusSpins=cfg.spins;bonusMultiplier=cfg.startMult;bonusTotal=0;bonusSpecialRate=cfg.specialRate;bonusMods=chooseMods(cfg);lockControls(true);stopAutoplay();updateHUD();var mods=bonusMods.length?' · '+bonusMods.map(modLabel).join(' + '):'';splash('ACCESS GRANTED · '+cfg.name+mods,1200);setTimeout(spin,turbo?500:1250);}
function endBonus(){if(!bonusActive||bonusEnding)return;bonusEnding=true;var total=bonusTotal,name=bonusMode.name;splash(name+' COMPLETE · '+money(total),1500);setTimeout(function(){bonusActive=false;bonusEnding=false;bonusMode=null;bonusSpins=0;bonusMultiplier=1;bonusTotal=0;bonusMods=[];lockControls(false);spinBtn.disabled=false;updateHUD();},turbo?800:1600);}
function closeInfo(){modalEl.classList.remove('open');modalEl.setAttribute('aria-hidden','true');}

spinBtn.addEventListener('click',function(){if(!bonusActive)spin();});minusBtn.addEventListener('click',function(){shiftBet(-1);});plusBtn.addEventListener('click',function(){shiftBet(1);});
turboBtn.addEventListener('click',function(e){turbo=!turbo;e.currentTarget.classList.toggle('active',turbo);});autoBtn.addEventListener('click',function(){if(bonusActive)return;if(autoplay)stopAutoplay();else startAutoplay();});
menuBtn.addEventListener('click',function(){if(bonusActive)return;modalEl.classList.add('open');modalEl.setAttribute('aria-hidden','false');});modalClose.addEventListener('click',closeInfo);modalEl.addEventListener('click',function(e){if(e.target===modalEl)closeInfo();});
buyBtn.addEventListener('click',openBuy);bonusClose.addEventListener('click',closeBuy);bonusModal.addEventListener('click',function(e){if(e.target===bonusModal)closeBuy();});bonusCards.forEach(function(card){card.addEventListener('click',function(){renderBuy(card.getAttribute('data-mode'));});});confirmBuy.addEventListener('click',function(){if(selectedBuy)startBonus(selectedBuy);});
document.addEventListener('keydown',function(e){var open=modalEl.classList.contains('open')||bonusModal.classList.contains('open');if(e.code==='Escape'){if(modalEl.classList.contains('open'))closeInfo();if(bonusModal.classList.contains('open'))closeBuy();}if(e.code==='Space'&&!open&&!spinning&&!bonusActive){e.preventDefault();if(autoplay)stopAutoplay();spin();}if(!open&&!bonusActive&&(e.key==='ArrowLeft'||e.key==='-')){e.preventDefault();shiftBet(-1);}if(!open&&!bonusActive&&(e.key==='ArrowRight'||e.key==='+'||e.key==='=')){e.preventDefault();shiftBet(1);}if(!open&&!bonusActive&&(e.key==='b'||e.key==='B'))openBuy();});
drawBoard(INITIAL_TILES,true);updateHUD();
})();