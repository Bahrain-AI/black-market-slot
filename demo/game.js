/* BLACK MARKET — reference-matched audience demo
 * Self-contained: no external runtime dependencies.
 * All outcomes, Bonus Buy prices and feature behavior are local prototype logic only.
 */
(function () {
  'use strict';

  var SYMBOLS = ['watch','diamond','ace','gold','cash','passport','bag','bust','wild','vip'];
  var PREMIUM = ['watch','diamond','gold','cash','vip'];
  var LOW = ['ace','passport','bag','bust'];
  var SPECIALS = ['scatter','buyer','wild-case','multiplier','red-phone','printer','vault-key','emp'];
  var MODIFIERS = ['counterfeit-printer','golden-key','inside-man','emp','red-phone','double-agent','marked-lot'];

  var INITIAL_BOARD = [
    'watch','diamond','ace','gold','cash',
    'passport','bag','bust','wild','vip',
    'gold','cash','watch','diamond','passport',
    'bust','wild','vip','bag','ace'
  ];
  var INITIAL_TILES = [
    'tile-00-watch','tile-01-diamond','tile-02-ace','tile-03-gold','tile-04-cash',
    'tile-05-passport','tile-06-bag','tile-07-bust','tile-08-wild','tile-09-vip',
    'tile-10-gold','tile-11-cash','tile-12-watch','tile-13-diamond','tile-14-passport',
    'tile-15-bust','tile-16-wild','tile-17-vip','tile-18-bag','tile-19-ace'
  ];

  var BUY_MODES = {
    backroom:{name:'BACKROOM PASS',costMult:60,spins:6,startMult:1,specialRate:.72,mods:[]},
    vault:{name:'VAULT ACCESS',costMult:100,spins:8,startMult:1,specialRate:.58,mods:['random']},
    black:{name:'BLACK CARD',costMult:200,spins:10,startMult:3,specialRate:.72,mods:['random','random']}
  };

  var BALANCE = 991.30;
  var BET = 1.00;
  var BET_STEPS = [0.10,0.20,0.50,1,2,5,10];

  var spinBtn = document.getElementById('btnSpin');
  var minusBtn = document.getElementById('btnMinus');
  var plusBtn = document.getElementById('btnPlus');
  var turboBtn = document.getElementById('btnTurbo');
  var autoBtn = document.getElementById('btnAutoplay');
  var menuBtn = document.getElementById('btnMenu');
  var buyBtn = document.getElementById('btnBuy');
  var balanceEl = document.getElementById('balance');
  var betEl = document.getElementById('bet');
  var gridEl = document.getElementById('reelGrid');
  var messageEl = document.getElementById('message');
  var modalEl = document.getElementById('modal');
  var modalClose = document.getElementById('modalClose');
  var bonusModal = document.getElementById('bonusModal');
  var bonusClose = document.getElementById('bonusClose');
  var bonusCards = Array.prototype.slice.call(document.querySelectorAll('.bonus-card'));
  var buyConfirm = document.getElementById('buyConfirm');
  var confirmName = document.getElementById('confirmName');
  var confirmCost = document.getElementById('confirmCost');
  var confirmBuy = document.getElementById('confirmBuy');
  var bonusStatus = document.getElementById('bonusStatus');
  var bonusModeEl = document.getElementById('bonusMode');
  var bonusSpinsEl = document.getElementById('bonusSpins');
  var bonusMultiplierEl = document.getElementById('bonusMultiplier');
  var featureSplash = document.getElementById('featureSplash');
  var featureSplashLabel = document.getElementById('featureSplashLabel');

  var board = INITIAL_BOARD.slice();
  var cells = [];
  var spinning = false;
  var turbo = false;
  var autoplay = false;
  var autoplaySpins = 0;
  var messageTimer = null;
  var selectedBuy = null;

  var bonusActive = false;
  var bonusMode = null;
  var bonusSpins = 0;
  var bonusMultiplier = 1;
  var bonusTotal = 0;
  var bonusMods = [];
  var bonusSpecialRate = .55;
  var bonusEnding = false;

  function money(v){ return '$' + Number(v).toFixed(2); }
  function choice(arr){ return arr[Math.floor(Math.random()*arr.length)]; }
  function randomIndex(){ return Math.floor(Math.random()*20); }

  function drawBoard(grid, areTiles){
    gridEl.innerHTML='';
    cells=[];
    var imgBase=areTiles?'./assets/tiles/':'./assets/symbols/';
    grid.forEach(function(sym){
      var d=document.createElement('div'); d.className='cell';
      var img=document.createElement('img'); img.src=imgBase+sym+'.webp'; img.alt=sym; img.draggable=false;
      d.appendChild(img); gridEl.appendChild(d); cells.push(d);
    });
  }

  function updateHUD(){
    balanceEl.textContent=money(BALANCE);
    betEl.textContent=money(BET);
    if(bonusActive){
      bonusModeEl.textContent=bonusMode.name;
      bonusSpinsEl.textContent=bonusSpins;
      bonusMultiplierEl.textContent='×'+bonusMultiplier;
      bonusStatus.classList.add('active');
    }else{
      bonusStatus.classList.remove('active');
    }
  }

  function pick(){
    if(Math.random()<.05) return 'wild';
    var pool=SYMBOLS.filter(function(s){return s!=='wild';});
    return choice(pool);
  }

  function evaluate(grid){
    var won={},mult=0;
    function line(ids){
      SYMBOLS.forEach(function(s){
        if(s==='wild') return;
        var matches=ids.filter(function(idx){return grid[idx]===s||grid[idx]==='wild';});
        if(matches.length>=3){
          matches.forEach(function(idx){won[idx]=true;});
          mult+=matches.length===5?8:(matches.length===4?4:1.5);
        }
      });
    }
    for(var r=0;r<4;r++) line([r*5,r*5+1,r*5+2,r*5+3,r*5+4]);
    for(var c=0;c<5;c++) line([c,5+c,10+c,15+c]);
    return {won:won,mult:mult};
  }

  function showMessage(text,duration){
    if(messageTimer) clearTimeout(messageTimer);
    messageEl.textContent=text; messageEl.classList.add('show');
    messageTimer=setTimeout(function(){messageEl.classList.remove('show');},duration||1300);
  }

  function splash(text,duration){
    featureSplashLabel.textContent=text;
    featureSplash.classList.add('show');
    setTimeout(function(){featureSplash.classList.remove('show');},duration||850);
  }

  function clearHighlights(){ cells.forEach(function(c){c.classList.remove('win');}); }

  function showSpecialToken(name){
    var idx=randomIndex();
    var token=document.createElement('span');
    token.className='special-token '+name;
    cells[idx] && cells[idx].appendChild(token);
    return token;
  }

  function forcePremium(grid,count){
    for(var i=0;i<count;i++) grid[randomIndex()]=choice(PREMIUM);
  }
  function rerollLow(grid,count){
    var candidates=[];
    grid.forEach(function(s,i){if(LOW.indexOf(s)>=0)candidates.push(i);});
    for(var n=0;n<count&&candidates.length;n++){
      var k=Math.floor(Math.random()*candidates.length),idx=candidates.splice(k,1)[0];
      grid[idx]=choice(PREMIUM.concat(['wild']));
    }
  }
  function duplicatePremium(grid){
    var candidates=[];
    grid.forEach(function(s){if(PREMIUM.indexOf(s)>=0)candidates.push(s);});
    if(!candidates.length)return;
    var sym=choice(candidates); grid[randomIndex()]=sym; grid[randomIndex()]=sym;
  }
  function spawnWilds(grid,count){ for(var i=0;i<count;i++)grid[randomIndex()]='wild'; }

  function applyPersistentModifiers(grid){
    var spinBoost=1;
    if(bonusMods.indexOf('golden-key')>=0) forcePremium(grid,1);
    if(bonusMods.indexOf('emp')>=0) rerollLow(grid,2);
    if(bonusMods.indexOf('counterfeit-printer')>=0) duplicatePremium(grid);
    if(bonusMods.indexOf('marked-lot')>=0){
      var col=Math.floor(Math.random()*5);
      for(var r=0;r<4;r++) if(Math.random()<.55) grid[r*5+col]=choice(PREMIUM);
    }
    if(bonusMods.indexOf('red-phone')>=0 && Math.random()<.28) spinBoost*=2;
    return spinBoost;
  }

  function applySpecial(grid,name){
    var boost=1,label='';
    if(name==='scatter'){bonusSpins+=2;label='SCATTER · +2 SPINS';}
    if(name==='buyer'){spawnWilds(grid,2);label='BUYER · 2 WILDS';}
    if(name==='wild-case'){spawnWilds(grid,3);label='WILD CASE · 3 WILDS';}
    if(name==='multiplier'){bonusMultiplier=Math.min(25,bonusMultiplier*2);label='MULTIPLIER · ×'+bonusMultiplier;}
    if(name==='red-phone'){boost=choice([2,3,5]);label='RED PHONE · ×'+boost;}
    if(name==='printer'){duplicatePremium(grid);label='COUNTERFEIT · DUPLICATE';}
    if(name==='vault-key'){forcePremium(grid,2);label='VAULT KEY · PREMIUM';}
    if(name==='emp'){rerollLow(grid,4);label='EMP · LOW VALUES REMOVED';}
    return {boost:boost,label:label};
  }

  function modifierLabel(m){
    return {'counterfeit-printer':'COUNTERFEIT PRINTER','golden-key':'GOLDEN KEY','inside-man':'INSIDE MAN','emp':'EMP','red-phone':'RED PHONE','double-agent':'DOUBLE AGENT','marked-lot':'MARKED LOT'}[m]||m.toUpperCase();
  }

  function finishOutcome(nextGrid,spinBoost){
    gridEl.classList.remove('spinning');
    drawBoard(nextGrid,false); board=nextGrid;
    var result=evaluate(board);
    var applied=bonusActive?bonusMultiplier*(spinBoost||1):1;
    var win=BET*result.mult*applied;
    if(win>0){
      BALANCE+=win;
      if(bonusActive) bonusTotal+=win;
      Object.keys(result.won).forEach(function(idx){if(cells[Number(idx)])cells[Number(idx)].classList.add('win');});
      showMessage('WIN '+money(win)+(applied>1?' · ×'+applied:''),1500);
    }
    updateHUD();
    spinning=false; spinBtn.disabled=false; spinBtn.classList.remove('spinning');

    if(bonusActive){
      bonusSpins--;
      updateHUD();
      if(bonusSpins<=0){ setTimeout(endBonus,turbo?450:1000); }
      else { setTimeout(spin,turbo?300:850); }
    }else{ settleAutoplay(); }
  }

  function resolveBonus(nextGrid){
    var grid=nextGrid.slice();
    var boost=applyPersistentModifiers(grid);
    var rate=bonusSpecialRate+(bonusMods.indexOf('inside-man')>=0?.15:0);
    var special=Math.random()<Math.min(.92,rate)?choice(SPECIALS):null;
    if(!special){ finishOutcome(grid,boost); return; }

    drawBoard(grid,false);
    var token=showSpecialToken(special);
    var wait=turbo?180:520;
    setTimeout(function(){
      if(token&&token.parentNode)token.parentNode.removeChild(token);
      var resolved=applySpecial(grid,special); boost*=resolved.boost;
      if(bonusMods.indexOf('double-agent')>=0){
        var second=choice(SPECIALS.filter(function(s){return s!==special;}));
        var again=applySpecial(grid,second); boost*=again.boost;
        splash(resolved.label+' + '+again.label,turbo?450:780);
      }else splash(resolved.label,turbo?420:720);
      updateHUD();
      setTimeout(function(){finishOutcome(grid,boost);},turbo?120:360);
    },wait);
  }

  function spin(){
    if(spinning||bonusEnding)return;
    if(!bonusActive&&BALANCE<BET){showMessage('INSUFFICIENT BALANCE',1400);stopAutoplay();return;}
    spinning=true; clearHighlights(); spinBtn.disabled=true; spinBtn.classList.add('spinning');
    if(!bonusActive) BALANCE-=BET;
    updateHUD(); gridEl.classList.add('spinning');
    var duration=turbo?250:760;
    setTimeout(function(){
      var nextGrid=Array.from({length:20},pick);
      if(bonusActive) resolveBonus(nextGrid); else finishOutcome(nextGrid,1);
    },duration);
  }

  function settleAutoplay(){
    if(!autoplay)return;
    if(autoplaySpins>0)autoplaySpins--;
    if(autoplaySpins<=0||BALANCE<BET){stopAutoplay();return;}
    autoBtn.textContent='AUTO · '+autoplaySpins;
    setTimeout(spin,350);
  }
  function startAutoplay(){
    if(spinning||autoplay||bonusActive)return;
    if(BALANCE<BET){showMessage('INSUFFICIENT BALANCE',1400);return;}
    autoplay=true;autoplaySpins=10;autoBtn.classList.add('active');autoBtn.textContent='AUTO · '+autoplaySpins;spin();
  }
  function stopAutoplay(){autoplay=false;autoplaySpins=0;autoBtn.classList.remove('active');autoBtn.textContent='AUTOPLAY';}

  function shiftBet(delta){
    if(spinning||bonusActive)return;
    var idx=BET_STEPS.indexOf(BET);if(idx<0)idx=3;
    BET=BET_STEPS[Math.max(0,Math.min(BET_STEPS.length-1,idx+delta))];updateHUD();
    if(selectedBuy)renderBuyConfirmation(selectedBuy);
  }

  function setBaseControlsLocked(locked){
    minusBtn.disabled=locked; plusBtn.disabled=locked; autoBtn.disabled=locked; buyBtn.disabled=locked;
  }

  function openBonusBuy(){
    if(spinning||bonusActive)return;
    stopAutoplay(); selectedBuy=null; buyConfirm.hidden=true;
    bonusCards.forEach(function(c){c.classList.remove('selected');});
    bonusModal.classList.add('open');bonusModal.setAttribute('aria-hidden','false');
  }
  function closeBonusBuy(){
    if(bonusActive)return;
    bonusModal.classList.remove('open');bonusModal.setAttribute('aria-hidden','true');selectedBuy=null;
  }
  function renderBuyConfirmation(key){
    var cfg=BUY_MODES[key]; if(!cfg)return;
    selectedBuy=key; bonusCards.forEach(function(c){c.classList.toggle('selected',c.getAttribute('data-mode')===key);});
    confirmName.textContent=cfg.name; confirmCost.textContent=money(BET*cfg.costMult);
    confirmBuy.disabled=BALANCE<BET*cfg.costMult; confirmBuy.textContent=confirmBuy.disabled?'INSUFFICIENT BALANCE':'CONFIRM PURCHASE';
    buyConfirm.hidden=false;
  }

  function chooseModifiers(cfg){
    var result=[];
    cfg.mods.forEach(function(m){
      if(m!=='random'){result.push(m);return;}
      var pool=MODIFIERS.filter(function(x){return result.indexOf(x)<0;});
      result.push(choice(pool));
    });
    return result;
  }

  function startBonus(key){
    var cfg=BUY_MODES[key]; if(!cfg)return;
    var cost=BET*cfg.costMult;
    if(BALANCE<cost){showMessage('INSUFFICIENT BALANCE',1500);renderBuyConfirmation(key);return;}
    BALANCE-=cost; updateHUD();
    bonusModal.classList.remove('open');bonusModal.setAttribute('aria-hidden','true');
    bonusActive=true;bonusEnding=false;bonusMode=cfg;bonusSpins=cfg.spins;bonusMultiplier=cfg.startMult;bonusTotal=0;bonusSpecialRate=cfg.specialRate;bonusMods=chooseModifiers(cfg);
    if(key==='backroom') bonusSpecialRate=.78;
    setBaseControlsLocked(true);stopAutoplay();updateHUD();
    var modText=bonusMods.length?' · '+bonusMods.map(modifierLabel).join(' + '):'';
    splash('ACCESS GRANTED · '+cfg.name+modText,1200);
    setTimeout(spin,turbo?500:1250);
  }

  function endBonus(){
    if(!bonusActive||bonusEnding)return;
    bonusEnding=true;
    var total=bonusTotal,modeName=bonusMode.name;
    splash(modeName+' COMPLETE · '+money(total),1500);
    setTimeout(function(){
      bonusActive=false;bonusEnding=false;bonusMode=null;bonusSpins=0;bonusMultiplier=1;bonusMods=[];bonusTotal=0;
      setBaseControlsLocked(false);updateHUD();spinBtn.disabled=false;
    },turbo?800:1600);
  }

  spinBtn.addEventListener('click',function(){ if(!bonusActive)spin(); });
  minusBtn.addEventListener('click',function(){shiftBet(-1);});
  plusBtn.addEventListener('click',function(){shiftBet(1);});
  turboBtn.addEventListener('click',function(e){turbo=!turbo;e.currentTarget.classList.toggle('active',turbo);});
  autoBtn.addEventListener('click',function(){if(bonusActive)return;if(autoplay)stopAutoplay();else startAutoplay();});
  menuBtn.addEventListener('click',function(){if(bonusActive)return;modalEl.classList.add('open');modalEl.setAttribute('aria-hidden','false');});
  modalClose.addEventListener('click',closeModal);
  modalEl.addEventListener('click',function(e){if(e.target===modalEl)closeModal();});
  function closeModal(){modalEl.classList.remove('open');modalEl.setAttribute('aria-hidden','true');}

  buyBtn.addEventListener('click',openBonusBuy);
  bonusClose.addEventListener('click',closeBonusBuy);
  bonusModal.addEventListener('click',function(e){if(e.target===bonusModal)closeBonusBuy();});
  bonusCards.forEach(function(card){card.addEventListener('click',function(){renderBuyConfirmation(card.getAttribute('data-mode'));});});
  confirmBuy.addEventListener('click',function(){if(selectedBuy)startBonus(selectedBuy);});

  document.addEventListener('keydown',function(e){
    var modalOpen=modalEl.classList.contains('open')||bonusModal.classList.contains('open');
    if(e.code==='Escape'){if(modalEl.classList.contains('open'))closeModal();if(bonusModal.classList.contains('open'))closeBonusBuy();}
    if(e.code==='Space'&&!modalOpen&&!spinning&&!bonusActive){e.preventDefault();if(autoplay)stopAutoplay();spin();}
    if(!modalOpen&&!bonusActive&&(e.key==='ArrowLeft'||e.key==='-')){e.preventDefault();shiftBet(-1);}
    if(!modalOpen&&!bonusActive&&(e.key==='ArrowRight'||e.key==='+'||e.key==='=')){e.preventDefault();shiftBet(1);}
    if(!modalOpen&&!bonusActive&&(e.key==='b'||e.key==='B'))openBonusBuy();
  });

  drawBoard(INITIAL_TILES,true);updateHUD();gridEl.classList.remove('spinning');
})();