document.addEventListener('DOMContentLoaded', function() {
    var fileInput = document.getElementById('id_file');
    var numberOfPagesContainer = document.getElementById('numberOfPagesContainer');

    fileInput.addEventListener('change', function() {
        if (fileInput.value) {
            // Show the number of pages field if a file is uploaded
            numberOfPagesContainer.style.display = 'block';
        } else {
            // Hide the number of pages field if no file is uploaded
            numberOfPagesContainer.style.display = 'none';
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const paymentStatusLabel = document.querySelector('label[for="payment_status"]');
    const discountLabel = document.querySelector('label[for="discount"]');
    if (paymentStatusLabel) {
        paymentStatusLabel.style.display = 'none'; // Hides the label
        paymentStatusLabel.nextElementSibling.style.display = 'none'; // Hides the associated input
    }
    if (discountLabel) {
        discountLabel.style.display = 'none'; // Hides the label
        discountLabel.nextElementSibling.style.display = 'none'; // Hides the associated input
    }
});

