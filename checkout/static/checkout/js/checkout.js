document.addEventListener('DOMContentLoaded', function () {

    // Get references to the HTML elements that we will need to update
    const deliverySelect = document.getElementById('id_delivery_method'); 
    const deliveryCostField = document.getElementById('delivery-cost'); 
    const orderSummaryDeliveryCost = document.getElementById('order-summary-delivery-cost'); 
    const grandTotalField = document.getElementById('grand-total'); 
    const grandTotalToPayField=document.getElementById('grand-total-to-pay');
    const estimatedDeliveryTimeField = document.getElementById('estimated-delivery-time'); 
    const companyNameField = document.getElementById('company-name'); 

    // Add an event listener for when the delivery method is changed
    deliverySelect.addEventListener('change', function () {
        const deliveryMethodId = this.value; 

        // Fetch updated delivery details from the server based on the selected method
        fetch(`/checkout/update-delivery/${deliveryMethodId}/`)
            .then(response => response.json()) // Parse the response as JSON
            .then(data => {
                // Update the page with the data received from the server
                companyNameField.textContent = `Company: ${data.company_name} (${data.delivery_name})`;
                estimatedDeliveryTimeField.textContent = `Estimated Delivery Time: ${data.estimated_delivery_time}`;
                deliveryCostField.textContent = `£${data.delivery_cost.toFixed(2)}`;
                orderSummaryDeliveryCost.textContent = `£${data.delivery_cost.toFixed(2)}`; 
                grandTotalField.textContent = `£${data.grand_total_with_vat.toFixed(2)}`;
                grandTotalToPayField.textContent = `£${data.grand_total_with_vat.toFixed(2)}`; 
            })
            .catch(error => console.error('Error:', error)); 
    });
});
