"""
Smart Attendance System - BCA Final Year Project
Deploy-ready version (Railway / Render / Any server)
Features: Student Login + QR Code + OTP + Session Timer + Admin Dashboard
"""

import os, csv, json, base64, random, uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file

# ─── Face Recognition (optional - works without it too) ──────────────────────
try:
    import cv2
    import numpy as np
    from deepface import DeepFace
    FACE_LIB_AVAILABLE = True
    print("✓ DeepFace loaded!")
except ImportError:
    FACE_LIB_AVAILABLE = False
    print("⚠ DeepFace not available - Demo mode ON")

# ─── QR Code ─────────────────────────────────────────────────────────────────
try:
    import qrcode
    from io import BytesIO
    QR_AVAILABLE = True
    print("✓ QRCode loaded!")
except ImportError:
    QR_AVAILABLE = False
    print("⚠ qrcode not available")

# ─── App Config ───────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smart_attend_bca_2024_secret")

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR    = os.path.join(BASE_DIR, "dataset")
STUDENTS_FILE  = os.path.join(BASE_DIR, "students.json")
ATTENDANCE_CSV = os.path.join(BASE_DIR, "attendance.csv")
ALERTS_FILE    = os.path.join(BASE_DIR, "alerts.json")

ADMIN_USERNAME   = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD   = os.environ.get("ADMIN_PASS", "admin123")
SESSION_DURATION = 600  # 10 minutes

# In-memory active sessions
active_sessions = {}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def ensure_dirs():
    os.makedirs(DATASET_DIR, exist_ok=True)

def load_students():
    if os.path.exists(STUDENTS_FILE):
        with open(STUDENTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_students(data):
    with open(STUDENTS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w") as f:
        json.dump(alerts, f, indent=2)

def add_alert(msg, roll_no=""):
    alerts = load_alerts()
    alerts.append({"message": msg, "roll_no": roll_no,
                   "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    save_alerts(alerts[-50:])

def get_today():
    return datetime.now().strftime("%Y-%m-%d")

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def mark_attendance(name, roll_no):
    today = get_today()
    if os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, "r") as f:
            for row in csv.DictReader(f):
                if row.get("Roll Number") == str(roll_no) and row.get("Date") == today:
                    return False, "Attendance already marked today"
    file_exists = os.path.exists(ATTENDANCE_CSV)
    with open(ATTENDANCE_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Name","Roll Number","Date","Time","Status"])
        if not file_exists:
            writer.writeheader()
        writer.writerow({"Name": name, "Roll Number": roll_no,
                         "Date": today, "Time": get_time(), "Status": "Present"})
    return True, "Attendance marked successfully"

def read_attendance():
    if not os.path.exists(ATTENDANCE_CSV):
        return []
    with open(ATTENDANCE_CSV, "r") as f:
        return [dict(row) for row in csv.DictReader(f)]

def get_today_attendance():
    today = get_today()
    return [r for r in read_attendance() if r.get("Date") == today]

def is_session_valid(sid):
    if sid not in active_sessions:
        return False, "Session not found"
    elapsed = (datetime.now() - active_sessions[sid]["created_at"]).total_seconds()
    if elapsed > SESSION_DURATION:
        del active_sessions[sid]
        return False, "Session expired"
    return True, SESSION_DURATION - int(elapsed)

def b64_to_file(img_b64, filename):
    try:
        if not FACE_LIB_AVAILABLE:
            return None
        if "," in img_b64:
            img_b64 = img_b64.split(",")[1]
        arr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        path = os.path.join(BASE_DIR, filename)
        cv2.imwrite(path, img)
        return path
    except Exception as e:
        print(f"b64_to_file error: {e}")
        return None

def save_face_image(roll_no, img_b64, index):
    try:
        if not FACE_LIB_AVAILABLE:
            return None
        if "," in img_b64:
            img_b64 = img_b64.split(",")[1]
        arr = np.frombuffer(base64.b64decode(img_b64), np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        folder = os.path.join(DATASET_DIR, str(roll_no))
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, f"{roll_no}_{index}.jpg")
        cv2.imwrite(path, img)
        return path
    except Exception as e:
        print(f"save_face_image error: {e}")
        return None

def deepface_verify(img_path, folder_path):
    if not os.path.exists(folder_path):
        return False, 0
    images = [f for f in os.listdir(folder_path)
              if f.lower().endswith((".jpg",".jpeg",".png"))]
    if not images:
        return False, 0
    best_conf = 0
    matched   = False
    for img_file in images:
        ref_path = os.path.join(folder_path, img_file)
        try:
            result = DeepFace.verify(
                img1_path=img_path, img2_path=ref_path,
                model_name="VGG-Face", enforce_detection=False,
                distance_metric="cosine", silent=True
            )
            conf = round((1 - result["distance"]) * 100, 1)
            if result["verified"] and conf > best_conf:
                best_conf = conf
                matched   = True
        except:
            continue
    return matched, best_conf

# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if (request.form.get("username") == ADMIN_USERNAME and
                request.form.get("password") == ADMIN_PASSWORD):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        return render_template("admin_login.html", error="Invalid credentials!")
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    students   = load_students()
    all_recs   = read_attendance()
    today_recs = get_today_attendance()
    alerts     = load_alerts()
    att_count  = {}
    for r in all_recs:
        roll = r.get("Roll Number","")
        att_count[roll] = att_count.get(roll, 0) + 1
    total_days          = len(set(r["Date"] for r in all_recs)) if all_recs else 0
    today_present_rolls = {r["Roll Number"] for r in today_recs}
    student_stats = []
    for roll, info in students.items():
        present = att_count.get(roll, 0)
        pct     = round(present / total_days * 100, 1) if total_days > 0 else 0
        student_stats.append({**info, "total_present": present, "percentage": pct,
                               "today_status": "Present" if roll in today_present_rolls else "Absent"})
    return render_template("admin_dashboard.html",
        students=student_stats, today_records=today_recs,
        total_students=len(students), today_present=len(today_recs),
        today_absent=len(students)-len(today_recs), today=get_today(),
        total_days=total_days, alerts=list(reversed(alerts))[:20],
        demo_mode=not FACE_LIB_AVAILABLE)

@app.route("/admin/start_session", methods=["POST"])
def start_session():
    if not session.get("admin"):
        return jsonify({"success": False})
    sid = str(uuid.uuid4())[:12]
    otp = str(random.randint(100000, 999999))
    active_sessions[sid] = {"otp": otp, "created_at": datetime.now(), "used_by": []}
    return jsonify({"success": True, "session_id": sid, "otp": otp,
                    "duration": SESSION_DURATION, "qr_url": f"/qr/{sid}"})

@app.route("/qr/<sid>")
def generate_qr(sid):
    if not QR_AVAILABLE:
        return "Install qrcode: pip install qrcode[pil]", 400
    host = request.host_url.rstrip("/")
    url  = f"{host}/attend/{sid}"
    img  = qrcode.make(url)
    buf  = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/admin/download")
def admin_download():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    if not os.path.exists(ATTENDANCE_CSV):
        with open(ATTENDANCE_CSV, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=["Name","Roll Number","Date","Time","Status"]).writeheader()
    return send_file(ATTENDANCE_CSV, as_attachment=True, download_name="attendance.csv")

@app.route("/admin/clear_today", methods=["POST"])
def admin_clear_today():
    if not session.get("admin"):
        return jsonify({"success": False})
    today   = get_today()
    records = [r for r in read_attendance() if r.get("Date") != today]
    with open(ATTENDANCE_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Name","Roll Number","Date","Time","Status"])
        w.writeheader(); w.writerows(records)
    return jsonify({"success": True})

@app.route("/admin/delete_student/<roll_no>", methods=["POST"])
def admin_delete_student(roll_no):
    if not session.get("admin"):
        return jsonify({"success": False})
    students = load_students()
    if roll_no in students:
        del students[roll_no]
        save_students(students)
    import shutil
    folder = os.path.join(DATASET_DIR, roll_no)
    if os.path.exists(folder):
        shutil.rmtree(folder)
    return jsonify({"success": True})

# ─── STUDENT ROUTES ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/student/login", methods=["GET","POST"])
def student_login():
    if request.method == "POST":
        roll = request.form.get("roll_no","").strip()
        pwd  = request.form.get("password","").strip()
        students = load_students()
        if roll in students and students[roll].get("password") == pwd:
            session["student_roll"] = roll
            session["student_name"] = students[roll]["name"]
            after = session.pop("after_login", None)
            return redirect(after if after else url_for("student_dashboard"))
        return render_template("student_login.html", error="Invalid Roll Number or Password")
    return render_template("student_login.html")

@app.route("/student/logout")
def student_logout():
    session.pop("student_roll", None)
    session.pop("student_name", None)
    return redirect(url_for("student_login"))

@app.route("/student/dashboard")
def student_dashboard():
    if not session.get("student_roll"):
        return redirect(url_for("student_login"))
    roll       = session["student_roll"]
    students   = load_students()
    info       = students.get(roll, {})
    all_recs   = read_attendance()
    total_days = len(set(r["Date"] for r in all_recs)) if all_recs else 0
    my_present = sum(1 for r in all_recs if r.get("Roll Number") == roll)
    pct        = round(my_present / total_days * 100, 1) if total_days > 0 else 0
    today_marked = any(r.get("Roll Number") == roll and r.get("Date") == get_today()
                       for r in all_recs)
    return render_template("student_dashboard.html",
        student=info, total_present=my_present, total_days=total_days,
        percentage=pct, low_attendance=(pct < 75 and total_days > 0),
        today_marked=today_marked)

@app.route("/attend/<sid>")
def attend_page(sid):
    if not session.get("student_roll"):
        session["after_login"] = f"/attend/{sid}"
        return redirect(url_for("student_login"))
    valid, val = is_session_valid(sid)
    if not valid:
        return render_template("attend.html",
            error="Session expired. Ask teacher to start a new session.",
            sid=sid, remaining=0)
    return render_template("attend.html", sid=sid, remaining=val, error=None)

# ─── API: Register ────────────────────────────────────────────────────────────

@app.route("/api/register", methods=["POST"])
def api_register():
    ensure_dirs()
    data       = request.get_json()
    name       = data.get("name","").strip()
    roll_no    = data.get("roll_no","").strip()
    enrollment = data.get("enrollment","").strip()
    course     = data.get("course","").strip()
    semester   = data.get("semester","").strip()
    mobile     = data.get("mobile","").strip()
    password   = data.get("password","").strip()
    images     = data.get("images",[])

    if not all([name, roll_no, enrollment, course, semester, mobile, password]):
        return jsonify({"success": False, "message": "All fields are required."})
    if len(images) < 3:
        return jsonify({"success": False, "message": "Please capture at least 3 face photos."})

    students = load_students()
    if roll_no in students:
        return jsonify({"success": False, "message": f"Roll Number {roll_no} is already registered."})

    if FACE_LIB_AVAILABLE:
        # Check duplicate face
        temp_path = b64_to_file(images[0], "temp_reg.jpg")
        if temp_path:
            for existing_roll in os.listdir(DATASET_DIR):
                folder = os.path.join(DATASET_DIR, existing_roll)
                if not os.path.isdir(folder) or existing_roll == roll_no:
                    continue
                matched, _ = deepface_verify(temp_path, folder)
                if matched:
                    ename = students.get(existing_roll, {}).get("name", existing_roll)
                    return jsonify({"success": False,
                        "message": f"Face already registered! Belongs to: {ename} (Roll: {existing_roll})"})
        # Save face images
        saved = sum(1 for i, img in enumerate(images) if save_face_image(roll_no, img, i+1))
        if saved == 0:
            return jsonify({"success": False, "message": "Could not save face images. Try again."})

    students[roll_no] = {
        "name": name, "roll_no": roll_no, "enrollment": enrollment,
        "course": course, "semester": semester, "mobile": mobile,
        "password": password,
        "registered_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_students(students)
    return jsonify({"success": True, "message": f"Registration successful! Welcome, {name}.",
                    "demo_mode": not FACE_LIB_AVAILABLE})

# ─── API: Check Face Duplicate ────────────────────────────────────────────────

@app.route("/api/check_face_duplicate", methods=["POST"])
def check_face_duplicate():
    if not FACE_LIB_AVAILABLE:
        return jsonify({"duplicate": False})
    data    = request.get_json()
    img_b64 = data.get("image","")
    if not os.path.exists(DATASET_DIR) or not os.listdir(DATASET_DIR):
        return jsonify({"duplicate": False})
    temp_path = b64_to_file(img_b64, "temp_dup.jpg")
    if not temp_path:
        return jsonify({"duplicate": False})
    students = load_students()
    for existing_roll in os.listdir(DATASET_DIR):
        folder = os.path.join(DATASET_DIR, existing_roll)
        if not os.path.isdir(folder):
            continue
        matched, _ = deepface_verify(temp_path, folder)
        if matched:
            name = students.get(existing_roll, {}).get("name", existing_roll)
            return jsonify({"duplicate": True, "name": name, "roll": existing_roll})
    return jsonify({"duplicate": False})

# ─── API: Verify OTP ──────────────────────────────────────────────────────────

@app.route("/api/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    sid  = data.get("session_id","")
    otp  = data.get("otp","").strip()
    roll = session.get("student_roll","")
    valid, val = is_session_valid(sid)
    if not valid:
        return jsonify({"success": False, "message": "Session expired. Ask teacher to start a new session."})
    sess = active_sessions[sid]
    if sess["otp"] != otp:
        return jsonify({"success": False, "message": "Incorrect OTP. Please check and try again."})
    if roll in sess["used_by"]:
        add_alert(f"Suspicious: {roll} tried to reuse OTP", roll)
        return jsonify({"success": False, "message": "You already marked attendance in this session."})
    return jsonify({"success": True, "message": "OTP verified! Now scan your face."})

# ─── API: Mark Attendance ─────────────────────────────────────────────────────

@app.route("/api/mark_attendance", methods=["POST"])
def api_mark_attendance():
    data    = request.get_json()
    sid     = data.get("session_id","")
    img_b64 = data.get("image","")
    roll    = session.get("student_roll","")

    if not roll:
        return jsonify({"success": False, "message": "Not logged in."})

    valid, val = is_session_valid(sid)
    if not valid:
        return jsonify({"success": False, "message": "Session expired."})

    sess     = active_sessions[sid]
    students = load_students()

    if roll in sess["used_by"]:
        add_alert(f"Duplicate attempt by {roll}", roll)
        return jsonify({"success": False, "message": "Attendance already marked in this session."})

    # ── DEMO MODE (no DeepFace) ───────────────────────────────────
    if not FACE_LIB_AVAILABLE:
        if roll in students:
            ok, msg = mark_attendance(students[roll]["name"], roll)
            if ok:
                sess["used_by"].append(roll)
            return jsonify({
                "success": ok, "recognized": True,
                "name": students[roll]["name"], "roll_no": roll,
                "message": msg, "already_marked": not ok
            })
        return jsonify({"success": False, "message": "Student not found."})

    # ── DEEPFACE MODE ─────────────────────────────────────────────
    student_folder = os.path.join(DATASET_DIR, roll)
    if not os.path.exists(student_folder) or not os.listdir(student_folder):
        return jsonify({"success": False, "message": "Face not registered. Please register first."})

    temp_path = b64_to_file(img_b64, f"temp_scan_{roll}.jpg")
    if not temp_path:
        return jsonify({"success": False, "message": "Could not process image."})

    try:
        matched, confidence = deepface_verify(temp_path, student_folder)
        if matched:
            name    = students[roll]["name"]
            ok, msg = mark_attendance(name, roll)
            if ok:
                sess["used_by"].append(roll)
            else:
                add_alert(f"Duplicate today: {roll}", roll)
            return jsonify({
                "success": ok, "recognized": True, "name": name,
                "roll_no": roll, "confidence": confidence,
                "message": msg, "already_marked": not ok
            })
        else:
            return jsonify({"success": False, "recognized": False,
                            "message": "Face not matched. Try again with better lighting."})
    except Exception as e:
        print(f"DeepFace error: {e}")
        return jsonify({"success": False, "message": "Face scan failed. Please try again."})

# ─── API: Misc ────────────────────────────────────────────────────────────────

@app.route("/api/today_attendance")
def api_today():
    return jsonify({"records": get_today_attendance(), "date": get_today()})

@app.route("/api/session_remaining/<sid>")
def api_session_remaining(sid):
    valid, val = is_session_valid(sid)
    return jsonify({"valid": valid, "remaining": val if valid else 0})

# ─── MAIN ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ensure_dirs()
    port = int(os.environ.get("PORT", 8080))
    print(f"\n{'='*50}")
    print("  SMART ATTENDANCE SYSTEM")
    print(f"  Face Recognition : {'✓ DeepFace' if FACE_LIB_AVAILABLE else '⚠ Demo Mode'}")
    print(f"  Admin: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
    print(f"  URL: http://localhost:{port}")
    print(f"{'='*50}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
