const API_BASE_URL = "https://ai-code-reviewer-wwqb.onrender.com";

export async function submitCodeReview(code, language = "python") {
  const response = await fetch(`${API_BASE_URL}/api/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(
      errorData.detail || `Server responded with status ${response.status}`
    );
  }

  return response.json();
}