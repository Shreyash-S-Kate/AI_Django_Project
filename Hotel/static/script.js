const API_BASE_URL = '/api';

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
        document.getElementById(btn.dataset.section).classList.add('active');
        
        loadSectionData(btn.dataset.section);
    });
});

// Load section data
async function loadSectionData(section) {
    switch(section) {
        case 'dashboard':
            await loadDashboardStats();
            break;
        case 'rooms':
            await loadRooms();
            break;
        case 'guests':
            await loadGuests();
            break;
        case 'bookings':
            await loadBookings();
            break;
    }
}

// API calls
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        if (response.status === 204) {
            return null;
        }
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Dashboard
async function loadDashboardStats() {
    try {
        const [rooms, guests, bookings] = await Promise.all([
            apiCall('/rooms/'),
            apiCall('/guests/'),
            apiCall('/bookings/')
        ]);
        
        document.getElementById('total-rooms').textContent = rooms.length || rooms.count;
        document.getElementById('available-rooms').textContent = 
            rooms.filter ? rooms.filter(r => r.is_available).length : 0;
        document.getElementById('total-guests').textContent = guests.length || guests.count;
        document.getElementById('active-bookings').textContent = 
            bookings.filter ? bookings.filter(b => 
                ['CONFIRMED', 'CHECKED_IN'].includes(b.status)
            ).length : 0;
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

// Rooms
async function loadRooms() {
    try {
        const rooms = await apiCall('/rooms/');
        displayRooms(rooms.results || rooms);
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

function displayRooms(rooms) {
    const tbody = document.getElementById('rooms-tbody');
    tbody.innerHTML = rooms.map(room => `
        <tr>
            <td>${room.room_number}</td>
            <td>${room.room_type}</td>
            <td>$${room.price_per_night}</td>
            <td>
                <span class="status-badge ${room.is_available ? 'status-confirmed' : 'status-cancelled'}">
                    ${room.is_available ? 'Available' : 'Booked'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="editRoom(${room.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deleteRoom(${room.id})">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterRooms() {
    const typeFilter = document.getElementById('room-type-filter').value;
    const availabilityFilter = document.getElementById('room-availability-filter').value;
    
    apiCall('/rooms/').then(rooms => {
        let filtered = rooms.results || rooms;
        
        if (typeFilter) {
            filtered = filtered.filter(r => r.room_type === typeFilter);
        }
        
        if (availabilityFilter) {
            const isAvailable = availabilityFilter === 'true';
            filtered = filtered.filter(r => r.is_available === isAvailable);
        }
        
        displayRooms(filtered);
    });
}

async function showRoomModal(roomId = null) {
    const modal = document.getElementById('room-modal');
    const title = document.getElementById('room-modal-title');
    const form = document.getElementById('room-form');
    
    form.reset();
    document.getElementById('room-id').value = '';
    
    if (roomId) {
        title.textContent = 'Edit Room';
        try {
            const room = await apiCall(`/rooms/${roomId}/`);
            document.getElementById('room-id').value = room.id;
            document.getElementById('room-number').value = room.room_number;
            document.getElementById('room-type').value = room.room_type;
            document.getElementById('room-price').value = room.price_per_night;
            document.getElementById('room-description').value = room.description || '';
            const statusSelect = document.getElementById('room-status');
            if (statusSelect) {
                statusSelect.value = room.is_available ? 'true' : 'false';
            }
        } catch (error) {
            console.error('Error loading room:', error);
            return;
        }
    } else {
        title.textContent = 'Add Room';
        const statusSelect = document.getElementById('room-status');
        if (statusSelect) {
            statusSelect.value = 'true';
        }
    }
    
    modal.style.display = 'block';
}

async function saveRoom(event) {
    event.preventDefault();
    
    const roomId = document.getElementById('room-id').value;
    const statusSelect = document.getElementById('room-status');
    const isAvailable = statusSelect ? statusSelect.value === 'true' : true;
    const roomData = {
        room_number: document.getElementById('room-number').value,
        room_type: document.getElementById('room-type').value,
        price_per_night: parseFloat(document.getElementById('room-price').value),
        description: document.getElementById('room-description').value,
        is_available: isAvailable
    };
    
    try {
        if (roomId) {
            await apiCall(`/rooms/${roomId}/`, 'PUT', roomData);
        } else {
            await apiCall('/rooms/', 'POST', roomData);
        }
        
        closeModal('room-modal');
        loadRooms();
        loadDashboardStats();
    } catch (error) {
        console.error('Error saving room:', error);
        alert('Error saving room. Please try again.');
    }
}

async function editRoom(roomId) {
    showRoomModal(roomId);
}

async function deleteRoom(roomId) {
    if (confirm('Are you sure you want to delete this room?')) {
        try {
            await apiCall(`/rooms/${roomId}/`, 'DELETE');
            loadRooms();
            loadDashboardStats();
        } catch (error) {
            console.error('Error deleting room:', error);
            alert('Error deleting room. Please try again.');
        }
    }
}

// Guests
async function loadGuests() {
    try {
        const guests = await apiCall('/guests/');
        displayGuests(guests.results || guests);
    } catch (error) {
        console.error('Error loading guests:', error);
    }
}

function displayGuests(guests) {
    const tbody = document.getElementById('guests-tbody');
    tbody.innerHTML = guests.map(guest => `
        <tr>
            <td>${guest.first_name} ${guest.last_name}</td>
            <td>${guest.email}</td>
            <td>${guest.phone_number}</td>
            <td>${guest.id_proof}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-secondary" onclick="editGuest(${guest.id})">Edit</button>
                    <button class="btn btn-danger" onclick="deleteGuest(${guest.id})">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function searchGuests() {
    const searchTerm = document.getElementById('guest-search').value.toLowerCase();
    
    apiCall('/guests/').then(guests => {
        const filtered = (guests.results || guests).filter(g => 
            g.first_name.toLowerCase().includes(searchTerm) ||
            g.last_name.toLowerCase().includes(searchTerm) ||
            g.email.toLowerCase().includes(searchTerm) ||
            g.phone_number.includes(searchTerm)
        );
        displayGuests(filtered);
    });
}

async function showGuestModal(guestId = null) {
    const modal = document.getElementById('guest-modal');
    const title = document.getElementById('guest-modal-title');
    const form = document.getElementById('guest-form');
    
    form.reset();
    document.getElementById('guest-id').value = '';
    
    if (guestId) {
        title.textContent = 'Edit Guest';
        try {
            const guest = await apiCall(`/guests/${guestId}/`);
            document.getElementById('guest-id').value = guest.id;
            document.getElementById('guest-first-name').value = guest.first_name;
            document.getElementById('guest-last-name').value = guest.last_name;
            document.getElementById('guest-email').value = guest.email;
            document.getElementById('guest-phone').value = guest.phone_number;
            document.getElementById('guest-address').value = guest.address;
            document.getElementById('guest-id-proof').value = guest.id_proof;
        } catch (error) {
            console.error('Error loading guest:', error);
            return;
        }
    } else {
        title.textContent = 'Add Guest';
    }
    
    modal.style.display = 'block';
}

async function saveGuest(event) {
    event.preventDefault();
    
    const guestId = document.getElementById('guest-id').value;
    const guestData = {
        first_name: document.getElementById('guest-first-name').value,
        last_name: document.getElementById('guest-last-name').value,
        email: document.getElementById('guest-email').value,
        phone_number: document.getElementById('guest-phone').value,
        address: document.getElementById('guest-address').value,
        id_proof: document.getElementById('guest-id-proof').value
    };
    
    try {
        if (guestId) {
            await apiCall(`/guests/${guestId}/`, 'PUT', guestData);
        } else {
            await apiCall('/guests/', 'POST', guestData);
        }
        
        closeModal('guest-modal');
        loadGuests();
        loadDashboardStats();
    } catch (error) {
        console.error('Error saving guest:', error);
        alert('Error saving guest. Please try again.');
    }
}

async function editGuest(guestId) {
    showGuestModal(guestId);
}

async function deleteGuest(guestId) {
    if (confirm('Are you sure you want to delete this guest?')) {
        try {
            await apiCall(`/guests/${guestId}/`, 'DELETE');
            loadGuests();
            loadDashboardStats();
        } catch (error) {
            console.error('Error deleting guest:', error);
            alert('Error deleting guest. Please try again.');
        }
    }
}

// Bookings
async function loadBookings() {
    try {
        const bookings = await apiCall('/bookings/');
        displayBookings(bookings.results || bookings);
    } catch (error) {
        console.error('Error loading bookings:', error);
    }
}

function displayBookings(bookings) {
    const tbody = document.getElementById('bookings-tbody');
    tbody.innerHTML = bookings.map(booking => `
        <tr>
            <td>#${booking.id}</td>
            <td>${booking.guest_name || booking.guest?.first_name + ' ' + booking.guest?.last_name}</td>
            <td>${booking.room_number || booking.room?.room_number}</td>
            <td>${booking.check_in_date}</td>
            <td>${booking.check_out_date}</td>
            <td>
                <span class="status-badge status-${booking.status.toLowerCase()}">${booking.status.replace('_', ' ')}</span>
            </td>
            <td>$${booking.total_amount}</td>
            <td>
                <div class="action-buttons">
                    ${booking.status === 'PENDING' ? 
                        `<button class="btn btn-primary" onclick="confirmBooking(${booking.id})">Confirm</button>` : ''}
                    ${booking.status === 'CONFIRMED' ? 
                        `<button class="btn btn-success" onclick="checkInBooking(${booking.id})">Check In</button>` : ''}
                    ${booking.status === 'CHECKED_IN' ? 
                        `<button class="btn btn-warning" onclick="checkOutBooking(${booking.id})">Check Out</button>` : ''}
                    ${['PENDING', 'CONFIRMED'].includes(booking.status) ? 
                        `<button class="btn btn-danger" onclick="cancelBooking(${booking.id})">Cancel</button>` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function filterBookings() {
    const statusFilter = document.getElementById('booking-status-filter').value;
    
    apiCall('/bookings/').then(bookings => {
        let filtered = bookings.results || bookings;
        
        if (statusFilter) {
            filtered = filtered.filter(b => b.status === statusFilter);
        }
        
        displayBookings(filtered);
    });
}

async function showBookingModal() {
    const modal = document.getElementById('booking-modal');
    const form = document.getElementById('booking-form');
    
    form.reset();
    document.getElementById('booking-id').value = '';
    
    try {
        const [guests, rooms] = await Promise.all([
            apiCall('/guests/'),
            apiCall('/rooms/')
        ]);
        
        const guestSelect = document.getElementById('booking-guest');
        guestSelect.innerHTML = '<option value="">Select Guest</option>' + 
            (guests.results || guests).map(g => 
                `<option value="${g.id}">${g.first_name} ${g.last_name}</option>`
            ).join('');
        
        const roomSelect = document.getElementById('booking-room');
        roomSelect.innerHTML = '<option value="">Select Room</option>' + 
            (rooms.results || rooms).filter(r => r.is_available).map(r => 
                `<option value="${r.id}">${r.room_number} - ${r.room_type} ($${r.price_per_night}/night)</option>`
            ).join('');
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Error loading booking data:', error);
        alert('Error loading booking data. Please try again.');
    }
}

async function saveBooking(event) {
    event.preventDefault();
    
    const bookingData = {
        guest: parseInt(document.getElementById('booking-guest').value),
        room: parseInt(document.getElementById('booking-room').value),
        check_in_date: document.getElementById('booking-check-in').value,
        check_out_date: document.getElementById('booking-check-out').value,
        special_requests: document.getElementById('booking-requests').value,
        status: 'PENDING'
    };
    
    if (bookingData.check_out_date <= bookingData.check_in_date) {
        alert('Check-out date must be after check-in date.');
        return;
    }
    
    try {
        await apiCall('/bookings/', 'POST', bookingData);
        
        closeModal('booking-modal');
        loadBookings();
        loadRooms();
        loadDashboardStats();
    } catch (error) {
        console.error('Error creating booking:', error);
        alert('Error creating booking. Please try again.');
    }
}

async function confirmBooking(bookingId) {
    try {
        await apiCall(`/bookings/${bookingId}/confirm/`, 'POST');
        loadBookings();
        loadRooms();
        loadDashboardStats();
    } catch (error) {
        console.error('Error confirming booking:', error);
        alert('Error confirming booking. Please try again.');
    }
}

async function checkInBooking(bookingId) {
    try {
        await apiCall(`/bookings/${bookingId}/check_in/`, 'POST');
        loadBookings();
        loadRooms();
        loadDashboardStats();
    } catch (error) {
        console.error('Error checking in booking:', error);
        alert('Error checking in booking. Please try again.');
    }
}

async function checkOutBooking(bookingId) {
    try {
        await apiCall(`/bookings/${bookingId}/check_out/`, 'POST');
        loadBookings();
        loadRooms();
        loadDashboardStats();
    } catch (error) {
        console.error('Error checking out booking:', error);
        alert('Error checking out booking. Please try again.');
    }
}

async function cancelBooking(bookingId) {
    if (confirm('Are you sure you want to cancel this booking?')) {
        try {
            await apiCall(`/bookings/${bookingId}/cancel/`, 'POST');
            loadBookings();
            loadRooms();
            loadDashboardStats();
        } catch (error) {
            console.error('Error cancelling booking:', error);
            alert('Error cancelling booking. Please try again.');
        }
    }
}

// Modal functions
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});
