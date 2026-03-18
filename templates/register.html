{% extends "base.html" %}
{% block title %}Register – Smart Attendance{% endblock %}
{% block content %}
<div class="page-hdr">
  <div class="container">
    <h4 class="page-title"><i class="bi bi-person-plus-fill me-2"></i>Student Registration</h4>
    <p class="page-sub">Fill your details and capture face photos to register.</p>
  </div>
</div>

<div class="container py-4">
  <div class="row g-4">

    <!-- Form -->
    <div class="col-lg-5">
      <div class="form-card">
        <h6 class="card-section-title"><i class="bi bi-info-circle me-2"></i>Student Information</h6>

        <div class="field-group"><label>Full Name *</label>
          <input type="text" id="inp-name" class="form-input" placeholder="e.g. Aarav Patel"/></div>

        <div class="field-group"><label>Roll Number * <small class="text-muted">(unique)</small></label>
          <input type="text" id="inp-roll" class="form-input" placeholder="e.g. BCA2024001"/></div>

        <div class="field-group"><label>Enrollment Number *</label>
          <input type="text" id="inp-enrollment" class="form-input" placeholder="e.g. EN20240001"/></div>

        <div class="row g-2">
          <div class="col-7"><div class="field-group"><label>Course *</label>
            <select id="inp-course" class="form-input">
              <option value="">Select Course</option>
              <option>BCA</option><option>BCS</option><option>BSc CS</option>
              <option>MCA</option><option>BTech CS</option>
            </select></div></div>
          <div class="col-5"><div class="field-group"><label>Semester *</label>
            <select id="inp-semester" class="form-input">
              <option value="">Sem</option>
              <option>1</option><option>2</option><option>3</option>
              <option>4</option><option>5</option><option>6</option>
            </select></div></div>
        </div>

        <div class="field-group"><label>Mobile Number *</label>
          <input type="tel" id="inp-mobile" class="form-input" placeholder="10-digit number" maxlength="10"/></div>

        <div class="field-group"><label>Password * <small class="text-muted">(for student login)</small></label>
          <input type="password" id="inp-password" class="form-input" placeholder="Create a password"/></div>

        <div id="form-alert"></div>
      </div>
    </div>

    <!-- Camera -->
    <div class="col-lg-7">
      <div class="form-card">
        <h6 class="card-section-title"><i class="bi bi-camera-fill me-2"></i>Face Capture</h6>
        <p class="text-muted small mb-3">Capture 3–5 clear face photos. Good lighting recommended.</p>

        <!-- Camera Box -->
        <div class="reg-camera-wrap mb-3">
          <video id="reg-video" autoplay playsinline muted></video>
          <canvas id="reg-canvas" style="display:none"></canvas>
          <div class="face-oval"></div>
          <div id="reg-cam-badge" class="reg-cam-badge"><i class="bi bi-camera-video-off me-1"></i>Camera off</div>
          <div id="dup-face-warning" class="dup-face-overlay d-none">
            <i class="bi bi-exclamation-triangle-fill"></i>
            <span id="dup-face-msg">Face already registered!</span>
          </div>
        </div>

        <div class="d-flex gap-2 mb-3">
          <button id="btn-cam" class="btn-cam-start flex-grow-1" onclick="startCam()">
            <i class="bi bi-camera-video-fill me-2"></i>Start Camera
          </button>
          <button id="btn-cap" class="btn-cam-capture flex-grow-1" onclick="capture()" disabled>
            <i class="bi bi-camera-fill me-2"></i>Capture
          </button>
        </div>

        <!-- Counter -->
        <div class="cap-counter">
          <span id="cap-count">0</span>/5 photos captured
          <div class="progress mt-1" style="height:4px">
            <div id="cap-bar" class="progress-bar bg-success" style="width:0"></div>
          </div>
        </div>
        <div id="thumbnails" class="thumb-row mt-2"></div>

        <button id="btn-reg" class="btn-submit w-100 mt-3" onclick="submitReg()" disabled>
          <i class="bi bi-person-check-fill me-2"></i>Complete Registration
        </button>
      </div>
    </div>
  </div>
</div>

<!-- Success Modal -->
<div class="modal fade" id="successModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content modal-custom">
      <div class="modal-body text-center p-5">
        <div class="success-anim-wrap">
          <div class="success-ring"></div>
          <div class="success-checkmark"><i class="bi bi-check-lg"></i></div>
        </div>
        <h4 class="mt-3">Registration Successful!</h4>
        <p class="text-muted" id="modal-msg"></p>
        <div class="d-flex gap-2 justify-content-center mt-4">
          <a href="/student/login" class="btn-submit px-4">Login & Mark Attendance</a>
          <a href="/" class="btn-outline-custom px-4">Go Home</a>
        </div>
      </div>
    </div>
  </div>
</div>
{% endblock %}

{% block extra_scripts %}
<script>
let captured = [];
let stream   = null;
let dupCheckTimeout = null;

async function startCam() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width:640, height:480, facingMode:"user" } });
    document.getElementById("reg-video").srcObject = stream;
    document.getElementById("btn-cap").disabled = false;
    document.getElementById("btn-cam").disabled = true;
    document.getElementById("reg-cam-badge").innerHTML = '<i class="bi bi-circle-fill text-success me-1"></i>Camera active';
  } catch(e) {
    showAlert("error", "Camera error: " + e.message);
  }
}

async function capture() {
  if (captured.length >= 5) { showAlert("warning","Maximum 5 photos captured."); return; }

  const video  = document.getElementById("reg-video");
  const canvas = document.getElementById("reg-canvas");
  canvas.width  = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const dataURL = canvas.toDataURL("image/jpeg", 0.85);
  captured.push(dataURL);
  refreshThumbs();
  updateCaptureUI();

  // Flash effect
  document.querySelector(".reg-camera-wrap").classList.add("flash");
  setTimeout(()=>document.querySelector(".reg-camera-wrap").classList.remove("flash"), 200);

  // Check for duplicate face on first capture
  if (captured.length === 1) {
    checkDuplicateFace(dataURL);
  }
}

async function checkDuplicateFace(imgB64) {
  const res  = await fetch("/api/check_face_duplicate", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ image: imgB64 })
  }).catch(()=>null);
  if (!res) return;
  const data = await res.json();
  if (data.duplicate) {
    document.getElementById("dup-face-msg").textContent =
      `Face already registered! Belongs to: ${data.name} (Roll: ${data.roll})`;
    document.getElementById("dup-face-warning").classList.remove("d-none");
    captured.pop();
    refreshThumbs();
    updateCaptureUI();
    setTimeout(()=>document.getElementById("dup-face-warning").classList.add("d-none"), 5000);
  }
}

function refreshThumbs() {
  const wrap = document.getElementById("thumbnails");
  wrap.innerHTML = "";
  captured.forEach((img, i) => {
    const div = document.createElement("div");
    div.className = "thumb-item";
    div.innerHTML = `<img src="${img}"/><span class="thumb-num">${i+1}</span><button class="thumb-del" onclick="removeCap(${i})">×</button>`;
    wrap.appendChild(div);
  });
}

function removeCap(i) {
  captured.splice(i, 1);
  refreshThumbs();
  updateCaptureUI();
}

function updateCaptureUI() {
  const n = captured.length;
  document.getElementById("cap-count").textContent = n;
  document.getElementById("cap-bar").style.width = (n/5*100)+"%";
  document.getElementById("btn-reg").disabled = n < 3;
  if (n >= 5) document.getElementById("btn-cap").disabled = true;
}

async function submitReg() {
  const name     = document.getElementById("inp-name").value.trim();
  const roll     = document.getElementById("inp-roll").value.trim();
  const enroll   = document.getElementById("inp-enrollment").value.trim();
  const course   = document.getElementById("inp-course").value;
  const semester = document.getElementById("inp-semester").value;
  const mobile   = document.getElementById("inp-mobile").value.trim();
  const password = document.getElementById("inp-password").value.trim();

  if (!name||!roll||!enroll||!course||!semester||!mobile||!password) {
    showAlert("error","Please fill in all fields."); return;
  }
  if (mobile.length!==10||isNaN(mobile)) {
    showAlert("error","Enter a valid 10-digit mobile number."); return;
  }
  if (captured.length < 3) {
    showAlert("error","Capture at least 3 face photos."); return;
  }

  const btn = document.getElementById("btn-reg");
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Registering...';

  const res = await fetch("/api/register", {
    method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({ name, roll_no:roll, enrollment:enroll, course, semester, mobile, password, images:captured })
  }).catch(()=>null);

  if (!res) { showAlert("error","Server error."); btn.disabled=false; btn.innerHTML='<i class="bi bi-person-check-fill me-2"></i>Complete Registration'; return; }
  const data = await res.json();

  if (data.success) {
    if (stream) stream.getTracks().forEach(t=>t.stop());
    document.getElementById("modal-msg").textContent = data.message;
    new bootstrap.Modal(document.getElementById("successModal")).show();
  } else {
    showAlert("error", data.message);
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-person-check-fill me-2"></i>Complete Registration';
  }
}

function showAlert(type, msg) {
  const el = document.getElementById("form-alert");
  el.innerHTML = `<div class="alert-box ${type} mt-2"><i class="bi bi-${type==='error'?'x-circle':'exclamation-circle'} me-2"></i>${msg}</div>`;
}
</script>
{% endblock %}
