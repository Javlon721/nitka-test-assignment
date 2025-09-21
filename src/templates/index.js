const API_URL = 'http://127.0.0.1:8000/'; // Replace with your API endpoint
const PAGE_SIZE = 5; // Adjust if your API uses a different size
let offset = 1;


const container = document.getElementById('dataContainer');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

async function fetchData() {
  try {
    const res = await fetch(`${API_URL}?offset=${offset}`);
    const data = await res.json();
    renderCards(data);
    prevBtn.disabled = offset === 1;
    nextBtn.disabled = data.length < PAGE_SIZE;
  } catch (err) {
    console.error('Fetch error:', err);
    container.innerHTML = '<p>Error loading data.</p>';
  }
}

function renderCards(items) {
  container.innerHTML = '';
  if (!items || items.length === 0) {
    container.innerHTML = '<p>No data found.</p>';
    return;
  }

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'card';
    const fields = [
      ['ID', item.id],
      ['Title', item.title],
      ['Summary', item.summary],
      ['Tags', item.tags],
      ['Year Published', item.year_published],
      ['Organization', item.organization],
      ['Country', item.country],
      ['Language', item.language],
      ['PDF Link', `<a href="${item.pdf_link}" target="_blank">Open</a>`],
      ['Local PDF Path', item.local_pdf_path],
      ['Created At', item.created_at],
    ];

    fields.forEach(([label, value]) => {
      const field = document.createElement('div');
      field.className = 'field';
      field.textContent = label;

      const val = document.createElement('div');
      val.className = 'value';
      val.innerHTML = value || '';

      card.appendChild(field);
      card.appendChild(val);
    });

    container.appendChild(card);
  });
}
prevBtn.addEventListener('click', () => {
  offset--;
  fetchData();
});

nextBtn.addEventListener('click', () => {
  offset++;
  fetchData();
});

// Initial load
fetchData();