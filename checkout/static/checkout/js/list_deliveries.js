// When the delete modal is shown, set the delivery ID and name
document.addEventListener('DOMContentLoaded', function () {
    let deleteModal = document.getElementById('deleteModal');
    deleteModal.addEventListener('show.bs.modal', function (event) {
        let button = event.relatedTarget; // Button that triggered the modal
        let deliveryId = button.getAttribute('data-delivery-id');
        let deliveryName = button.getAttribute('data-delivery-name');

        // Update the modal's content
        let modalTitle = deleteModal.querySelector('#deleteModalLabel');
        let modalBody = deleteModal.querySelector('#deliveryName');
        let action = "{% url 'delete_delivery' 0 %}".replace('0', deliveryId);

        modalBody.textContent = deliveryName;
        deleteModal.querySelector('#deleteForm').setAttribute('action', action);
    });
});