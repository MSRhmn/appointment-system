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

  fetch("/api/services/")
    .then((res) => res.json())
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
  
    fetch(`/api/available-slots/?date=${date}&service_id=${serviceId}`)
      .then((res) => res.json())
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

  // Helper function to convert time string to minutes
  function timeToMinutes(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    return hours * 60 + minutes;
  }

  // Helper function to convert minutes to time string
  function minutesToTime(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
  }

  // Check if service can fit at a specific start time
  function canFitService(availableSlots, startSlot, serviceDurationMinutes) {
    const startMinutes = timeToMinutes(startSlot);
    const slotsNeeded = Math.ceil(serviceDurationMinutes / 5); // 5-minute backend intervals
    
    // Check if we have consecutive 5-minute slots for the entire duration
    for (let i = 0; i < slotsNeeded; i++) {
      const requiredTime = minutesToTime(startMinutes + (i * 5));
      if (!availableSlots.includes(requiredTime)) {
        return false; // Missing a required slot
      }
    }
    return true;
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

    fetch("/api/book-appointment/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
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


function addMinutesToTime(timeStr, minutesToAdd) {
  const [hours, minutes] = timeStr.split(":").map(Number);
  const date = new Date();
  date.setHours(hours, minutes);
  date.setMinutes(date.getMinutes() + minutesToAdd);
  return date.toTimeString().slice(0, 5);
}