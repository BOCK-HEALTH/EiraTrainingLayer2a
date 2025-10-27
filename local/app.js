// app.js
// This script will make the UI interactive and ready for S3 integration
// For now, it will mock S3 bucket data and show how to fetch and display datasets

const datasets = {
  audio: {
    name: "Audio Dataset",
    mainBucket: "eira1-general-dataset",
    subBucket: "eira1-a2a-ds",
    prefix: "audio/"
  },
  video: {
    name: "Video Dataset",
    mainBucket: "eira1-general-dataset",
    subBucket: "eira1-a2v-ds",
    prefix: "videos/"
  }
};

async function copyDatasetAPI(type) {
  // Call Flask backend to copy dataset
  const token = localStorage.getItem('eira_api_token') || 'changeme';
  try {
    const response = await fetch(`/fetch/${type}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Unknown error');
    }
    const data = await response.json();
    // Show detailed feedback
    let feedback = `<div style='color:#2d3a4b;font-weight:bold;'>Copied <b>${data.copied.length}</b> files to <b>${data.sub_bucket || ''}</b></div>`;
    if (data.copied && data.copied.length > 0) {
      feedback += `<div>Sample files:<ul style='margin:8px 0;'>${data.copied.slice(0,5).map(f => `<li>${f}</li>`).join('')}</ul></div>`;
    }
    return feedback;
  } catch (e) {
    return `Error: ${e.message}`;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Upload TXT file logic
  const uploadForm = document.getElementById('upload-form');
  const uploadFileInput = document.getElementById('upload-file');
  const uploadStatus = document.getElementById('upload-status');
  if (uploadForm && uploadFileInput && uploadStatus) {
    uploadForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const file = uploadFileInput.files[0];
      if (!file || !file.name.endsWith('.txt')) {
        uploadStatus.textContent = 'Please select a .txt file.';
        uploadStatus.style.color = 'red';
        return;
      }
      uploadStatus.textContent = 'Uploading and processing...';
      uploadStatus.style.color = '#3a7bd5';
      const formData = new FormData();
      formData.append('file', file);
      try {
        const response = await fetch('/upload-txt', {
          method: 'POST',
          body: formData
        });
        const data = await response.json();
        if (response.ok) {
          uploadStatus.textContent = data.message;
          uploadStatus.style.color = '#3a7bd5';
        } else {
          uploadStatus.textContent = data.error || 'Upload failed.';
          uploadStatus.style.color = 'red';
        }
      } catch (err) {
        uploadStatus.textContent = 'Error uploading file.';
        uploadStatus.style.color = 'red';
      }
    });
  }

  document.querySelectorAll('.fetch-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const type = btn.getAttribute('data-type');
      const ds = datasets[type];
      const statusDiv = document.getElementById(`status-${type}`);
      btn.disabled = true;
      statusDiv.innerHTML = `<span style='color:#3a7bd5'>Fetching ${ds.name}...</span>`;
      const result = await copyDatasetAPI(type);
      statusDiv.innerHTML = `<b>Result:</b> ${result}`;
      btn.disabled = false;
    });
  });
});

function showFilesModal(title, files) {
  let modal = document.getElementById("files-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "files-modal";
    modal.className = "modal";
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close">&times;</span>
        <h2 id="modal-title"></h2>
        <ul id="modal-files"></ul>
      </div>
    `;
    document.body.appendChild(modal);
    modal.querySelector(".close").onclick = () => {
      modal.style.display = "none";
    };
  }
  modal.querySelector("#modal-title").textContent = title;
  const filesList = modal.querySelector("#modal-files");
  filesList.innerHTML = files.map(f => `<li>${f}</li>`).join("");
  modal.style.display = "block";
}

function updateStatusUI(status) {
  const progressBar = document.getElementById('progress-bar');
  const progressFill = document.getElementById('progress-fill');
  const progressText = document.getElementById('progress-text');
  const logList = document.getElementById('log-list');
  if (!progressBar || !progressFill || !progressText || !logList) return;

  const total = status.total || 0;
  const current = status.current || 0;
  let percent = total ? Math.round((current / total) * 100) : 0;
  progressFill.style.width = percent + '%';
  progressText.textContent = total
    ? `Processed ${current} of ${total} videos (${percent}%)`
    : 'Waiting for extraction...';
  logList.innerHTML = (status.logs || []).map(
    log => `<div style='margin-bottom:6px'>${log}</div>`
  ).join('');
}

function pollStatus() {
  fetch('/status')
    .then(res => res.json())
    .then(updateStatusUI)
    .catch(() => {});
}

setInterval(pollStatus, 3000); // Poll every 3 seconds

// Individual fetch functions for each dataset
async function fetchAudioDataset() {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Fetching...';
  const result = await copyDatasetAPI('audio');
  alert(result.replace(/<[^>]*>/g, '')); // Show result without HTML tags
  btn.disabled = false;
  btn.textContent = 'Fetch Audio Dataset';
}

async function fetchVideoDataset() {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Fetching...';
  const result = await copyDatasetAPI('video');
  alert(result.replace(/<[^>]*>/g, ''));
  btn.disabled = false;
  btn.textContent = 'Fetch Video Dataset';
}

async function fetchImagesTranscriptsDataset() {
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = 'Fetching...';
  const result = await copyDatasetAPI('images-transcripts');
  alert(result.replace(/<[^>]*>/g, ''));
  btn.disabled = false;
  btn.textContent = 'Fetch Images + Transcripts';
}
