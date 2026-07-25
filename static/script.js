const form = document.getElementById("search-form");
const input = document.getElementById("search-input");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const query = input.value.trim();
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
});

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
