const form = document.getElementById('upload-form');
const status = document.getElementById('status');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(form);

  try {
    const uploadResponse = await fetch('/upload', {
      method: 'POST',
      body: formData
    });

    if (uploadResponse.ok) {
      const finetuneResponse = await fetch('/finetuning', {
        method: 'POST',
        body: formData
      }); 
      
      if (finetuneResponse.ok) {
        status.innerText = 'Fine-tuning completed!';
      } else {
        const data = await finetuneResponse.json();
        status.innerText = `Error during fine-tuning: ${data.error}`;
      }
    } else {
      const data = await uploadResponse.json();
      status.innerText = `Error during file upload: ${data.error}`;
    }
  } catch (error) {
    console.error(error);
    status.innerText = 'An error occurred while uploading and finetuning.';
  }
});
