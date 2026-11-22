const button = document.getElementById('scan');
const status = document.getElementById('status');
const results = document.getElementById('results');
const count = document.getElementById('count');
const note = document.getElementById('note');

function cell(row, value) {
  const td = document.createElement('td');
  td.textContent = value;
  row.appendChild(td);
}

button.addEventListener('click', async () => {
  button.disabled = true;
  status.textContent = 'Scanning the approved lab host…';
  results.replaceChildren();
  count.textContent = 'Scanning';
  try {
    const response = await fetch('/scan', { method: 'POST' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Scan failed');
    count.textContent = `${data.count} open`;
    status.textContent = `Scan complete for ${data.target}.`;
    note.textContent = data.note;
    if (data.ports.length === 0) {
      const row = results.insertRow();
      const td = row.insertCell();
      td.colSpan = 5;
      td.className = 'empty';
      td.textContent = 'No open ports found among the 20 scanned ports.';
    }
    for (const p of data.ports) {
      const row = results.insertRow();
      cell(row, p.port);
      cell(row, p.protocol.toUpperCase());
      cell(row, 'OPEN');
      cell(row, p.service);
      cell(row, p.version || '—');
    }
  } catch (error) {
    count.textContent = 'Error';
    status.textContent = `Scan failed: ${error.message}`;
    const row = results.insertRow();
    const td = row.insertCell();
    td.colSpan = 5;
    td.className = 'empty';
    td.textContent = 'No results available.';
  } finally { button.disabled = false; }
});
