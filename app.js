const form = document.querySelector("#query-form");
const statusMessage = document.querySelector("#form-status");

function setStatus(message, isError = false) {
  statusMessage.textContent = message;
  statusMessage.style.color = isError ? "#9b3d4f" : "#126c6a";
}

form?.addEventListener("submit", async (event) => {
  event.preventDefault();
  setStatus("Sending...");

  const payload = Object.fromEntries(new FormData(form).entries());

  try {
    const response = await fetch("/api/queries", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Request failed");
    }

    const result = await response.json();
    form.reset();
    setStatus(
      result.email_sent
        ? "Thanks. Your message has been sent."
        : "Thanks. Your message was saved, but email is not configured yet."
    );
  } catch (error) {
    setStatus("Start the Python server to submit queries locally.", true);
  }
});
