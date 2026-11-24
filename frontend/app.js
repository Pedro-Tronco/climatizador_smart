(() => {
  "use strict";

  const VALID_TABS = ["tempo-real", "historico", "resumo"];

  const STATUS_META = {
    INITIALIZING: {
      label: "Inicializando",
      description: "Aguardando primeira leitura dos sensores do Arduino.",
      led: "Branco",
    },
    OK: {
      label: "Operando Normalmente",
      description: "Sensores 1 e 2 ativos.",
      led: "Verde",
    },
    WARNING: {
      label: "Atenção",
      description: "Apenas um sensor está ativo.",
      led: "Azul",
    },
    DISABLED: {
      label: "Desativado",
      description: "Sensores 1 e 2 inativos.",
      led: "Vermelho",
    },
  };

  const state = {
    currentStatus: "INITIALIZING",
    lastUpdated: null,
    occurrences: [], // sorted newest-first
    filteredOccurrences: [],
    wsState: "connecting",
    activeTab: "tempo-real",
    filterStatus: "ALL",
    serverFilterTimestamp: "",
    reconnectAttempts: 0,
    reconnectTimer: null,
    ws: null,
  };

  const dom = {
    tabButtons: Array.from(document.querySelectorAll(".tab-btn")),
    tabPanels: {
      "tempo-real": document.getElementById("tab-tempo-real"),
      historico: document.getElementById("tab-historico"),
      resumo: document.getElementById("tab-resumo"),
    },
    wsIndicator: document.getElementById("ws-indicator"),
    wsLabel: document.getElementById("ws-label"),

    liveCard: document.getElementById("live-status-card"),
    liveStatusLabel: document.getElementById("live-status-label"),
    liveStatusCode: document.getElementById("live-status-code"),
    liveStatusDesc: document.getElementById("live-status-desc"),
    liveLastUpdated: document.getElementById("live-last-updated"),
    liveElapsed: document.getElementById("live-elapsed"),
    liveFeedList: document.getElementById("live-feed-list"),
    liveFeedEmpty: document.getElementById("live-feed-empty"),
    btnFullscreen: document.getElementById("btn-fullscreen"),

    filterForm: document.getElementById("history-filter-form"),
    filterStatus: document.getElementById("filter-status"),
    filterTimestamp: document.getElementById("filter-timestamp"),
    btnClear: document.getElementById("btn-clear"),
    btnRefresh: document.getElementById("btn-refresh"),
    btnExportCsv: document.getElementById("btn-export-csv"),
    historyCount: document.getElementById("history-count"),
    historyError: document.getElementById("history-error"),
    historyTbody: document.getElementById("history-tbody"),
    historyEmpty: document.getElementById("history-empty"),

    kpiTotal: document.getElementById("kpi-total"),
    kpiOkCount: document.getElementById("kpi-ok-count"),
    kpiOkPct: document.getElementById("kpi-ok-pct"),
    kpiWarningCount: document.getElementById("kpi-warning-count"),
    kpiWarningPct: document.getElementById("kpi-warning-pct"),
    kpiDisabledCount: document.getElementById("kpi-disabled-count"),
    kpiDisabledPct: document.getElementById("kpi-disabled-pct"),

    barOk: document.getElementById("bar-ok"),
    barOkLabel: document.getElementById("bar-ok-label"),
    barWarning: document.getElementById("bar-warning"),
    barWarningLabel: document.getElementById("bar-warning-label"),
    barDisabled: document.getElementById("bar-disabled"),
    barDisabledLabel: document.getElementById("bar-disabled-label"),
    barInitializing: document.getElementById("bar-initializing"),
    barInitializingLabel: document.getElementById("bar-initializing-label"),

    timelineStrip: document.getElementById("timeline-strip"),
    timelineEmpty: document.getElementById("timeline-empty"),
  };

  function isValidStatus(status) {
    return Object.prototype.hasOwnProperty.call(STATUS_META, status);
  }

  function getStatusMeta(status) {
    return STATUS_META[isValidStatus(status) ? status : "INITIALIZING"];
  }

  function formatDateTime(isoString) {
    if (!isoString) return "—";
    const date = new Date(isoString);
    if (Number.isNaN(date.getTime())) return isoString;
    return date.toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  }

  function formatElapsed(isoString) {
    if (!isoString) return "—";
    const ms = Date.now() - Date.parse(isoString);
    if (Number.isNaN(ms) || ms < 0) return "agora";
    const seconds = Math.floor(ms / 1000);
    if (seconds < 60) return `há ${seconds} s`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `há ${minutes} min`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `há ${hours} h`;
    const days = Math.floor(hours / 24);
    return `há ${days} d`;
  }

  function sortAndDedupeOccurrences(items) {
    const byTimestamp = new Map();
    for (const item of items) {
      if (item && item.timestamp && isValidStatus(item.type)) {
        byTimestamp.set(item.timestamp, {
          timestamp: item.timestamp,
          type: item.type,
        });
      }
    }
    return Array.from(byTimestamp.values()).sort(
      (a, b) => Date.parse(b.timestamp) - Date.parse(a.timestamp)
    );
  }

  function mergeOccurrences(existing, incoming) {
    return sortAndDedupeOccurrences([...existing, ...incoming]);
  }

  /* ---- Tabs & Hash Routing ---- */

  function getTabFromHash() {
    const raw = window.location.hash.replace(/^#/, "").trim();
    return VALID_TABS.includes(raw) ? raw : "tempo-real";
  }

  function setActiveTab(tabName, updateHash = true) {
    const target = VALID_TABS.includes(tabName) ? tabName : "tempo-real";
    state.activeTab = target;

    for (const btn of dom.tabButtons) {
      const isSelected = btn.dataset.tab === target;
      btn.classList.toggle("is-active", isSelected);
      btn.setAttribute("aria-selected", String(isSelected));
    }

    for (const [key, panel] of Object.entries(dom.tabPanels)) {
      const isMatch = key === target;
      panel.hidden = !isMatch;
      panel.classList.toggle("is-active", isMatch);
    }

    if (updateHash && window.location.hash !== `#${target}`) {
      window.location.hash = target;
    }
  }

  /* ---- Rendering ---- */

  function renderWsIndicator() {
    const labels = {
      connecting: "Conectando...",
      connected: "Conectado",
      reconnecting: "Reconectando...",
      disconnected: "Desconectado",
    };
    dom.wsIndicator.dataset.ws = state.wsState;
    dom.wsLabel.textContent = labels[state.wsState] || "Desconectado";
  }

  function renderLivePanel() {
    const status = isValidStatus(state.currentStatus)
      ? state.currentStatus
      : "INITIALIZING";
    const meta = getStatusMeta(status);

    dom.liveCard.dataset.status = status;
    dom.liveStatusLabel.textContent = meta.label;
    dom.liveStatusCode.textContent = status;
    dom.liveStatusDesc.textContent = meta.description;
    dom.liveLastUpdated.textContent = formatDateTime(state.lastUpdated);
    dom.liveElapsed.textContent = formatElapsed(state.lastUpdated);

    const recent = state.occurrences.slice(0, 10);
    dom.liveFeedList.replaceChildren();
    dom.liveFeedEmpty.hidden = recent.length > 0;

    for (const item of recent) {
      const itemMeta = getStatusMeta(item.type);
      const li = document.createElement("li");
      li.className = "feed-item";
      li.dataset.status = item.type;

      const main = document.createElement("div");
      main.className = "feed-item-main";

      const badge = document.createElement("span");
      badge.className = "status-badge";
      badge.textContent = item.type;

      const label = document.createElement("span");
      label.textContent = itemMeta.label;

      const time = document.createElement("span");
      time.className = "feed-item-time";
      time.textContent = formatDateTime(item.timestamp);

      main.append(badge, label);
      li.append(main, time);
      dom.liveFeedList.appendChild(li);
    }
  }

  function applyHistoryClientFilter() {
    const base = state.serverFilterTimestamp
      ? state.occurrences.filter(
          (item) =>
            Date.parse(item.timestamp) > Date.parse(state.serverFilterTimestamp)
        )
      : state.occurrences;

    state.filteredOccurrences =
      state.filterStatus === "ALL"
        ? base
        : base.filter((item) => item.type === state.filterStatus);
  }

  function renderHistoryTable() {
    applyHistoryClientFilter();

    const rows = state.filteredOccurrences;
    dom.historyCount.textContent = `${rows.length} ${
      rows.length === 1 ? "ocorrência exibida" : "ocorrências exibidas"
    }`;
    dom.historyTbody.replaceChildren();
    dom.historyEmpty.hidden = rows.length > 0;

    const fragment = document.createDocumentFragment();
    for (const item of rows) {
      const meta = getStatusMeta(item.type);
      const tr = document.createElement("tr");

      const tdTime = document.createElement("td");
      tdTime.className = "mono";
      tdTime.textContent = formatDateTime(item.timestamp);

      const tdStatus = document.createElement("td");
      const badge = document.createElement("span");
      badge.className = "status-badge";
      badge.dataset.status = item.type;
      badge.textContent = item.type;
      tdStatus.appendChild(badge);

      const tdDesc = document.createElement("td");
      tdDesc.textContent = `${meta.label} — ${meta.description}`;

      tr.append(tdTime, tdStatus, tdDesc);
      fragment.appendChild(tr);
    }

    dom.historyTbody.appendChild(fragment);
  }

  function renderSummary() {
    const total = state.occurrences.length;
    const counts = {
      OK: 0,
      WARNING: 0,
      DISABLED: 0,
      INITIALIZING: 0,
    };

    for (const item of state.occurrences) {
      if (Object.prototype.hasOwnProperty.call(counts, item.type)) {
        counts[item.type] += 1;
      }
    }

    const pct = (count) =>
      total === 0 ? "0%" : `${((count / total) * 100).toFixed(1)}%`;

    dom.kpiTotal.textContent = String(total);
    dom.kpiOkCount.textContent = String(counts.OK);
    dom.kpiOkPct.textContent = pct(counts.OK);
    dom.kpiWarningCount.textContent = String(counts.WARNING);
    dom.kpiWarningPct.textContent = pct(counts.WARNING);
    dom.kpiDisabledCount.textContent = String(counts.DISABLED);
    dom.kpiDisabledPct.textContent = pct(counts.DISABLED);

    const setBar = (fillEl, labelEl, count) => {
      const width = total === 0 ? 0 : (count / total) * 100;
      fillEl.style.width = `${width.toFixed(1)}%`;
      labelEl.textContent = `${count} (${pct(count)})`;
    };

    setBar(dom.barOk, dom.barOkLabel, counts.OK);
    setBar(dom.barWarning, dom.barWarningLabel, counts.WARNING);
    setBar(dom.barDisabled, dom.barDisabledLabel, counts.DISABLED);
    setBar(dom.barInitializing, dom.barInitializingLabel, counts.INITIALIZING);

    const timelineItems = state.occurrences.slice(0, 50).reverse();
    dom.timelineStrip.replaceChildren();
    dom.timelineEmpty.hidden = timelineItems.length > 0;

    for (const item of timelineItems) {
      const block = document.createElement("div");
      block.className = "timeline-block";
      block.dataset.status = item.type;
      block.title = `${item.type} em ${formatDateTime(item.timestamp)}`;
      dom.timelineStrip.appendChild(block);
    }
  }

  function renderAll() {
    renderWsIndicator();
    renderLivePanel();
    renderHistoryTable();
    renderSummary();
  }

  /* ---- REST API ---- */

  function showHistoryError(message) {
    if (!message) {
      dom.historyError.hidden = true;
      dom.historyError.textContent = "";
    } else {
      dom.historyError.hidden = false;
      dom.historyError.textContent = message;
    }
  }

  async function fetchOccurrences(timestamp = "") {
    const query = timestamp
      ? `?timestamp=${encodeURIComponent(timestamp)}`
      : "";
    const response = await fetch(`/api/occurrences${query}`, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) {
      throw new Error(`Erro HTTP ${response.status} ao buscar ocorrências`);
    }
    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error("Formato inválido retornado por /api/occurrences");
    }
    return data;
  }

  async function loadInitialOccurrences() {
    try {
      showHistoryError("");
      const data = await fetchOccurrences();
      state.occurrences = sortAndDedupeOccurrences(data);

      if (state.occurrences.length > 0) {
        state.currentStatus = state.occurrences[0].type;
        state.lastUpdated = state.occurrences[0].timestamp;
      } else {
        state.currentStatus = "INITIALIZING";
        state.lastUpdated = null;
      }
      renderAll();
    } catch (err) {
      showHistoryError(
        err instanceof Error ? err.message : "Falha ao carregar histórico."
      );
    }
  }

  async function syncNewOccurrences(fallbackStatus = null) {
    try {
      const latestTs =
        state.occurrences.length > 0 ? state.occurrences[0].timestamp : "";
      const fresh = await fetchOccurrences(latestTs);

      if (fresh.length > 0) {
        state.occurrences = mergeOccurrences(state.occurrences, fresh);
        state.currentStatus = state.occurrences[0].type;
        state.lastUpdated = state.occurrences[0].timestamp;
      } else if (fallbackStatus && isValidStatus(fallbackStatus)) {
        const nowIso = new Date().toISOString();
        state.occurrences = mergeOccurrences(state.occurrences, [
          { timestamp: nowIso, type: fallbackStatus },
        ]);
        state.lastUpdated = nowIso;
      }
      showHistoryError("");
      renderAll();
    } catch (_err) {
      if (fallbackStatus && isValidStatus(fallbackStatus)) {
        const nowIso = new Date().toISOString();
        state.occurrences = mergeOccurrences(state.occurrences, [
          { timestamp: nowIso, type: fallbackStatus },
        ]);
        state.lastUpdated = nowIso;
        renderAll();
      }
    }
  }

  async function handleHistoryFilterSubmit(event) {
    event.preventDefault();
    state.filterStatus = dom.filterStatus.value;
    state.serverFilterTimestamp = dom.filterTimestamp.value.trim();

    try {
      showHistoryError("");
      const data = await fetchOccurrences(state.serverFilterTimestamp);
      if (!state.serverFilterTimestamp) {
        state.occurrences = sortAndDedupeOccurrences(data);
      } else {
        state.occurrences = mergeOccurrences(state.occurrences, data);
      }
      renderHistoryTable();
    } catch (err) {
      showHistoryError(
        err instanceof Error ? err.message : "Falha ao filtrar histórico."
      );
    }
  }

  function exportHistoryCsv() {
    applyHistoryClientFilter();
    const rows = state.filteredOccurrences;
    const header = ["timestamp", "status", "descricao"];
    const csvLines = [header.join(",")];

    for (const row of rows) {
      const meta = getStatusMeta(row.type);
      const escapeCsv = (val) => `"${String(val).replace(/"/g, '""')}"`;
      csvLines.push(
        [
          escapeCsv(row.timestamp),
          escapeCsv(row.type),
          escapeCsv(`${meta.label} - ${meta.description}`),
        ].join(",")
      );
    }

    const blob = new Blob(["\uFEFF" + csvLines.join("\n")], {
      type: "text/csv;charset=utf-8;",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "ocorrencias-climatizador.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /* ---- WebSocket ---- */

  function getWebSocketUrl() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${window.location.host}/ws`;
  }

  function scheduleReconnect() {
    if (state.reconnectTimer !== null) return;
    const delayMs = Math.min(15000, 1000 * Math.pow(2, state.reconnectAttempts));
    state.reconnectAttempts += 1;
    state.wsState = "reconnecting";
    renderWsIndicator();

    state.reconnectTimer = window.setTimeout(() => {
      state.reconnectTimer = null;
      connectWebSocket();
    }, delayMs);
  }

  function connectWebSocket() {
    if (
      state.ws &&
      (state.ws.readyState === WebSocket.OPEN ||
        state.ws.readyState === WebSocket.CONNECTING)
    ) {
      return;
    }

    state.wsState =
      state.reconnectAttempts > 0 ? "reconnecting" : "connecting";
    renderWsIndicator();

    const ws = new WebSocket(getWebSocketUrl());
    state.ws = ws;

    ws.addEventListener("open", () => {
      state.reconnectAttempts = 0;
      state.wsState = "connected";
      renderWsIndicator();
    });

    ws.addEventListener("message", (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload && isValidStatus(payload.current_status)) {
          state.currentStatus = payload.current_status;
          state.lastUpdated = new Date().toISOString();
          renderLivePanel();
          void syncNewOccurrences(payload.current_status);
        }
      } catch (_err) {
        // Ignore malformed frames
      }
    });

    ws.addEventListener("close", () => {
      state.ws = null;
      state.wsState = "disconnected";
      renderWsIndicator();
      scheduleReconnect();
    });

    ws.addEventListener("error", () => {
      // Close event will trigger reconnection
    });
  }

  /* ---- Fullscreen ---- */

  function updateFullscreenButton() {
    if (!dom.btnFullscreen) return;
    const supported = Boolean(document.documentElement.requestFullscreen);
    dom.btnFullscreen.hidden = !supported;
    if (supported) {
      dom.btnFullscreen.textContent = document.fullscreenElement
        ? "Sair da Tela Cheia"
        : "Tela Cheia";
    }
  }

  async function toggleFullscreen() {
    try {
      if (!document.fullscreenElement) {
        await document.documentElement.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch (_err) {
      // Ignore fullscreen denial
    } finally {
      updateFullscreenButton();
    }
  }

  /* ---- Init ---- */

  function bindEvents() {
    for (const btn of dom.tabButtons) {
      btn.addEventListener("click", () => {
        setActiveTab(btn.dataset.tab, true);
      });
    }

    window.addEventListener("hashchange", () => {
      setActiveTab(getTabFromHash(), false);
    });

    dom.filterForm.addEventListener("submit", handleHistoryFilterSubmit);

    dom.btnClear.addEventListener("click", () => {
      dom.filterStatus.value = "ALL";
      dom.filterTimestamp.value = "";
      state.filterStatus = "ALL";
      state.serverFilterTimestamp = "";
      void loadInitialOccurrences();
    });

    dom.btnRefresh.addEventListener("click", () => {
      if (state.serverFilterTimestamp) {
        dom.filterForm.requestSubmit();
      } else {
        void loadInitialOccurrences();
      }
    });

    dom.btnExportCsv.addEventListener("click", exportHistoryCsv);
    dom.btnFullscreen.addEventListener("click", toggleFullscreen);
    document.addEventListener("fullscreenchange", updateFullscreenButton);
  }

  function init() {
    setActiveTab(getTabFromHash(), false);
    bindEvents();
    updateFullscreenButton();
    renderAll();

    void loadInitialOccurrences();
    connectWebSocket();

    window.setInterval(() => {
      dom.liveElapsed.textContent = formatElapsed(state.lastUpdated);
    }, 1000);
  }

  init();
})();
