const form = document.getElementById('scan-form');
const imageInput = document.getElementById('image-input');
const previewWrap = document.getElementById('preview-wrap');
const previewImage = document.getElementById('preview-image');
const uploadLabel = document.getElementById('upload-label');
const resultsPanel = document.getElementById('results-panel');
const queryInput = document.getElementById('query-input');
const submitButton = document.getElementById('submit-button');
const formStatus = document.getElementById('form-status');

const MAX_PREVIEW_BYTES = 8 * 1024 * 1024;
let previewUrl = null;

const fields = {
  productName: document.getElementById('product-name'),
  productCategory: document.getElementById('product-category'),
  productPrice: document.getElementById('product-price'),
  productConfidence: document.getElementById('product-confidence'),
  bestDealPrice: document.getElementById('best-deal-price'),
  bestDealMerchant: document.getElementById('best-deal-merchant'),
  productDescription: document.getElementById('product-description'),
  productMatchNote: document.getElementById('product-match-note'),
  demoNotice: document.getElementById('demo-notice'),
  attributesBox: document.getElementById('attributes-box'),
  onlineList: document.getElementById('online-list'),
  localList: document.getElementById('local-list')
};

imageInput.addEventListener('change', () => {
  const file = imageInput.files[0];
  if (!file) return;

  formStatus.textContent = '';
  if (!file.type.startsWith('image/')) {
    imageInput.value = '';
    uploadLabel.textContent = 'Choose an optional preview image';
    previewWrap.classList.add('hidden');
    formStatus.textContent = 'Please choose an image file.';
    return;
  }

  if (file.size > MAX_PREVIEW_BYTES) {
    imageInput.value = '';
    uploadLabel.textContent = 'Choose an optional preview image';
    previewWrap.classList.add('hidden');
    formStatus.textContent = 'Preview images must be 8 MB or smaller.';
    return;
  }

  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
  }

  uploadLabel.textContent = file.name;
  previewUrl = URL.createObjectURL(file);
  previewImage.src = previewUrl;
  previewWrap.classList.remove('hidden');
});

function renderAttributes(attributes) {
  fields.attributesBox.innerHTML = '';
  Object.entries(attributes || {}).forEach(([key, value]) => {
    const tag = document.createElement('span');
    tag.className = 'attr-tag';
    tag.textContent = `${key}: ${value}`;
    fields.attributesBox.appendChild(tag);
  });
}

function renderList(target, items, accentLabel) {
  target.innerHTML = '';

  if (!items || !items.length) {
    target.innerHTML = '<li class="match-item"><strong>No matches</strong><span>Try a different product or image.</span></li>';
    return;
  }

  items.forEach((item) => {
    const li = document.createElement('li');
    li.className = 'match-item';

    const title = document.createElement('strong');
    title.textContent = `${item.merchant || item.store}`;

    const meta = document.createElement('span');
    meta.textContent = item.distance_miles
      ? `${item.distance_miles} miles away • ${item.inventory}`
      : item.availability;

    const price = document.createElement('div');
    price.textContent = `$${item.total || item.price}`;

    const link = document.createElement('a');
    link.href = item.link;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = `Open ${accentLabel}`;

    li.appendChild(title);
    li.appendChild(meta);
    li.appendChild(price);
    li.appendChild(link);
    target.appendChild(li);
  });
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  const query = queryInput.value.trim();
  formStatus.textContent = 'Loading sample comparison…';
  submitButton.disabled = true;

  try {
    const response = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ query })
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error?.message || 'The demo request failed.');
    }

    const product = data.product;
    const results = data.results;

    fields.productName.textContent = product.name;
    fields.productCategory.textContent = product.category;
    fields.productPrice.textContent = `$${product.price}`;
    fields.productConfidence.textContent = `Confidence: ${(product.confidence * 100).toFixed(0)}%`;
    fields.productDescription.textContent = product.description;
    fields.productMatchNote.textContent = product.match_note;
    fields.demoNotice.textContent = data.demo.notice;
    fields.bestDealPrice.textContent = `$${results.best_online.total}`;
    fields.bestDealMerchant.textContent = `${results.best_online.merchant} • cheapest online`;

    renderAttributes(product.attributes);
    renderList(fields.onlineList, results.online, 'online offer');
    renderList(fields.localList, results.local, 'local listing');

    resultsPanel.classList.remove('hidden');
    formStatus.textContent = 'Sample comparison loaded.';
  } catch (error) {
    console.error(error);
    formStatus.textContent = error.message || 'There was a problem loading the demo. Please try again.';
  } finally {
    submitButton.disabled = false;
  }
});

window.addEventListener('beforeunload', () => {
  if (previewUrl) {
    URL.revokeObjectURL(previewUrl);
  }
});
