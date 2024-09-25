// When the delete modal is shown, set the delivery ID and name
$('#deleteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var deliveryId = button.data('delivery-id');
    var deliveryName = button.data('delivery-name');
    
    var modal = $(this);
    modal.find('#deliveryName').text(deliveryName);
    
    // Update the form action with the delivery ID
    var action = "{% url 'delete_delivery' 'delivery_id' %}".replace('delivery_id', deliveryId);
    modal.find('#deleteForm').attr('action', action);
});