document.addEventListener('DOMContentLoaded', () => {
    // Form elements
    const form = document.getElementById('video-trigger-form');
    const promptInput = document.getElementById('prompt-input');
    const negPromptInput = document.getElementById('neg-prompt-input');
    const framesInput = document.getElementById('frames-input');
    const framesVal = document.getElementById('frames-val');
    const stepsInput = document.getElementById('steps-input');
    const stepsVal = document.getElementById('steps-val');
    const resolutionSelect = document.getElementById('resolution-select');
    const cfgInput = document.getElementById('cfg-input');
    const cfgVal = document.getElementById('cfg-val');
    const seedInput = document.getElementById('seed-input');
    const triggerBtn = document.getElementById('trigger-btn');

    // UI Feedback elements
    const activeBadge = document.getElementById('active-job-badge');
    const progressContainer = document.getElementById('progress-container');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressStatusLabel = document.getElementById('progress-status-label');
    const progressPctLabel = document.getElementById('progress-pct-label');
    const metaJobId = document.getElementById('meta-job-id');
    const metaPromptId = document.getElementById('meta-prompt-id');
    const previewPlaceholder = document.getElementById('preview-placeholder');
    const videoPlayer = document.getElementById('output-video-player');
    const recentJobsList = document.getElementById('recent-jobs-list');
    const refreshJobsBtn = document.getElementById('refresh-jobs-btn');

    let currentPollingTimer = null;

    // Sliders dynamic updates
    framesInput.addEventListener('input', () => { framesVal.textContent = framesInput.value; });
    stepsInput.addEventListener('input', () => { stepsVal.textContent = stepsInput.value; });
    cfgInput.addEventListener('input', () => { cfgVal.textContent = parseFloat(cfgInput.value).toFixed(1); });

    // Handle Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const [widthStr, heightStr] = resolutionSelect.value.split('x');
        const seedValue = parseInt(seedInput.value, 10);

        const payload = {
            prompt: promptInput.value.trim(),
            negativePrompt: negPromptInput.value.trim(),
            frames: parseInt(framesInput.value, 10),
            steps: parseInt(stepsInput.value, 10),
            width: parseInt(widthStr, 10),
            height: parseInt(heightStr, 10),
            cfgScale: parseFloat(cfgInput.value),
            seed: seedValue > 0 ? seedValue : null
        };

        try {
            triggerBtn.disabled = true;
            triggerBtn.innerHTML = '<span>Initiating Run...</span>';
            setStatus('QUEUED', 'Submitting to pipeline...');

            const response = await fetch('/api/v1/videos/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || errorData.title || 'Pipeline trigger failed');
            }

            const initialJob = await response.json();
            metaJobId.textContent = initialJob.jobId;
            metaPromptId.textContent = initialJob.promptId || 'Pending Queue...';

            progressContainer.classList.remove('hidden');
            previewPlaceholder.classList.remove('hidden');
            videoPlayer.classList.add('hidden');

            startPolling(initialJob.jobId);
            fetchRecentJobs();

        } catch (err) {
            console.error('Trigger Error:', err);
            alert('Failed to trigger generation: ' + err.message);
            setStatus('FAILED', err.message);
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = '<span class="btn-icon">⚡</span><span>Launch Pipeline Run</span>';
        }
    });

    // Poll job status
    function startPolling(jobId) {
        if (currentPollingTimer) clearInterval(currentPollingTimer);

        let progressPct = 10;
        progressBarFill.style.width = `${progressPct}%`;
        progressPctLabel.textContent = `${progressPct}%`;

        currentPollingTimer = setInterval(async () => {
            try {
                const res = await fetch(`/api/v1/videos/jobs/${jobId}`);
                if (!res.ok) return;

                const job = await res.json();
                setStatus(job.status);

                if (job.promptId) {
                    metaPromptId.textContent = job.promptId;
                }

                if (job.status === 'PROCESSING') {
                    if (progressPct < 85) progressPct += 5;
                    progressBarFill.style.width = `${progressPct}%`;
                    progressPctLabel.textContent = `${progressPct}%`;
                    progressStatusLabel.textContent = 'Rendering diffusion frames in ComfyUI...';
                }

                if (job.status === 'COMPLETED') {
                    clearInterval(currentPollingTimer);
                    progressBarFill.style.width = '100%';
                    progressPctLabel.textContent = '100%';
                    progressStatusLabel.textContent = 'Generation finished! Rendering MP4.';

                    triggerBtn.disabled = false;
                    triggerBtn.innerHTML = '<span class="btn-icon">⚡</span><span>Launch Pipeline Run</span>';

                    // Stream output video
                    showRenderedVideo(job.outputFileName);
                    fetchRecentJobs();
                } else if (job.status === 'FAILED') {
                    clearInterval(currentPollingTimer);
                    progressBarFill.style.width = '100%';
                    progressBarFill.style.background = 'var(--error)';
                    progressStatusLabel.textContent = 'Failed: ' + (job.errorDetails || 'Unknown error');

                    triggerBtn.disabled = false;
                    triggerBtn.innerHTML = '<span class="btn-icon">⚡</span><span>Launch Pipeline Run</span>';
                    fetchRecentJobs();
                }
            } catch (pollErr) {
                console.warn('Poll error:', pollErr);
            }
        }, 1200);
    }

    function showRenderedVideo(filename) {
        if (!filename) return;
        previewPlaceholder.classList.add('hidden');
        videoPlayer.classList.remove('hidden');
        videoPlayer.src = `/api/v1/videos/stream/${encodeURIComponent(filename)}`;
        videoPlayer.load();
        videoPlayer.play().catch(e => console.log('Autoplay prevented:', e));
    }

    function setStatus(status, detail) {
        activeBadge.className = 'badge';
        activeBadge.textContent = status;

        switch (status) {
            case 'SUBMITTED':
            case 'QUEUED':
                activeBadge.classList.add('badge-queued');
                progressStatusLabel.textContent = detail || 'Queued in ComfyUI...';
                break;
            case 'PROCESSING':
                activeBadge.classList.add('badge-processing');
                progressStatusLabel.textContent = detail || 'Processing neural workflow...';
                break;
            case 'COMPLETED':
                activeBadge.classList.add('badge-completed');
                break;
            case 'FAILED':
                activeBadge.classList.add('badge-failed');
                break;
            default:
                activeBadge.classList.add('badge-idle');
        }
    }

    async function fetchRecentJobs() {
        try {
            const res = await fetch('/api/v1/videos/jobs');
            if (!res.ok) return;
            const jobs = await res.json();

            if (jobs.length === 0) {
                recentJobsList.innerHTML = '<p class="empty-state">No pipeline runs recorded yet.</p>';
                return;
            }

            recentJobsList.innerHTML = '';
            jobs.forEach(job => {
                const div = document.createElement('div');
                div.className = 'job-card-item';
                div.innerHTML = `
                    <div>
                        <div class="job-item-prompt">${escapeHtml(job.request ? job.request.prompt : 'Custom Prompt')}</div>
                        <div class="job-item-time">${new Date(job.createdAt).toLocaleTimeString()} • ${job.status}</div>
                    </div>
                    <span class="badge ${getBadgeClass(job.status)}">${job.status}</span>
                `;
                div.addEventListener('click', () => {
                    if (job.status === 'COMPLETED' && job.outputFileName) {
                        showRenderedVideo(job.outputFileName);
                        metaJobId.textContent = job.jobId;
                        metaPromptId.textContent = job.promptId || '-';
                        setStatus('COMPLETED');
                    }
                });
                recentJobsList.appendChild(div);
            });
        } catch (e) {
            console.warn('Failed to load recent jobs:', e);
        }
    }

    function getBadgeClass(status) {
        switch (status) {
            case 'COMPLETED': return 'badge-completed';
            case 'PROCESSING': return 'badge-processing';
            case 'QUEUED': return 'badge-queued';
            case 'FAILED': return 'badge-failed';
            default: return 'badge-idle';
        }
    }

    function escapeHtml(str) {
        return str.replace(/[&<>'"]/g, tag => ({
            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
        }[tag] || tag));
    }

    refreshJobsBtn.addEventListener('click', fetchRecentJobs);
    fetchRecentJobs();
});
