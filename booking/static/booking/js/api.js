// api.js

export async function fetchServices() {
  const res = await fetch("/api/services/");
  if (!res.ok) throw new Error("Failed to fetch services");
  return await res.json();
}

export async function fetchAvailableSlots(serviceId, date) {
  const res = await fetch(`/api/available-slots/?date=${date}&service_id=${serviceId}`);
  if (!res.ok) throw new Error("Failed to fetch available slots");
  return await res.json();
}

export async function bookAppointment(payload) {
  const res = await fetch("/api/book-appointment/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to book appointment");
  return await res.json();
}
