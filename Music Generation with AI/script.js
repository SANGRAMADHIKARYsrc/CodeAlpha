function generateMusic() {
  const btn = document.getElementById('generateBtn');
  btn.disabled = true;
  btn.innerText = "Generating... 🎶";

  fetch('/generate', { method: 'POST' })
    .then(res => res.blob())
    .then(blob => {
      const url = URL.createObjectURL(blob);
      const audio = document.getElementById('musicPlayer');
      const download = document.getElementById('downloadLink');

      audio.src = url;
      download.href = url;
      audio.classList.remove('hidden');
      download.classList.remove('hidden');

      btn.disabled = false;
      btn.innerText = "🎼 Generate Music";
    })
    .catch(() => {
      alert("Music generation failed.");
      btn.disabled = false;
      btn.innerText = "🎼 Generate Music";
    });
}
