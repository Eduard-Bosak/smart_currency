// ==========================================
// CURRENCY ARBITRAGE CALCULATOR LOGIC (TypeScript)
// ==========================================

interface CountryRates {
    nbg: number;
    street: number;
    direct: number;
    eur_usd: number;
    usd_local: number;
}

interface CountryProfile {
    name: string;
    flag: string;
    city: string;
    local_currency: string;
    local_symbol: string;
    central_bank: string;
    central_bank_full: string;
    central_bank_api: string;
    street_exchange: string;
    default_rates: CountryRates;
}

// 1. Country Profiles Data (17 Countries)
const COUNTRY_PROFILES: Record<string, CountryProfile> = {
    // ===== ОСНОВНЫЕ СТРАНЫ =====
    georgia: {
        name: "Грузия", flag: "🇬🇪", city: "Тбилиси",
        local_currency: "GEL", local_symbol: "₾",
        central_bank: "НБГ", central_bank_full: "Национальный Банк Грузии",
        central_bank_api: "https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json",
        street_exchange: "Valuto/Rico",
        default_rates: { nbg: 3.16, street: 3.14, direct: 3.02, eur_usd: 1.175, usd_local: 2.67 }
    },
    serbia: {
        name: "Сербия", flag: "🇷🇸", city: "Белград",
        local_currency: "RSD", local_symbol: "дин",
        central_bank: "НБС", central_bank_full: "Народный Банк Сербии",
        central_bank_api: "https://nbs.rs/", street_exchange: "Menjačnica",
        default_rates: { nbg: 117.0, street: 116.5, direct: 115.0, eur_usd: 1.175, usd_local: 108.0 }
    },
    albania: {
        name: "Албания", flag: "🇦🇱", city: "Тирана",
        local_currency: "ALL", local_symbol: "L",
        central_bank: "БА", central_bank_full: "Банк Албании",
        central_bank_api: "", street_exchange: "Këmbim Valutor",
        default_rates: { nbg: 100.0, street: 99.0, direct: 97.0, eur_usd: 1.175, usd_local: 93.0 }
    },
    turkey: {
        name: "Турция", flag: "🇹🇷", city: "Стамбул",
        local_currency: "TRY", local_symbol: "₺",
        central_bank: "TCMB", central_bank_full: "ЦБ Турции",
        central_bank_api: "https://tcmb.gov.tr/", street_exchange: "Döviz Bürosu",
        default_rates: { nbg: 35.0, street: 34.8, direct: 34.0, eur_usd: 1.175, usd_local: 32.5 }
    },
    
    // ===== ЕВРОСОЮЗ (ЕС) =====
    poland: {
        name: "Польша", flag: "🇵🇱", city: "Варшава",
        local_currency: "PLN", local_symbol: "zł",
        central_bank: "НБП", central_bank_full: "НБ Польши",
        central_bank_api: "https://nbp.pl/", street_exchange: "Kantor",
        default_rates: { nbg: 4.3, street: 4.25, direct: 4.15, eur_usd: 1.175, usd_local: 4.0 }
    },
    czechia: {
        name: "Чехия", flag: "🇨🇿", city: "Прага",
        local_currency: "CZK", local_symbol: "Kč",
        central_bank: "ЧНБ", central_bank_full: "ЧНБ",
        central_bank_api: "https://cnb.cz/", street_exchange: "Směnárna",
        default_rates: { nbg: 25.3, street: 25.0, direct: 24.5, eur_usd: 1.175, usd_local: 23.5 }
    },
    hungary: {
        name: "Венгрия", flag: "🇭🇺", city: "Будапешт",
        local_currency: "HUF", local_symbol: "Ft",
        central_bank: "МНБ", central_bank_full: "НБ Венгрии",
        central_bank_api: "https://mnb.hu/", street_exchange: "Pénzváltó",
        default_rates: { nbg: 395.0, street: 390.0, direct: 380.0, eur_usd: 1.175, usd_local: 365.0 }
    },
    romania: {
        name: "Румыния", flag: "🇷🇴", city: "Бухарест",
        local_currency: "RON", local_symbol: "lei",
        central_bank: "НБР", central_bank_full: "НБ Румынии",
        central_bank_api: "https://bnr.ro/", street_exchange: "Casa de Schimb",
        default_rates: { nbg: 4.97, street: 4.92, direct: 4.85, eur_usd: 1.175, usd_local: 4.6 }
    },
    bulgaria: {
        name: "Болгария", flag: "🇧🇬", city: "София",
        local_currency: "BGN", local_symbol: "лв",
        central_bank: "БНБ", central_bank_full: "БНБ",
        central_bank_api: "https://bnb.bg/", street_exchange: "Обменно бюро",
        default_rates: { nbg: 1.96, street: 1.94, direct: 1.90, eur_usd: 1.175, usd_local: 1.81 }
    }
};

// 2. State App
let currentCountryKey = 'georgia';
let currentCountry = COUNTRY_PROFILES[currentCountryKey];

// 3. Selectors
interface DOMSelectors {
    themeBtn: HTMLElement;
    countrySelect: HTMLSelectElement;
    currentFlag: HTMLImageElement;
    autoRatesBtn: HTMLButtonElement;
    apiStatusBoard: HTMLElement | null;
    
    spendAmount: HTMLInputElement;
    nbgRate: HTMLInputElement;
    
    directRecv: HTMLInputElement;
    directSpent: HTMLInputElement;
    directRate: HTMLInputElement;
    
    transferFeePct: HTMLInputElement;
    eurUsdRate: HTMLInputElement;
    usdGelRate: HTMLInputElement;
    
    atmFeePct: HTMLInputElement;
    atmFeeFix: HTMLInputElement;
    streetRate: HTMLInputElement;
    
    labelCentralBank: HTMLElement;
    labelStreetExchange: HTMLElement;
    localCurrencySpans: NodeListOf<HTMLElement>;
    
    resultsTbody: HTMLElement;
    chartContainer: HTMLElement;
    
    bannerWrapper: HTMLElement;
    bannerIcon: HTMLElement;
    bannerTitle: HTMLElement;
    bannerSubtitle: HTMLElement;
    bannerSavings: HTMLElement;
}

// Use a getter for DOM to satisfy TypeScript after loaded
let DOM: DOMSelectors;

// 4. Initialization
function initApp() {
    DOM = {
        themeBtn: document.getElementById('theme-toggle') as HTMLElement,
        countrySelect: document.getElementById('country-select') as HTMLSelectElement,
        currentFlag: document.getElementById('current-flag') as HTMLImageElement,
        autoRatesBtn: document.getElementById('auto-rates-btn') as HTMLButtonElement,
        apiStatusBoard: document.getElementById('api-status-board'), // Can be null
        
        spendAmount: document.getElementById('spend-amount') as HTMLInputElement,
        nbgRate: document.getElementById('nbg-rate') as HTMLInputElement,
        
        directRecv: document.getElementById('direct-recv') as HTMLInputElement,
        directSpent: document.getElementById('direct-spent') as HTMLInputElement,
        directRate: document.getElementById('direct-rate') as HTMLInputElement,
        
        transferFeePct: document.getElementById('transfer-fee-pct') as HTMLInputElement,
        eurUsdRate: document.getElementById('eur-usd-rate') as HTMLInputElement,
        usdGelRate: document.getElementById('usd-gel-rate') as HTMLInputElement,
        
        atmFeePct: document.getElementById('atm-fee-pct') as HTMLInputElement,
        atmFeeFix: document.getElementById('atm-fee-fix') as HTMLInputElement,
        streetRate: document.getElementById('street-rate') as HTMLInputElement,
        
        labelCentralBank: document.getElementById('label-central-bank') as HTMLElement,
        labelStreetExchange: document.getElementById('label-street-exchange') as HTMLElement,
        localCurrencySpans: document.querySelectorAll('.local-currency') as NodeListOf<HTMLElement>,
        
        resultsTbody: document.getElementById('results-tbody') as HTMLElement,
        chartContainer: document.getElementById('chart-container') as HTMLElement,
        
        bannerWrapper: document.getElementById('winner-banner') as HTMLElement,
        bannerIcon: document.getElementById('banner-icon') as HTMLElement,
        bannerTitle: document.getElementById('banner-title') as HTMLElement,
        bannerSubtitle: document.getElementById('banner-subtitle') as HTMLElement,
        bannerSavings: document.getElementById('banner-savings-value') as HTMLElement
    };

    // Populate countries dropdown
    for (const [key, profile] of Object.entries(COUNTRY_PROFILES)) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = profile.name;
        DOM.countrySelect.appendChild(option);
    }
    
    // Setup listeners
    DOM.countrySelect.addEventListener('change', (e: Event) => changeCountry((e.target as HTMLSelectElement).value));
    DOM.themeBtn.addEventListener('click', toggleTheme);
    DOM.autoRatesBtn.addEventListener('click', fetchAllRates);
    
    // Listen to all inputs for live calculation
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('input', () => {
            if(input.id === 'direct-recv' || input.id === 'direct-spent') {
                updateImpliedDirectRate();
            }
            calculate();
        });
    });

    changeCountry('georgia');
}

// 5. App Logic
function changeCountry(key: string) {
    currentCountryKey = key;
    currentCountry = COUNTRY_PROFILES[key];
    
    // Update UI headers & flags
    DOM.countrySelect.value = key;
    
    // ISO codes mapping for flags
    const flagCodeMap: Record<string, string> = {
        georgia: "ge", armenia: "am", azerbaijan: "az", serbia: "rs",
        albania: "al", north_macedonia: "mk", bosnia: "ba", ukraine: "ua",
        moldova: "md", belarus: "by", russia: "ru", poland: "pl",
        czechia: "cz", hungary: "hu", romania: "ro", bulgaria: "bg",
        turkey: "tr"
    };
    DOM.currentFlag.src = `https://flagcdn.com/24x18/${flagCodeMap[key] || 'un'}.png`;
    
    DOM.labelCentralBank.textContent = `ЭТАЛОН (${currentCountry.central_bank})`;
    DOM.labelStreetExchange.textContent = `МЕТОД 3: Наличные + ${currentCountry.street_exchange}`;
    
    DOM.localCurrencySpans.forEach(span => {
        span.textContent = currentCountry.local_currency;
    });

    // Apply defaults
    const rates = currentCountry.default_rates;
    DOM.nbgRate.value = rates.nbg.toString();
    DOM.streetRate.value = rates.street.toString();
    DOM.directRate.value = rates.direct.toString();
    DOM.eurUsdRate.value = rates.eur_usd.toString();
    DOM.usdGelRate.value = rates.usd_local.toString();

    // Reset direct calc helpers
    DOM.directRecv.value = (100 * rates.direct).toFixed(1);
    DOM.directSpent.value = "100.00";

    calculate();
}

function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.getAttribute('data-theme') === 'dark';
    html.setAttribute('data-theme', isDark ? 'light' : 'dark');
    DOM.themeBtn.innerHTML = isDark ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
}

function updateImpliedDirectRate() {
    const recv = parseFloat(DOM.directRecv.value) || 0;
    const spent = parseFloat(DOM.directSpent.value) || 1;
    if (spent > 0) {
        DOM.directRate.value = (recv / spent).toFixed(4);
    }
}

function calculate() {
    const spendAmount = parseFloat(DOM.spendAmount.value) || 0;
    
    // Reference
    const nbgRate = parseFloat(DOM.nbgRate.value) || 0;
    const nbgResult = spendAmount * nbgRate;

    // Method 1: Direct
    const directRate = parseFloat(DOM.directRate.value) || 0;
    const directResult = spendAmount * directRate;

    // Method 2: Transfer (Fee is subtracted from the top)
    const tFee = parseFloat(DOM.transferFeePct.value) || 0;
    const eUsd = parseFloat(DOM.eurUsdRate.value) || 0;
    const uGel = parseFloat(DOM.usdGelRate.value) || 0;
    const netEurTransfer = spendAmount - (spendAmount * (tFee / 100));
    const transferResult = (netEurTransfer * eUsd) * uGel;

    // Method 3: Cash (Fixed fee and % fee are subtracted from the top)
    const aFeePct = parseFloat(DOM.atmFeePct.value) || 0;
    const aFeeFix = parseFloat(DOM.atmFeeFix.value) || 0;
    const sRate = parseFloat(DOM.streetRate.value) || 0;
    let cashResult = 0;
    if (spendAmount > aFeeFix) {
        // Subtract fixed fee, then subtract % fee on the original principal
        const netEurCash = spendAmount - aFeeFix - (spendAmount * (aFeePct / 100));
        if (netEurCash > 0) {
            cashResult = netEurCash * sRate;
        }
    }

    renderResults({
        amount: spendAmount,
        ref: nbgResult,
        direct: directResult,
        transfer: transferResult,
        cash: cashResult
    });
}

interface ResultsPayload {
    amount: number;
    ref: number;
    direct: number;
    transfer: number;
    cash: number;
}

function renderResults(res: ResultsPayload) {
    const s = currentCountry.local_symbol;
    
    // Calculate losses
    const ref = res.ref;
    const dLoss = ref ? ((res.direct - ref) / ref) * 100 : 0;
    const tLoss = ref ? ((res.transfer - ref) / ref) * 100 : 0;
    const cLoss = ref ? ((res.cash - ref) / ref) * 100 : 0;

    const dLossAbs = ref ? (res.direct - ref) : 0;
    const tLossAbs = ref ? (res.transfer - ref) : 0;
    const cLossAbs = ref ? (res.cash - ref) : 0;

    // Sort to find winners
    const methods = [
        { id: 'direct', name: 'Прямая оплата', val: res.direct, loss: dLoss, lossAbs: dLossAbs, icon: 'fa-credit-card', keyColor: 'red' },
        { id: 'transfer', name: 'Перевод IBT → Credo', val: res.transfer, loss: tLoss, lossAbs: tLossAbs, icon: 'fa-money-bill-transfer', keyColor: 'orange' },
        { id: 'cash', name: `Наличные (${currentCountry.street_exchange})`, val: res.cash, loss: cLoss, lossAbs: cLossAbs, icon: 'fa-money-bill-wave', keyColor: 'green' }
    ];
    
    methods.sort((a, b) => b.val - a.val); // Best first

    // Render Table
    let tableHtml = `<tr class="nbg-row">
        <td><div class="method-name"><i class="fa-solid fa-building-columns"></i> ${currentCountry.central_bank} (Эталон)</div></td>
        <td style="text-align: right">${res.ref.toFixed(2)} ${s}</td>
        <td class="loss-none" style="text-align: right">0.00 ${s} <br><small>(0.00%)</small></td>
    </tr>`;

    methods.forEach((m, idx) => {
        const isWinner = idx === 0;
        const lossClass = m.loss < -2.0 ? 'loss-high' : 'loss-low';
        tableHtml += `
            <tr class="${isWinner ? 'winner-row' : ''} ${m.id}-row">
                <td><div class="method-name"><i class="fa-solid ${m.icon}"></i> ${m.name}</div></td>
                <td style="text-align: right; ${isWinner ? 'color: var(--success);' : ''}">${m.val.toFixed(2)} ${s}</td>
                <td class="loss-value ${lossClass}" style="text-align: right">
                    ${m.lossAbs > 0 ? '+' : ''}${m.lossAbs.toFixed(2)} ${s} <br>
                    <small>(${m.loss > 0 ? '+' : ''}${m.loss.toFixed(2)}%)</small>
                </td>
            </tr>
        `;
    });
    DOM.resultsTbody.innerHTML = tableHtml;

    // Render Chart
    let chartHtml = '';
    const maxVal = Math.max(res.ref, methods[0].val); 

    methods.forEach((m, idx) => {
        const pct = maxVal > 0 ? (m.val / maxVal) * 100 : 0;
        const colorVar = idx === 0 ? 'var(--success)' : (idx === 2 ? 'var(--danger)' : 'var(--warning)');
        const badge = idx === 0 ? '<span class="winner-badge">✓ ЛУЧШИЙ</span>' : '';
        
        chartHtml += `
            <div class="chart-item">
                <div class="chart-header">
                    <div class="chart-title">
                        <i class="fa-solid ${m.icon}"></i>
                        <span>${m.name} ${badge}</span>
                    </div>
                    <div class="chart-value">
                        <span class="chart-val-num" style="color: ${colorVar}">${m.val.toFixed(2)} <span style="font-size:0.8rem">${s}</span></span>
                        <span class="chart-val-sub">${m.loss.toFixed(1)}% от ${currentCountry.central_bank}</span>
                    </div>
                </div>
                <div class="bar-container">
                    <div class="bar-fill" style="width: ${pct}%; background-color: ${colorVar}"></div>
                </div>
            </div>
        `;
    });

    // Reference Bar
    const refPct = maxVal > 0 ? (res.ref / maxVal) * 100 : 0;
    chartHtml += `
        <div class="chart-item" style="border-color: var(--info); background: rgba(14, 165, 233, 0.05);">
            <div class="chart-header">
                <div class="chart-title" style="color: var(--info);">
                    <i class="fa-solid fa-building-columns"></i> ${currentCountry.central_bank}
                </div>
                <div class="chart-value">
                    <span class="chart-val-num" style="color: var(--info);">${res.ref.toFixed(2)} <span style="font-size:0.8rem">${s}</span></span>
                    <span class="chart-val-sub">ЭТАЛОН (100%)</span>
                </div>
            </div>
            <div class="bar-container" style="background: rgba(14, 165, 233, 0.2)">
                <div class="bar-fill" style="width: ${refPct}%; background-color: var(--info)"></div>
            </div>
        </div>
    `;
    DOM.chartContainer.innerHTML = chartHtml;

    // Render Winner Banner
    const winner = methods[0];
    const savings = winner.val - methods[methods.length-1].val; // difference between best and worst
    
    if (winner.id === 'cash') {
        DOM.bannerTitle.textContent = "💵 СНИМАЙТЕ НАЛИЧНЫЕ!";
        DOM.bannerSubtitle.textContent = `Идите в ${currentCountry.street_exchange}. Это выгоднее.`;
        DOM.bannerIcon.textContent = "🏆";
    } else if (winner.id === 'transfer') {
        DOM.bannerTitle.textContent = "📲 ПЕРЕВОДИТЕ В CREDO!";
        DOM.bannerSubtitle.textContent = `Используйте IBT и меняйте внутри.`;
        DOM.bannerIcon.textContent = "📱";
    } else {
        DOM.bannerTitle.textContent = "💳 ПЛАТИТЕ КАРТОЙ IBT";
        DOM.bannerSubtitle.textContent = `Удивительно, но прямая оплата выгоднее всего.`;
        DOM.bannerIcon.textContent = "🤔";
    }
    
    // Optional: show difference vs worst
    if (savings > 0 && res.ref > 0) {
        DOM.bannerSavings.textContent = `+${savings.toFixed(2)} ${s}`;
    } else {
        DOM.bannerSavings.textContent = "";
    }
}

// 6. Ultra-Fast API Fetching mechanism (Promise.any race)
function fetchWithRace(targetUrl: string): Promise<string> {
    const proxies = [
        fetch(`https://api.allorigins.win/raw?url=${encodeURIComponent(targetUrl)}`, { cache: 'no-store' }),
        fetch(`https://corsproxy.io/?${encodeURIComponent(targetUrl)}`, { cache: 'no-store' })
    ];
    
    return Promise.any(proxies).then((res: Response) => {
        if (!res.ok) throw new Error("Status " + res.status);
        return res.text();
    });
}

async function fetchAllRates() {
    const btn = DOM.autoRatesBtn;
    const origText = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Загрузка...';
    btn.disabled = true;

    let updates: string[] = [];
    
    // 1. Cross-Rate EUR/USD
    try {
        const frankResponse = await fetch('https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD', { cache: 'no-store' });
        const frankData = await frankResponse.json();
        if (frankData && frankData.rates && frankData.rates.USD) {
            DOM.eurUsdRate.value = frankData.rates.USD.toFixed(4);
            updates.push(`🌍 Кросс EUR/USD: ${frankData.rates.USD.toFixed(4)}`);
        }
    } catch(e) {
        console.warn('Frankfurter error:', e);
    }

    if (currentCountryKey === 'georgia') {
        // 2. NBG (Central Bank)
        try {
            const nbgText = await fetchWithRace(currentCountry.central_bank_api);
            const nbgData = JSON.parse(nbgText);
            
            let nbgEur = 0; let nbgUsd = 0;
            if (nbgData && nbgData[0] && nbgData[0].currencies) {
                for (let c of nbgData[0].currencies) {
                    if (c.code === 'EUR') nbgEur = c.rate / c.quantity;
                    if (c.code === 'USD') nbgUsd = c.rate / c.quantity;
                }
            }
            if (nbgEur > 0) {
                DOM.nbgRate.value = nbgEur.toFixed(4);
                updates.push(`🏦 НБГ EUR: ${nbgEur.toFixed(4)}`);
            }
        } catch (e) {
            console.error('NBG fetch error:', e);
        }

        // 3. Rico Exchange (HTML scraping)
        try {
            const ricoHtml = await fetchWithRace('https://rico.ge/?lang=en');
            const eurMatch = ricoHtml.match(/EUR[\s\S]*?(\d+\.\d+)/i);
            const usdMatch = ricoHtml.match(/USD[\s\S]*?(\d+\.\d+)/i);

            if (eurMatch && eurMatch[1]) {
                DOM.streetRate.value = parseFloat(eurMatch[1]).toFixed(4);
                updates.push(`💸 Rico EUR: ${eurMatch[1]}`);
            }
            if (usdMatch && usdMatch[1]) {
                DOM.usdGelRate.value = parseFloat(usdMatch[1]).toFixed(4);
                updates.push(`💵 Credo(USD proxy): ${usdMatch[1]}`);
            }
        } catch (e) {
            console.error('Rico fetch error:', e);
        }

    } else {
        showToast(`Авто-стягивание курсов работает только для Грузии. Для ${currentCountry.name} пока нет авто-обновления.`, "warning");
    }

    calculate();
    
    if (updates.length > 0) {
        showToast("Курсы успешно обновлены!<br><small>" + updates.join('<br>') + "</small>", "success");
    } else {
        showToast("Не удалось спарсить курсы", "error");
    }

    btn.innerHTML = origText;
    btn.disabled = false;
}

// Toast notification helper
function showToast(message: string, type: "info" | "success" | "warning" | "error" = "info") {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? 'fa-circle-check' : 
                 type === 'error' ? 'fa-circle-xmark' : 
                 type === 'warning' ? 'fa-triangle-exclamation' : 'fa-circle-info';
                 
    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <div>${message}</div>`;
    container.appendChild(toast);
    
    setTimeout(() => toast.classList.add('show'), 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Start app
document.addEventListener('DOMContentLoaded', initApp);
