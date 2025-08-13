// Zoom modal
function openModal(ref) {
    const modal = document.getElementById('imageModal');
    const modalImg = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    const modalDesc = document.getElementById('modalDesc');
    
    modalImg.src = `/static/images/extracted/${ref}.jpg`;
    modalTitle.textContent = ref;
    modalDesc.textContent = document.querySelector(`[data-ref="${ref}"] .part-desc`).textContent;
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('imageModal').style.display = 'none';
}

// Search functionality
const searchInput = document.getElementById('searchInput');
const searchBtn = document.getElementById('searchBtn');
const searchResults = document.getElementById('searchResults');

function performSearch() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const parts = document.querySelectorAll('.part-card');
    
    parts.forEach(card => {
        const ref = card.querySelector('.part-ref').textContent.toLowerCase();
        const desc = card.querySelector('.part-desc').textContent.toLowerCase();
        
        if (ref.includes(searchTerm) || desc.includes(searchTerm)) {
            card.style.display = 'block';
            card.style.animation = 'highlight 0.5s';
        } else {
            card.style.display = searchTerm ? 'none' : 'block';
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    searchInput.addEventListener('input', performSearch);
    searchBtn.addEventListener('click', performSearch);
    
    // Modal close events
    document.querySelector('.close').addEventListener('click', closeModal);
    document.getElementById('imageModal').addEventListener('click', closeModal);
    
    // Smooth scroll
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            target.scrollIntoView({ behavior: 'smooth' });
        });
    });
});

// Download function
function downloadImage(ref) {
    const link = document.createElement('a');
    link.href = `/static/images/extracted/${ref}.jpg`;
    link.download = `${ref}.jpg`;
    link.click();
}

// Add highlight animation
const style = document.createElement('style');
style.textContent = `
    @keyframes highlight {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);