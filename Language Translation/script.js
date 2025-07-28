async function translateText() {
  const inputText = document.getElementById("inputText").value.trim();
  const sourceLang = document.getElementById("sourceLang").value;
  const targetLang = document.getElementById("targetLang").value;

  if (!inputText) {
    alert("Please enter text to translate.");
    return;
  }

  try {
    const response = await fetch("https://translate.astian.org/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        q: inputText,
        source: sourceLang,
        target: targetLang,
        format: "text"
      })
    });

    const data = await response.json();
    document.getElementById("outputText").innerText = data.translatedText;
  } catch (error) {
    alert("Translation failed. Please check your internet or try again later.");
    console.error("Translation error:", error);
  }
}

function copyText() {
  const text = document.getElementById("outputText").innerText;
  if (text !== "—") {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  }
}

function speakText() {
  const text = document.getElementById("outputText").innerText;
  if (text !== "—") {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = document.getElementById("targetLang").value;
    speechSynthesis.speak(utterance);
  }
}
