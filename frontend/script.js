// ============================================
// WEBSITE ANIMATION FUNCTIONS (YOUR ORIGINAL)
// ============================================

function revealOnScroll() {
    const reveals = document.querySelectorAll('.reveal');

    reveals.forEach(element => {
        const windowHeight = window.innerHeight;
        const elementTop = element.getBoundingClientRect().top;
        const revealPoint = 100;

        if (elementTop < windowHeight - revealPoint) {
            element.classList.add('active');
        }
    });
}

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", function (e) {
            const href = this.getAttribute("href");
            if (href === "#") return;
            e.preventDefault();
            const targetElement = document.querySelector(href);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });
            }
        });
    });
}

function initNavbarScroll() {
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = "0 4px 6px rgba(0,0,0,0.3)";
        } else {
            navbar.style.boxShadow = "none";
        }
    });
}

// ============================================
// SECURE CHAT SYSTEM (WEBSOCKET & PERSISTENCE)
// ============================================

// UPDATE: When you deploy to Render, change 'ws://localhost:8000' to 'wss://your-app.onrender.com'
const socket = new WebSocket('wss://secure-chat-app-eagy.onrender.com');
const DEVICE_USER_KEY = "securechat_device_user";

let myUsername = localStorage.getItem(DEVICE_USER_KEY);

socket.onopen = () => {
    console.log("Connected to Secure Backend");
    // AUTO-LOGIN: If this device has a saved name, send it to the server immediately
    if (myUsername) {
        socket.send(JSON.stringify({ type: "login", username: myUsername }));
    }
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);

    if (data.type === "login_success") {
        myUsername = data.username;
        localStorage.setItem(DEVICE_USER_KEY, myUsername); // Fix name to this device
        
        // UI: You can trigger a transition here to hide the login screen
        console.log("Identity fixed to device: " + myUsername);
    } 

    else if (data.type === "error") {
        alert(data.message);
        // Optional: clear cache if the server rejects the name
        // localStorage.removeItem(DEVICE_USER_KEY);
    }

    else if (data.type === "user_list") {
        updateOnlineUsersList(data.users);
    }

    else if (data.type === "chat") {
        // This is where your AES-128 / HMAC logic will process incoming messages
        console.log("Encrypted message received");
    }
};

// ============================================
// ENTER CHAT (MERGED LOGIC)
// ============================================

function enterChat() {
    const usernameInput = document.getElementById("username").value.trim();

    // 1. Check if name is empty
    if (!usernameInput) {
        alert("Please enter a username");
        return;
    }

    // 2. CRITICAL CHECK: Is the server actually connected?
    if (socket.readyState !== WebSocket.OPEN) {
        alert("Connecting to secure server... Please wait 5 seconds and try again.");
        
        // If it's closed, try to reconnect
        if (socket.readyState === WebSocket.CLOSED) {
            location.reload(); 
        }
        return;
    }

    const deviceUser = localStorage.getItem(DEVICE_USER_KEY);

    if (deviceUser && deviceUser !== usernameInput) {
        alert("This device is already registered as: " + deviceUser);
        return;
    }

    socket.send(JSON.stringify({
        type: "login",
        username: usernameInput
    }));
}
// ============================================
// ONLINE USERS DISPLAY (UI)
// ============================================

function updateOnlineUsersList(users) {
    const list = document.getElementById("onlineUsers"); // Ensure this ID matches your HTML
    if (!list) return;

    list.innerHTML = "";

    users.forEach(username => {
        const li = document.createElement("li");

        // The "(you)" logic for the specific device
        if (username === myUsername) {
            li.innerHTML = `<span class="user-me"><strong>${username} (you)</strong></span>`;
            li.style.color = "#4CAF50"; 
        } else {
            li.textContent = username;
        }
        
        list.appendChild(li);
    });
}

// ============================================
// INITIALIZE WEBSITE (YOUR ORIGINAL DOM LOAD)
// ============================================

document.addEventListener("DOMContentLoaded", () => {
    // Run your original animations
    initSmoothScroll();
    initNavbarScroll();
    window.addEventListener("scroll", revealOnScroll);
    revealOnScroll();

    console.log("SecureChat Website & Secure System Loaded");
});
function resetDeviceIdentity() {
    if(confirm("This will clear your username from this device. Continue?")) {
        localStorage.removeItem("securechat_device_user");
        location.reload(); // Refresh to show login screen again
    }
}