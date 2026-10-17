const detectButton = document.getElementById('detectButton');
const runAgainButton = document.getElementById('runAgainButton');
const outputPanel = document.getElementById('outputPanel');
const scanOverlay = document.getElementById('scanOverlay');
const scanText = document.getElementById('scanText');
const scanSubtext = document.getElementById('scanSubtext');
const progressBar = document.getElementById('progressBar');
const progressLabel = document.getElementById('progressLabel');
const statusTitle = document.getElementById('statusTitle');
const statusText = document.getElementById('statusText');
const statusIcon = document.getElementById('statusIcon');
const inputState = document.getElementById('inputState');
const outputState = document.getElementById('outputState');
const outputCaption = document.getElementById('outputCaption');
const connectorProgress = document.getElementById('connectorProgress');
const connectorLabel = document.getElementById('connectorLabel');

let timer;

function resetDemo() {
  window.clearInterval(timer);
  detectButton.disabled = false;
  detectButton.innerHTML = '<span class="button-icon">✦</span> Detect pothole';
  outputPanel.classList.remove('scanning', 'detected');
  progressBar.style.width = '0%';
  progressLabel.textContent = '0%';
  connectorProgress.style.width = '0%';
  connectorLabel.textContent = 'ready to scan';
  inputState.textContent = 'Waiting';
  inputState.className = 'panel-state neutral';
  outputState.textContent = 'Not analyzed';
  outputState.className = 'panel-state';
  statusTitle.textContent = 'Ready to demonstrate';
  statusText.textContent = 'RoadGuard is waiting for a road image to analyze.';
  statusIcon.textContent = '↗';
  statusIcon.style.background = '#dcecf3';
  statusIcon.style.color = '#1775ad';
  scanText.textContent = 'Waiting for input';
  scanSubtext.textContent = 'Press Detect pothole to begin';
  outputCaption.textContent = 'The detector output will appear here.';
}

function runDetection() {
  resetDemo();
  detectButton.disabled = true;
  detectButton.innerHTML = '<span class="button-icon">◌</span> Analyzing image…';
  outputPanel.classList.add('scanning');
  inputState.textContent = 'Captured';
  inputState.className = 'panel-state success';
  outputState.textContent = 'Scanning';
  outputState.className = 'panel-state';
  statusTitle.textContent = 'RoadGuard is analyzing the image';
  statusText.textContent = 'The detector is looking for visible pothole patterns.';
  statusIcon.textContent = '◌';
  statusIcon.style.background = '#d7f6eb';
  statusIcon.style.color = '#189b6d';
  connectorLabel.textContent = 'AI scan in progress';
  connectorProgress.style.width = '15%';

  let progress = 0;
  timer = window.setInterval(() => {
    progress += 2;
    progressBar.style.width = `${progress}%`;
    progressLabel.textContent = `${progress}%`;
    connectorProgress.style.width = `${Math.min(100, progress)}%`;
    if (progress > 25) {
      scanText.textContent = 'Scanning road surface';
      scanSubtext.textContent = 'Comparing visible patterns';
    }
    if (progress > 65) {
      scanText.textContent = 'Preparing review output';
      scanSubtext.textContent = 'Highlighting suspected region';
    }
    if (progress >= 100) {
      window.clearInterval(timer);
      window.setTimeout(showResult, 420);
    }
  }, 52);
}

function showResult() {
  outputPanel.classList.remove('scanning');
  outputPanel.classList.add('detected');
  outputState.textContent = 'Detected';
  outputState.className = 'panel-state success';
  connectorLabel.textContent = 'output ready';
  statusTitle.textContent = 'Pothole detected — review required';
  statusText.textContent = 'The green box marks the region a human inspector should verify next.';
  statusIcon.textContent = '✓';
  statusIcon.style.background = '#d7f6eb';
  statusIcon.style.color = '#189b6d';
  outputCaption.textContent = 'RoadGuard turns the input frame into a focused, reviewable detection output.';
  detectButton.disabled = false;
  detectButton.innerHTML = '<span class="button-icon">↻</span> Run again';
}

detectButton.addEventListener('click', runDetection);
runAgainButton.addEventListener('click', () => {
  document.getElementById('demo').scrollIntoView({ behavior: 'smooth', block: 'start' });
  window.setTimeout(runDetection, 420);
});
resetDemo();
