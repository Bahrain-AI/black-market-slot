/* BLACK MARKET — reference-matched audience demo
 * Self-contained: no external runtime dependencies.
 * All outcomes are local demo results only.
 */
(function () {
  'use strict';

  var SYMBOLS = ['watch', 'diamond', 'ace', 'gold', 'cash', 'passport', 'bag', 'bust', 'wild', 'vip'];

  // Reference initial board (row-major, 5x4)
  var INITIAL_BOARD = [
    'watch', 'diamond', 'ace', 'gold', 'cash',
    'passport', 'bag', 'bust', 'wild', 'vip',
    'gold', 'cash', 'watch', 'diamond', 'passport',
    'bust', 'wild', 'vip', 'bag', 'ace'
  ];

  // Per-cell tiles cropped straight from the reference — used for the idle board
  // so the opening screen matches the reference image exactly (each cell is the
  // actual artwork instance shown in the reference, not a generic symbol reuse).
  var INITIAL_TILES = [
    'tile-00-watch',     'tile-01-diamond', 'tile-02-ace',  'tile-03-gold',   'tile-04-cash',
    'tile-05-passport',  'tile-06-bag',     'tile-07-bust', 'tile-08-wild',   'tile-09-vip',
    'tile-10-gold',      'tile-11-cash',    'tile-12-watch','tile-13-diamond','tile-14-passport',
    'tile-15-bust',      'tile-16-wild',    'tile-17-vip', 'tile-18-bag',    'tile-19-ace'
  ];

  var BALANCE = 991.30;
  var BET = 1.00;
  var BET_STEPS = [0.10, 0.20, 0.50, 1, 2, 5, 10];

  var spinBtn = document.getElementById('btnSpin');
  var minusBtn = document.getElementById('btnMinus');
  var plusBtn = document.getElementById('btnPlus');
  var turboBtn = document.getElementById('btnTurbo');
  var autoBtn = document.getElementById('btnAutoplay');
  var menuBtn = document.getElementById('btnMenu');
  var balanceEl = document.getElementById('balance');
  var betEl = document.getElementById('bet');
  var gridEl = document.getElementById('reelGrid');
  var messageEl = document.getElementById('message');
  var modalEl = document.getElementById('modal');
  var modalClose = document.getElementById('modalClose');

  var board = INITIAL_BOARD.slice();
  var cells = [];
  var spinning = false;
  var turbo = false;
  var autoplay = false;
  var autoplaySpins = 0;
  var messageTimer = null;

  function money(v) {
    return '$' + v.toFixed(2);
  }

  function cssVar(name, value) {
    var s = document.documentElement.style;
    if (value === undefined) {
      return s.getPropertyValue(name).trim();
    }
    s.setProperty(name, value);
  }

  function drawBoard(grid, areTiles) {
    gridEl.innerHTML = '';
    cells = [];
    var imgBase = areTiles ? './assets/tiles/' : './assets/symbols/';
    grid.forEach(function (sym) {
      var d = document.createElement('div');
      d.className = 'cell';
      var img = document.createElement('img');
      img.src = imgBase + sym + '.webp';
      img.alt = sym;
      img.draggable = false;
      d.appendChild(img);
      gridEl.appendChild(d);
      cells.push(d);
    });
  }

  function updateHUD() {
    balanceEl.textContent = money(BALANCE);
    betEl.textContent = money(BET);
  }

  // Symbol pick: low-key weighted, WILD rarer (matches demo feel, not production math)
  function pick() {
    var r = Math.random();
    if (r < 0.05) return 'wild';
    var pool = SYMBOLS.filter(function (s) { return s !== 'wild'; });
    return pool[Math.floor(Math.random() * pool.length)];
  }

  // Win evaluation: 3/4/5-of-a-kind on each row and each column, WILD substitutes.
  function evaluate(grid) {
    var won = {};
    var mult = 0;

    function line(ids) {
      for (var i = 0; i < SYMBOLS.length; i++) {
        var s = SYMBOLS[i];
        if (s === 'wild') continue;
        var matches = ids.filter(function (idx) {
          return grid[idx] === s || grid[idx] === 'wild';
        });
        if (matches.length >= 3) {
          matches.forEach(function (idx) { won[idx] = true; });
          mult += matches.length === 5 ? 8 : (matches.length === 4 ? 4 : 1.5);
        }
      }
    }

    // 4 rows, indices r*5+0..4
    for (var r = 0; r < 4; r++) {
      line([r * 5 + 0, r * 5 + 1, r * 5 + 2, r * 5 + 3, r * 5 + 4]);
    }
    // 5 columns, indices 0..3 + c*1
    for (var c = 0; c < 5; c++) {
      line([c, 5 + c, 10 + c, 15 + c]);
    }
    return { won: won, mult: mult };
  }

  function showMessage(text, duration) {
    if (messageTimer) clearTimeout(messageTimer);
    messageEl.textContent = text;
    messageEl.classList.add('show');
    messageTimer = setTimeout(function () {
      messageEl.classList.remove('show');
    }, duration || 1300);
  }

  function clearHighlights() {
    cells.forEach(function (c) { c.classList.remove('win'); });
  }

  function finishSpin(nextGrid) {
    gridEl.classList.remove('spinning');
    drawBoard(nextGrid, false);
    board = nextGrid;

    var result = evaluate(board);
    var win = BET * result.mult;

    if (win > 0 && BALANCE - BET >= 0) {
      BALANCE += win;
      Object.keys(result.won).forEach(function (idx) {
        cells[Number(idx)] && cells[Number(idx)].classList.add('win');
      });
      showMessage('WIN ' + money(win) + ' · ' + (result.mult).toFixed(1) + '\u00D7', 1600);
    }
    updateHUD();
    spinning = false;
    spinBtn.disabled = false;
    spinBtn.classList.remove('spinning');
  }

  function settleAutoplay() {
    if (!autoplay) return;
    if (autoplaySpins > 0) autoplaySpins--;
    if (autoplaySpins <= 0 || BALANCE < BET) {
      stopAutoplay();
      return;
    }
    setTimeout(spin, 350);
  }

  function startAutoplay() {
    if (spinning || autoplay) return;
    if (BALANCE < BET) {
      showMessage('INSUFFICIENT BALANCE', 1400);
      return;
    }
    autoplay = true;
    autoplaySpins = 10;
    autoBtn.classList.add('active');
    autoBtn.textContent = 'AUTO \u00B7 ' + autoplaySpins;
    spin();
  }

  function stopAutoplay(fromClick) {
    autoplay = false;
    autoplaySpins = 0;
    autoBtn.classList.remove('active');
    autoBtn.textContent = 'AUTOPLAY';
    if (!fromClick) return;
  }

  function spin() {
    if (spinning) return;
    if (BALANCE < BET) {
      showMessage('INSUFFICIENT BALANCE', 1400);
      stopAutoplay();
      return;
    }
    spinning = true;
    clearHighlights();
    spinBtn.disabled = true;
    spinBtn.classList.add('spinning');

    BALANCE -= BET;
    updateHUD();

    gridEl.classList.add('spinning');
    var duration = turbo ? 320 : 900;

    // Generate the next grid
    var nextGrid;
    setTimeout(function () {
      nextGrid = Array.from({ length: 20 }, pick);
      finishSpin(nextGrid);
      settleAutoplay();
    }, duration);
  }

  function shiftBet(delta) {
    if (spinning) return;
    var idx = BET_STEPS.indexOf(BET);
    if (idx < 0) idx = 3;
    BET = BET_STEPS[Math.max(0, Math.min(BET_STEPS.length - 1, idx + delta))];
    updateHUD();
  }

  // --- Wiring ---
  spinBtn.addEventListener('click', spin);
  minusBtn.addEventListener('click', function () { shiftBet(-1); });
  plusBtn.addEventListener('click', function () { shiftBet(1); });

  turboBtn.addEventListener('click', function (e) {
    turbo = !turbo;
    e.currentTarget.classList.toggle('active', turbo);
  });

  autoBtn.addEventListener('click', function () {
    if (autoplay) {
      stopAutoplay(true);
    } else {
      startAutoplay();
    }
  });

  menuBtn.addEventListener('click', function () {
    modalEl.classList.add('open');
    modalEl.setAttribute('aria-hidden', 'false');
  });
  modalClose.addEventListener('click', closeModal);
  modalEl.addEventListener('click', function (e) {
    if (e.target === modalEl) closeModal();
  });
  function closeModal() {
    modalEl.classList.remove('open');
    modalEl.setAttribute('aria-hidden', 'true');
  }

  document.addEventListener('keydown', function (e) {
    if (e.code === 'Space' && !modalEl.classList.contains('open') && !spinning) {
      e.preventDefault();
      if (autoplay) { stopAutoplay(true); }
      spin();
    }
    // +/- / arrow bet control
    if (e.key === 'ArrowLeft' || e.key === '-') { e.preventDefault(); shiftBet(-1); }
    if (e.key === 'ArrowRight' || e.key === '+' || e.key === '=') { e.preventDefault(); shiftBet(1); }
  });

  // Initial render — per-cell tiles match the reference board exactly
  drawBoard(INITIAL_TILES, true);
  updateHUD();
  gridEl.classList.remove('spinning');
})();