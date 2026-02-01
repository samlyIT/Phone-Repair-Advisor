// Phone Repair Advisor - Main JavaScript

// Auto-dismiss alerts after 5 seconds
document.addEventListener("DOMContentLoaded", function () {
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 5000);
  });

  // Add fade-in animation to cards
  const cards = document.querySelectorAll(".card");
  cards.forEach(function (card, index) {
    setTimeout(function () {
      card.classList.add("fade-in");
    }, index * 100);
  });
});

// Form validation
function validateDiagnosisForm() {
  const form = document.getElementById("diagnosisForm");
  if (!form) return true;

  const checkboxes = form.querySelectorAll('input[type="checkbox"]');
  const checkedCount = Array.from(checkboxes).filter((cb) => cb.checked).length;

  if (checkedCount === 0) {
    alert("Please select at least one symptom before submitting.");
    return false;
  }

  return true;
}

// Confirm password match
function validatePasswordMatch() {
  const password = document.getElementById("password");
  const confirmPassword = document.getElementById("confirm_password");

  if (password && confirmPassword) {
    if (password.value !== confirmPassword.value) {
      confirmPassword.setCustomValidity("Passwords don't match");
    } else {
      confirmPassword.setCustomValidity("");
    }
  }
}

// Add event listeners for password validation
document.addEventListener("DOMContentLoaded", function () {
  const confirmPassword = document.getElementById("confirm_password");
  if (confirmPassword) {
    confirmPassword.addEventListener("input", validatePasswordMatch);
    document
      .getElementById("password")
      .addEventListener("input", validatePasswordMatch);
  }
});

// Symptom counter
function updateSymptomCount() {
  const checkboxes = document.querySelectorAll(
    '.form-check-input[type="checkbox"]'
  );
  const checkedCount = Array.from(checkboxes).filter((cb) => cb.checked).length;

  const counter = document.getElementById("symptomCounter");
  if (counter) {
    counter.textContent = `${checkedCount} symptom(s) selected`;
  }
}

// Add symptom counter if on diagnosis page
document.addEventListener("DOMContentLoaded", function () {
  const diagnosisForm = document.getElementById("diagnosisForm");
  if (diagnosisForm) {
    // Create counter element
    const counterDiv = document.createElement("div");
    counterDiv.className = "alert alert-info mt-3";
    counterDiv.id = "symptomCounterAlert";
    counterDiv.innerHTML =
      '<i class="bi bi-info-circle"></i> <span id="symptomCounter">0 symptoms selected</span>';

    // Insert before submit button
    const submitButton = diagnosisForm.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.parentElement.insertBefore(counterDiv, submitButton);
    }

    // Add event listeners to checkboxes
    const checkboxes = diagnosisForm.querySelectorAll(
      '.form-check-input[type="checkbox"]'
    );
    checkboxes.forEach(function (checkbox) {
      checkbox.addEventListener("change", updateSymptomCount);
    });
  }
});

// Smooth scroll to top
function scrollToTop() {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  });
}

// Add scroll-to-top button
document.addEventListener("DOMContentLoaded", function () {
  // Create button
  const scrollBtn = document.createElement("button");
  scrollBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  scrollBtn.className =
    "btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle";
  scrollBtn.style.display = "none";
  scrollBtn.style.width = "50px";
  scrollBtn.style.height = "50px";
  scrollBtn.style.zIndex = "1000";
  scrollBtn.onclick = scrollToTop;

  document.body.appendChild(scrollBtn);

  // Show/hide on scroll
  window.addEventListener("scroll", function () {
    if (window.pageYOffset > 300) {
      scrollBtn.style.display = "block";
    } else {
      scrollBtn.style.display = "none";
    }
  });
});

// API Diagnosis Function
async function performAPIDiagnosis(symptoms, phoneBrand, phoneModel) {
  try {
    const response = await fetch("/advisor/api/diagnose", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        symptoms: symptoms,
        phone_brand: phoneBrand,
        phone_model: phoneModel,
      }),
    });

    if (!response.ok) {
      throw new Error("Diagnosis request failed");
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error during diagnosis:", error);
    return null;
  }
}

// Tooltip initialization
document.addEventListener("DOMContentLoaded", function () {
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});

// Copy to clipboard function
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(function () {
    // Show success message
    const toast = document.createElement("div");
    toast.className = "position-fixed top-0 end-0 p-3";
    toast.style.zIndex = "11";
    toast.innerHTML = `
            <div class="toast show" role="alert">
                <div class="toast-header">
                    <i class="bi bi-check-circle text-success me-2"></i>
                    <strong class="me-auto">Success</strong>
                    <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
                </div>
                <div class="toast-body">
                    Copied to clipboard!
                </div>
            </div>
        `;
    document.body.appendChild(toast);
    setTimeout(function () {
      toast.remove();
    }, 3000);
  });
}

// Initialize Select2 if jQuery is available (additional safeguard)
(function () {
  function initSelect2() {
    if (window.jQuery && jQuery().select2) {
      jQuery(".select2").select2({ width: "100%" });
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initSelect2);
  } else {
    initSelect2();
  }
})();

// Print diagnosis result
function printDiagnosis() {
  window.print();
}

// Export diagnosis to PDF (using browser's print to PDF)
function exportDiagnosisPDF() {
  window.print();
}

// Dark mode toggle (optional feature)
function toggleDarkMode() {
  document.body.classList.toggle("dark-mode");
  const isDark = document.body.classList.contains("dark-mode");
  localStorage.setItem("darkMode", isDark);
}

// Load dark mode preference
document.addEventListener("DOMContentLoaded", function () {
  const darkMode = localStorage.getItem("darkMode") === "true";
  if (darkMode) {
    document.body.classList.add("dark-mode");
  }
});

// Console log for debugging
console.log("Phone Repair Advisor Expert System - Loaded Successfully");

// Sticky navbar on scroll
document.addEventListener("scroll", function () {
  const navbar = document.querySelector(.custom-navbar);
  if (window.scrollY > 50) {
    navbar.classList.add(scrolled);
  } else {
    navbar.classList.remove(scrolled);
  }
});

// Sticky navbar on scroll
document.addEventListener("DOMContentLoaded", function () {
  const navbar = document.querySelector(.custom-navbar);
  if (navbar) {
    document.addEventListener("scroll", function () {
      if (window.scrollY > 50) {
        navbar.classList.add(scrolled);
      } else {
        navbar.classList.remove(scrolled);
      }
    });
  }
});
