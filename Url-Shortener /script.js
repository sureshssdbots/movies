// DOM Elements
const urlInput = document.getElementById("urlInput");
const shortenBtn = document.getElementById("shortenBtn");
const resultDiv = document.getElementById("result");
const shortUrl = document.getElementById("shortUrl");
const copyBtn = document.getElementById("copyBtn");

// Mock Shorten Function (Replace with API Call)
async function shortenURL(url) {
    // Mock shortened URL (You can replace this with your API response)
    return `https://short.ly/${Math.random().toString(36).substr(2, 8)}`;
}

// Button Click Event
shortenBtn.addEventListener("click", async () => {
    const longUrl = urlInput.value.trim();
    if (!longUrl) {
        alert("Please enter a valid URL!");
        return;
    }

    try {
        const shortLink = await shortenURL(longUrl);
        shortUrl.textContent = shortLink;
        shortUrl.href = shortLink;
        resultDiv.classList.remove("hidden");
    } catch (error) {
        alert("Failed to shorten URL. Try again!");
    }
});

// Copy Button Click Event
copyBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(shortUrl.textContent).then(() => {
        alert("Shortened URL copied to clipboard!");
    });
});
