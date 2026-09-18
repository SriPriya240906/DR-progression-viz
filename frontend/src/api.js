const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export async function analyzeImage(file) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_BASE_URL}/api/analyze`, { method: "POST", body });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || "The backend could not analyze this image.");
  return payload;
}

export async function downloadReport(analysisId, data) {
  const response = await fetch(`${API_BASE_URL}/api/report/${analysisId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || "The PDF report could not be generated.");
  }
  return response.blob();
}
