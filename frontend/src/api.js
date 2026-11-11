const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://ai-code-reviewer-wwqb.onrender.com';

export async function submitCodeReview(code) {
  const response = await fetch(`${API_BASE_URL}/api/review`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ code }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}
