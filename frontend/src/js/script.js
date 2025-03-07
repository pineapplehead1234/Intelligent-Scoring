let files = [];
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileList = document.getElementById('fileList');
const submitBtn = document.getElementById('submitBtn');
const standardAnswer = document.getElementById('standardAnswer');

dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#1890ff';
    dropZone.style.backgroundColor = '#f0f7ff';
});
dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '#d9d9d9';
    dropZone.style.backgroundColor = '#fafafa';
});
dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '#d9d9d9';
    dropZone.style.backgroundColor = '#fafafa';
    handleFiles(e.dataTransfer.files);
});

fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
});

function handleFiles(newFiles) {
    Array.from(newFiles).forEach(file => {
        if (file.type === 'audio/mp3' || file.name.endsWith('.mp3')) {
            files.push(file);
            addFileToList(file);
        }
    });
    updateSubmitButton();
}

function addFileToList(file) {
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <div class="file-header">
            <button class="delete-btn" style="background: none; border: none; color: #ff4d4f; cursor: pointer; padding: 4px 8px; font-size: 14px; position: absolute; left: 0; top: 0;">×</button>
            <div class="file-name"><span class="label">文件名：</span>${file.name}</div>
            <div class="file-score"></div>
        </div>
        <div class="file-transcript"><span class="label">转录结果：</span></div>
    `;

    const deleteBtn = fileItem.querySelector('.delete-btn');
    deleteBtn.addEventListener('click', () => {
        const index = Array.from(fileList.children).indexOf(fileItem);
        files.splice(index, 1);
        fileList.removeChild(fileItem);
        updateSubmitButton();
    });

    fileList.appendChild(fileItem);
}

function updateSubmitButton() {
    submitBtn.disabled = files.length === 0 || !standardAnswer.value.trim();
}

standardAnswer.addEventListener('input', updateSubmitButton);

submitBtn.addEventListener('click', async () => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });
    formData.append('standard_answer', standardAnswer.value.trim());

    try {
        submitBtn.disabled = true;
        submitBtn.textContent = '评分中...';
        submitBtn.style.backgroundColor = '#91d5ff';

        const response = await fetch('http://localhost:5000/api/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) throw new Error('评分请求失败');

        const results = await response.json();
        updateScores(results);
    } catch (error) {
        alert('评分失败：' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = '提交评分';
        submitBtn.style.backgroundColor = '';
    }
});

function updateScores(results) {
    const fileItems = fileList.children;
    results.forEach((result, index) => {
        const fileItem = fileItems[index];
        const scoreElement = fileItem.querySelector('.file-score');
        const transcriptElement = fileItem.querySelector('.file-transcript');
        
        const score = result.score * 100;
        let scoreClass = '';
        if (score >= 80) {
            scoreClass = 'high';
        } else if (score >= 50) {
            scoreClass = 'medium';
        } else {
            scoreClass = 'low';
        }
        
        scoreElement.className = `file-score ${scoreClass}`;
        scoreElement.innerHTML = `${score.toFixed(2)}%`;
        transcriptElement.innerHTML = `<span class="label">转录结果：</span>${result.transcript}`;
    });
}