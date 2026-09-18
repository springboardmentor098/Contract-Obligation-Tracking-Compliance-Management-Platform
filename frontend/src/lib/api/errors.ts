import axios from "axios";

export function apiErrorMessage(error: unknown, fallback = "The request could not be completed.") {
  if (!axios.isAxiosError(error)) return error instanceof Error ? error.message : fallback;
  if (!error.response)
    return "Unable to reach the server. Check that the FastAPI service is running.";
  const detail = error.response.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg ?? "Invalid value").join(" ");
  const messages: Record<number, string> = {
    400: "The request was invalid. Please verify the submitted information.",
    401: "Your session has expired or you are unauthorized. Please sign in again.",
    403: "You do not have permission to perform this action.",
    404: "The requested record could not be found.",
    409: "A conflict occurred with an existing record. Please review the details.",
    422: "Some submitted values are invalid. Please check the required fields.",
    500: "The server could not complete the request. Please try again later.",
    502: "Bad gateway. The backend service is temporarily unavailable.",
    503: "Service temporarily unavailable. Please try again shortly.",
  };
  return messages[error.response.status] ?? fallback;
}
