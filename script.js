document.addEventListener("DOMContentLoaded", () => {

  // -------------------------------------------------------
  // EMOJI SELECTION
  // -------------------------------------------------------
  const emojiOptions = document.querySelectorAll(".emoji-option");
  const moodInput = document.getElementById("mood");

  emojiOptions.forEach(emoji => {
    emoji.addEventListener("click", () => {

      // remove all
      emojiOptions.forEach(e => e.classList.remove("selected"));

      // add selected
      emoji.classList.add("selected");

      // update hidden mood value
      moodInput.value = emoji.dataset.value;
    });
  });

  // DEFAULT emoji = 😐 (mood = 60)
  document.querySelector(".emoji-option[data-value='60']").classList.add("selected");



  // -------------------------------------------------------
  // FORM SUBMIT + STRESS INDICATOR LOGIC
  // -------------------------------------------------------
  const form = document.getElementById("stress-form");
  const scoreEl = document.getElementById("stress-score");
  const interventionEl = document.getElementById("intervention-text");
  const resultCard = document.getElementById("result-card");
  const errorMessage = document.getElementById("error-message");

  const marker = document.getElementById("indicator-marker");
  const category = document.getElementById("stress-category");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    errorMessage.classList.add("hidden");
    resultCard.classList.add("hidden");

    // Read values
    const mood = parseInt(moodInput.value);
    const screen = parseFloat(document.getElementById("screen_time").value);
    const typing = parseInt(document.getElementById("typing_speed").value);

    try {
      // ---- Call Backend ----
      const response = await fetch("http://127.0.0.1:8000/stress", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mood: mood,
          screen_time: screen,
          typing_speed: typing
        })
      });

      const data = await response.json();
      const avgStress = data.stress_score; // backend score

      // ---- Update UI ----
      scoreEl.textContent = avgStress;
      interventionEl.textContent = data.intervention;

      // ---- 🔥 MOVE INDICATOR ----
      marker.style.left = `${avgStress}%`;

      // ---- Category Text ----
      if (avgStress < 25) category.textContent = "Low Stress — you’re doing great!";
      else if (avgStress < 50) category.textContent = "Normal Stress — totally fine.";
      else if (avgStress < 75) category.textContent = "Moderate Stress — take a short break.";
      else category.textContent = "High Stress — consider resting soon.";

      // show result card
      resultCard.classList.remove("hidden");

    } catch (err) {
      console.error(err);
      errorMessage.textContent = "Backend not responding!";
      errorMessage.classList.remove("hidden");
    }
  });
});


const screenTimeInput = document.getElementById("screen_time");
const screenTimeValue = document.getElementById("screen_time_value");

screenTimeInput.addEventListener("input", () => {
  screenTimeValue.textContent = screenTimeInput.value;
});
