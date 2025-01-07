// Function to handle (multi) file (.pdf) upload
document.getElementById("upload-button").addEventListener("click", async () => {
  const files = document.getElementById("file-input").files;
  const formData = new FormData();

  for (let file of files) {
    formData.append("files", file);
  }

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      throw new Error(`an error occurred: ${response}`);
    }
    // No need to diplay what was uploaded 😅
  } catch (error) {
    console.error(`-> an error occurred: ${error}`);
  }
});
