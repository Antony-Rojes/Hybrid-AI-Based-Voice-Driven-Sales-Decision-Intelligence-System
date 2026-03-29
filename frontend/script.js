async function uploadAudio() {

    const fileInput = document.getElementById("audioFile");
    const file = fileInput.files[0];

    if (!file) {
        alert("Please upload an audio file");
        return;
    }

    document.getElementById("loading").innerText = "Analyzing meeting...";

    const formData = new FormData();
    formData.append("file", file);

    try {

        const response = await fetch("http://localhost:8000/analyze-voice", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("loading").innerText = "";

        document.getElementById("transcript").innerText = data.transcript;
        document.getElementById("prob").innerText = data.closure_probability;
        document.getElementById("strategy").innerText = data.recommended_strategy;
        document.getElementById("risk").innerText = data.risk_level;
        document.getElementById("summary").innerText = data.decision_summary;

    } catch (error) {

        console.error(error);
        document.getElementById("loading").innerText =
            "Error contacting AI server. Check console.";

    }
}