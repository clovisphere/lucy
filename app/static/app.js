// Select key DOM elements
const dragDropArea = document.getElementById("drag-drop-area");
const uploadButton = document.getElementById("upload-button");
const progressBar = document.getElementById("progress-bar");
const progressContainer = document.getElementById("progress-container");
const statusMessage = document.getElementById("status-message");
const responseMessage = document.getElementById("response");

// Initialize variables to hold dropped files
let selectedFiles = [];

// Function to update the status message
const updateStatusMessage = (message, color = "black") => {
  statusMessage.innerText = message;
  statusMessage.style.color = color;
};

// Handle drag over event
dragDropArea.addEventListener("dragover", (event) => {
  event.preventDefault();
  dragDropArea.classList.add("dragover");
});

// Handle drag leave event
dragDropArea.addEventListener("dragleave", () => {
  dragDropArea.classList.remove("dragover");
});

// Handle drop event
dragDropArea.addEventListener("drop", (event) => {
  event.preventDefault();
  dragDropArea.classList.remove("dragover");

  // Filter for PDF files
  selectedFiles = Array.from(event.dataTransfer.files).filter(
    (file) => file.type === "application/pdf",
  );

  if (selectedFiles.length > 0) {
    // Enable the upload button
    uploadButton.disabled = false;
    // Provide feedback to the user
    updateStatusMessage(
      `${selectedFiles.length} PDF file(s) ready to upload.`,
      "green",
    );
  } else {
    updateStatusMessage("Please upload only PDF files.", "red");
  }
});

// Handle the upload button click
uploadButton.addEventListener("click", async () => {
  if (selectedFiles.length === 0) {
    updateStatusMessage("No files to upload!", "red");
    return;
  }

  // Prepare FormData with the selected files
  const formData = new FormData();
  selectedFiles.forEach((file) => formData.append("files", file));

  // Show the progress bar
  progressContainer.style.display = "block";
  updateStatusMessage("Uploading files...", "black");

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/upload");

  // Update the progress bar during upload
  xhr.upload.onprogress = (event) => {
    if (event.lengthComputable) {
      const percent = (event.loaded / event.total) * 100;
      progressBar.value = percent;
    }
  };

  // Handle the response after upload
  xhr.onload = () => {
    if (xhr.status === 201) {
      responseMessage.innerText = "Files uploaded successfully!";
      responseMessage.style.color = "#67ACC7";
      updateStatusMessage("Upload complete!", "green");
    } else {
      responseMessage.innerText = "Error uploading files!";
      responseMessage.style.color = "#FA7F9E";
      updateStatusMessage("Failed to upload files.", "red");
    }
    // Reset the UI
    resetUI();
  };

  xhr.onerror = () => {
    responseMessage.innerText = "Error uploading files!";
    responseMessage.style.color = "#FA7F9E";
    resetUI();
  };

  // Send the files
  xhr.send(formData);
});

// Reset the progress bar and button state
function resetUI() {
  progressBar.value = 0;
  progressContainer.style.display = "none";
  uploadButton.disabled = true;
  selectedFiles = [];
}

// Start with the upload button disabled
window.onload = () => {
  uploadButton.disabled = true;
};
