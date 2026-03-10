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
// USER SYSTEM
// ============================================

const DEVICE_USER_KEY = "securechat_device_user";
const USERS_KEY = "securechat_users";

// get device username
function getCurrentUser() {
    return localStorage.getItem(DEVICE_USER_KEY);
}

// get all users
function getUsers() {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
}

// save users
function saveUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

// ============================================
// ENTER CHAT
// ============================================

function enterChat() {

    const usernameInput = document.getElementById("username").value.trim();

    if (!usernameInput) {
        alert("Enter a username");
        return;
    }

    const deviceUser = getCurrentUser();

    if (deviceUser) {
        alert("This device already registered as: " + deviceUser);
        return;
    }

    let users = getUsers();

    const existing = users.find(u => u.name === usernameInput);

    if (existing) {
        alert("Username already used. Try different username.");
        return;
    }

    const newUser = {
        name: usernameInput,
        status: "online",
        lastSeen: Date.now()
    };

    users.push(newUser);

    saveUsers(users);

    localStorage.setItem(DEVICE_USER_KEY, usernameInput);

    loadOnlineUsers();

}

// ============================================
// ONLINE USERS DISPLAY
// ============================================

function loadOnlineUsers() {

    const list = document.getElementById("onlineUsers");

    if (!list) return;

    const users = getUsers();

    const currentUser = getCurrentUser();

    list.innerHTML = "";

    users.forEach(user => {

        const li = document.createElement("li");

        let text = user.name;

        if (user.name === currentUser) {
            text += " (you)";
        }

        text += " - " + user.status;

        li.textContent = text;

        list.appendChild(li);

    });

}

// ============================================
// STATUS SYSTEM
// ============================================

function setBusy() {

    let users = getUsers();

    const currentUser = getCurrentUser();

    users.forEach(user => {

        if (user.name === currentUser) {
            user.status = "busy";
            user.lastSeen = Date.now();
        }

    });

    saveUsers(users);

    loadOnlineUsers();

}

function setAvailable() {

    let users = getUsers();

    const currentUser = getCurrentUser();

    users.forEach(user => {

        if (user.name === currentUser) {
            user.status = "online";
            user.lastSeen = Date.now();
        }

    });

    saveUsers(users);

    loadOnlineUsers();

}

// ============================================
// REMOVE INACTIVE USERS
// ============================================

function cleanupInactiveUsers() {

    let users = getUsers();

    const now = Date.now();

    users = users.filter(user => {

        return now - user.lastSeen < 600000; // 10 minutes

    });

    saveUsers(users);

    loadOnlineUsers();

}

// run cleanup every minute
setInterval(cleanupInactiveUsers, 60000);

// ============================================
// INITIALIZE WEBSITE
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    initSmoothScroll();

    initNavbarScroll();

    window.addEventListener("scroll", revealOnScroll);

    revealOnScroll();

    loadOnlineUsers();

    console.log("SecureChat website loaded");

});