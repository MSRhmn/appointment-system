import { fetchServices, fetchAvailableSlots, bookAppointment } from "./api.js";
import { addMinutesToTime, timeToMinutes } from "./utils.js";

document.addEventListener("DOMContentLoaded", () => {
  const serviceSelect = document.getElementById("service");
  const dateInput = document.getElementById("date");
  const slotsSelect = document.getElementById("time-slot");
  const staffNameDisplay = document.getElementById("assigned-staff");
  const form = document.getElementById("booking-form");
  const nameInput = document.getElementById("customer-name");
  const emailInput = document.getElementById("customer-email");
  const messageDiv = document.getElementById("message");

  let allServices = [];

  fetchServices()
    .then((data) => {
      allServices = data.services; // Save full list for later use
  
      serviceSelect.innerHTML = `<option value="">Select a service</option>`;
      data.services.forEach((service) => {
        const option = document.createElement("option");
        option.value = service.id;
        option.textContent = `${service.name} (${service.duration_minutes} mins, $${service.price})`;
        serviceSelect.appendChild(option);
      });
    })
    .catch((err) => {
      console.error("Error loading services:", err);
    });


  // Fetch available slots
  function loadAvailableSlots() {
    const serviceId = serviceSelect.value;
    const date = dateInput.value;
  
    if (!serviceId || !date) {
      slotsSelect.innerHTML = `<option value="">Choose a service and date first</option>`;
      staffNameDisplay.textContent = "--";
      return;
    }
  
    // Find service info from local list
    const selectedService = allServices.find(s => s.id == serviceId);
    if (!selectedService) {
      console.warn("Service not found in list");
      return;
    }
  
    const totalDuration = selectedService.duration_minutes + (selectedService.buffer_minutes || 0);
  
    fetchAvailableSlots(serviceId, date)
      .then((data) => {
        slotsSelect.innerHTML = "";
  
        if (!data.slots || data.slots.length === 0) {
          slotsSelect.innerHTML = `<option value="">No slots available</option>`;
          staffNameDisplay.textContent = "--";
        } else {
          // Filter slots based on service duration + buffer
          const filteredSlots = [];
          let lastSlotMinutes = -Infinity;
  
          data.slots.forEach((slot) => {
            const currentSlotMinutes = timeToMinutes(slot);
            
            // Check spacing AND availability for full service duration
            if (currentSlotMinutes - lastSlotMinutes >= totalDuration) {
              filteredSlots.push(slot);
              lastSlotMinutes = currentSlotMinutes;
            }
          });

          if (filteredSlots.length === 0) {
            slotsSelect.innerHTML = `<option value="">No suitable slots available for this service</option>`;
            staffNameDisplay.textContent = "--";
          } else {
            filteredSlots.forEach((slot) => {
              const option = document.createElement("option");
              option.value = slot;
              option.textContent = `${slot} — ${addMinutesToTime(slot, selectedService.duration_minutes)} (${selectedService.duration_minutes} mins)`;
              option.dataset.staffId = data.staff.id;
              option.dataset.staffName = data.staff.name;
              slotsSelect.appendChild(option);
            });

            if (data.staff) {
              staffNameDisplay.textContent = data.staff.name;
              slotsSelect.dataset.staffId = data.staff.id;
              slotsSelect.dataset.staffName = data.staff.name;
            }
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching available slots:", error);
      });
  }
 
  serviceSelect.addEventListener("change", loadAvailableSlots);
  dateInput.addEventListener("change", loadAvailableSlots);

  // Show assigned staff on slot selection
  slotsSelect.addEventListener("change", () => {
    const selected = slotsSelect.options[slotsSelect.selectedIndex];
    if (selected && selected.dataset.staffName) {
      staffNameDisplay.textContent = selected.dataset.staffName;
    } else {
      staffNameDisplay.textContent = "--";
    }
  });

  // Submit form
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const selectedSlot = slotsSelect.options[slotsSelect.selectedIndex];
    if (!selectedSlot || !selectedSlot.value) {
      alert("Please select a valid time slot.");
      return;
    }

    const payload = {
      service_id: serviceSelect.value,
      staff_id: selectedSlot.dataset.staffId,
      customer_name: nameInput.value,
      customer_email: emailInput.value,
      date: dateInput.value,
      start_time: selectedSlot.value,
    };

    bookAppointment(payload)
      .then((data) => {
        messageDiv.innerHTML = "";
        if (data.success) {
          messageDiv.innerHTML = `<div class="alert alert-success">🎉 Booking successful! Your booking ID is <strong>${data.booking_id}</strong>.</div>`;
          form.reset();
          staffNameDisplay.textContent = "--";
          slotsSelect.innerHTML = `<option value="">Choose a service and date first</option>`;
        } else {
          messageDiv.innerHTML = `<div class="alert alert-danger">❌ Error: ${data.error}</div>`;
        }
      })
      .catch(() => {
        messageDiv.innerHTML = `<div class="alert alert-danger">❌ Something went wrong. Please try again later.</div>`;
      });
  });
});
