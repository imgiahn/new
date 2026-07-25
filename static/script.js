const form = document.getElementById("search-form");
const input = document.getElementById("search-input");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const recommendEl = document.getElementById("recommend");
const chipsEl = document.getElementById("recommend-chips");

// 추천 키워드 로드 → 칩 렌더링
loadRecommendations();

async function loadRecommendations() {
  try {
    const resp = await fetch("/api/recommendations");
    const data = await resp.json();
    chipsEl.innerHTML = data.keywords
      .map((k) => `<button type="button" class="chip">${escapeHtml(k)}</button>`)
      .join("");
    chipsEl.querySelectorAll(".chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        input.value = btn.textContent;
        runSearch(btn.textContent);
      });
    });
  } catch (err) {
    recommendEl.style.display = "none";
  }
}

form.addEventListener("submit", (e) => {
  e.preventDefault();
  runSearch(input.value.trim());
});

async function runSearch(query) {
  query = (query || "").trim();
  if (!query) return;

  statusEl.textContent = "검색 중...";
  resultsEl.innerHTML = "";

  try {
    const resp = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
    const data = await resp.json();

    if (!resp.ok) {
      statusEl.textContent = data.error || "오류가 발생했습니다.";
      return;
    }

    if (!data.results.length) {
      statusEl.textContent = "검색 결과가 없습니다.";
      return;
    }

    statusEl.textContent = "";
    render(data.results);
  } catch (err) {
    statusEl.textContent = "네트워크 오류가 발생했습니다.";
  }
}

function render(results) {
  resultsEl.innerHTML = results
    .map((v) => {
      const meta = [v.views, v.published].filter(Boolean).join(" · ");
      const badge = v.length
        ? `<span class="badge">${escapeHtml(v.length)}</span>`
        : "";
      return `
    <a class="card" href="${v.url}" target="_blank" rel="noopener">
      <div class="thumb-wrap">
        <img src="${v.thumbnail}" alt="${escapeHtml(v.title)}" loading="lazy" />
        ${badge}
      </div>
      <div class="card-body">
        <div class="card-title">${escapeHtml(v.title)}</div>
        <div class="card-meta">${escapeHtml(v.channel)}</div>
        ${meta ? `<div class="card-meta">${escapeHtml(meta)}</div>` : ""}
      </div>
    </a>`;
    })
    .join("");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
