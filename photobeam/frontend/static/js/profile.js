// Confirm deletion
document.querySelectorAll('.delete-form').forEach(form => {
    form.addEventListener('submit', function(event) {
        if (!confirm('Are you sure you want to delete this album?')) {
            event.preventDefault();
        }
    });
});
// Download QR Code
function downloadQRCode(uniqueId) {
    const qrImage = document.getElementById(`qr-code-${uniqueId}`);
    const qrURL = qrImage.src;
    const link = document.createElement('a');
    link.href = qrURL;
    link.download = `qr_code_${uniqueId}.png`;
    link.click();
}