# Bonus Buy browser regression checks

Serve the repository root (for example, `python -m http.server 8765`) and open
`http://localhost:8765/demo/index.html`. This static demo needs no build step.

1. At desktop size and 390 x 844, verify a gold BONUS BUY button is visible,
   has a touch target at least 44px high, and opens the BONUS BUY dialog.
   At 844 x 390, verify the button is visible at the upper left.
2. Focus Bonus Buy and press Space. The dialog opens without charging a spin.
   Focus begins on Close; Tab and Shift+Tab remain in the dialog. Escape closes
   it, restores focus to Bonus Buy, and leaves the balance unchanged.
3. Select each option. At a $1 bet, the confirmation shows $60, $100, or $200.
   Confirm each after a fresh reload. The balance immediately becomes $931.30,
   $891.30, or $791.30; the bonus begins with 6, 8, or 10 spins and an initial
   multiplier of x1, x1, or x3. Controls lock during the bonus, then unlock when
   it completes. Turbo can shorten this check. Retriggers may extend it.
4. Raise the bet to $10 and select Black Card. Its $2000 cost exceeds the initial
   balance, and confirmation must be disabled with INSUFFICIENT BALANCE.
5. On mobile, check all cards, selected price, and confirmation fit inside the
   dialog without horizontal overflow. Selection scrolls confirmation into view.
6. Verify all 20 reel cells stay within the reel grid on desktop and mobile.
7. Check browser errors and missing images, and repeat the purchase flow on the
   commit-pinned raw.githack URL after pushing. If the host shows its landing
   screen, choose Open the page.

The original visibility regression was reproduced in the browser: the button
had transparent foreground/background and a 38.875px height at 1280 x 720.
After the fix, the label is opaque and the target is at least 44px high.
