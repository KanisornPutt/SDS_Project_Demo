// get DOM child
const fileInput = document.getElementById("file-input");
const browseBtn = document.getElementById("browse-btn");
const uploadText = document.getElementById("upload-text");
const uploadBox = document.getElementById("upload-box");
const cloudIcon = document.getElementById("cloud-upload");
const buttons = document.getElementById("convert-group");
const cancelButton = document.getElementById("cancel");
const addButton = document.getElementById("add");
const convertButton = document.getElementById("convert");

// API Gateway URL - change this to your gateway address
const API_GATEWAY = 'http://localhost:3000';

// Store the current file
let currentFile = null;

// reset to first state
function resetUploadBox() {
  browseBtn.classList.remove("hidden");
  buttons.classList.add("hidden");
  fileInput.value = "";
  uploadText.classList.remove("hidden");
  cloudIcon.classList.remove("hidden");
  currentFile = null;
  const fileContent = document.getElementById("file-content");
  if (fileContent) fileContent.remove();
  lucide.createIcons();
}

browseBtn.addEventListener("click", () => fileInput.click());

// # Add file event
fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (file) {
    // Validate file type
    if (!file.name.endsWith('.ipynb')) {
      alert('Please select a .ipynb file');
      return;
    }

    // Store file for later upload
    currentFile = file;

    // 1. add upload file box
    const newUploadBox = `
          
            <div
      class="bg-white flex flex-row justify-center items-center gap-30 px-6 py-5 rounded-lg border-2 border-yellow-900 
      hover:bg-slate-100 active:bg-slate-200 transition-all duration-150"
      id="file-content"
    >
      <div class="flex flex-row justify-center items-center gap-3">
        <div class="relative inline-block">
          <i data-lucide="file" class="w-10 h-10 text-gray-700"></i>
          <div
            class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
           bg-red-400 text-white text-[10px] px-1 rounded"
          >
            ipynb
          </div>
        </div>

        <div id="file-text" class="flex flex-col justify-center">
          <h3 class="font-semibold">${file.name}</h3>
          <p id="file-upload-text" class="text-sm font-medium opacity-50">file uploaded (${formatFileSize(file.size)})</p>
        </div>
      </div>

      <i data-lucide="trash-2" id="trash-btn" class="text-yellow-900 hover:text-yellow-950 active:text-black"></i>
    </div>
          `;
    uploadBox.insertAdjacentHTML("beforeend", newUploadBox);

    // 2.1 hide unused components
    cloudIcon.classList.add("hidden");
    browseBtn.classList.add("hidden");
    uploadText.classList.add("hidden");

    // 2.2 call to action button
    buttons.classList.remove("hidden");
    convertButton.classList.remove("hidden");
    addButton.classList.add("hidden");

    // [Open File Event]
    const fileContent = document.getElementById("file-content");
    fileContent.addEventListener("click", () => {
      const fileURL = URL.createObjectURL(file);
      window.open(fileURL);
    });

    lucide.createIcons();

    // [Cancel Event]
    const trashBtn = document.getElementById("trash-btn");
    trashBtn.addEventListener("click", (event) => {
      event.stopPropagation();
      resetUploadBox();
    });
  }
});

// [Cancel Event]
cancelButton.addEventListener("click", () => {
  resetUploadBox();
});

// # Convert file event with API integration
convertButton.addEventListener("click", async () => {
  if (!currentFile) {
    alert('No file selected');
    return;
  }

  convertButton.classList.add("hidden");

  // get file box element
  const text = document.getElementById("file-upload-text");
  const fileText = document.getElementById("file-text");
  if (text) text.remove();

  // 1. add progress bar
  const progressBarHTML = `
<div class="w-64 h-3 bg-[#D9D9D9] rounded relative" id="progress-container">
  <div id="progress-bar" class="h-full w-0 bg-[#98B893] rounded transition-all"></div>
  <span id="progress-text" class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2 text-sm font-semibold text-white">0%</span>
</div>`;
  fileText.insertAdjacentHTML("beforeend", progressBarHTML);

  const progressBar = document.getElementById("progress-bar");
  const progressText = document.getElementById("progress-text");
  const progressContainer = document.getElementById("progress-container");

  try {
    // 2. Upload file to API Gateway
    const formData = new FormData();
    formData.append('file', currentFile);

    // Start progress animation
    let width = 0;
    const progressInterval = setInterval(() => {
      if (width < 90) { // Stop at 90%, finish when response arrives
        width += 2;
        progressBar.style.width = width + "%";
        progressText.textContent = width + "%";
      }
    }, 100);

    console.log('📤 Uploading to:', `${API_GATEWAY}/convert`);

    const response = await fetch(`${API_GATEWAY}/convert`, {
      method: 'POST',
      body: formData
    });

    clearInterval(progressInterval);

    if (!response.ok) {
      throw new Error(`Conversion failed: ${response.status} ${response.statusText}`);
    }

    // Complete progress
    progressBar.style.width = "100%";
    progressText.textContent = "100%";

    // 3. Download PDF
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentFile.name.replace('.ipynb', '.pdf');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);

    console.log('✅ PDF downloaded successfully');

    // 4. Update UI - conversion done
    setTimeout(() => {
      progressContainer.remove();
      fileText.insertAdjacentHTML(
        "beforeend",
        `<p id="file-upload-text" class="text-sm font-medium opacity-50">✅ converting done - PDF downloaded</p>`
      );
      addButton.classList.remove("hidden");
    }, 500);

  } catch (error) {
    console.error('❌ Conversion error:', error);
    
    // Show error in UI
    progressContainer.remove();
    fileText.insertAdjacentHTML(
      "beforeend",
      `<p id="file-upload-text" class="text-sm font-medium text-red-600">❌ Error: ${error.message}</p>`
    );
    
    // Show convert button again to retry
    convertButton.classList.remove("hidden");
    
    alert(`Conversion failed: ${error.message}\n\nMake sure the API Gateway is running at ${API_GATEWAY}`);
  }
});

// [Add Another File Event]
addButton.addEventListener("click", () => {
  resetUploadBox();
});

// Helper function to format file size
function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}