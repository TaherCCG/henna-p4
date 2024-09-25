// Stripe payment setup
document.addEventListener('DOMContentLoaded', function () {
    /*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
    */

    let stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
    let clientSecret = $('#id_client_secret').text().slice(1, -1);
    let stripe = Stripe(stripePublicKey);
    let elements = stripe.elements();
    let style = {
        base: {
            color: '#000',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };
    let card = elements.create('card', { style: style });
    card.mount('#card-element');

    // Handle real-time validation errors on the card element
    card.addEventListener('change', function (event) {
        let errorDiv = document.getElementById('card-errors');
        if (event.error) {
            let html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
            `;
            $(errorDiv).html(html);
        } else {
            errorDiv.textContent = '';
        }
    });

    // Handle form submission
    let form = document.getElementById('payment-form');

    form.addEventListener('submit', function (ev) {
        ev.preventDefault();

        // Disable the card element and show spinner
        card.update({ 'disabled': true });
        $('#submit-button').attr('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> Processing...'); // Show spinner

        // Capture save info and CSRF token
        let saveInfo = $('#id-save-info').prop('checked');
        let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
        let postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo,
        };
        let url = '/checkout/cache_checkout_data/';

        // Post data to the server
        $.post(url, postData).done(function () {
            // Stripe payment confirmation logic removed for now see EOF. 

            // Directly submit the form without confirming the card payment
            form.submit(); // This submits the form and proceeds to checkout success
        }).fail(function () {
            // Reload the page in case of error (error will be handled by Django messages)
            location.reload();
        }).always(function () {
            // Restore the button state in case of fail
            card.update({ 'disabled': false });
            $('#submit-button').attr('disabled', false).html('Submit Payment');  // Restore button text
        });
    });

    // Delivery method update setup
    const deliverySelect = document.getElementById('id_delivery_method');
    const deliveryCostField = document.getElementById('delivery-cost');
    const orderSummaryDeliveryCost = document.getElementById('order-summary-delivery-cost');
    const grandTotalField = document.getElementById('grand-total');
    const grandTotalToPayField = document.getElementById('grand-total-to-pay');
    const estimatedDeliveryTimeField = document.getElementById('estimated-delivery-time');
    const companyNameField = document.getElementById('company-name');

    // Update delivery cost and details when delivery method changes
    deliverySelect.addEventListener('change', function () {
        const deliveryMethodId = this.value;

        // Fetch updated delivery details from the server
        $.ajax({
            url: `/checkout/update-delivery/${deliveryMethodId}/`,
            method: 'GET',
            success: function (data) {
                companyNameField.textContent = `Company: ${data.company_name} (${data.delivery_name})`;
                estimatedDeliveryTimeField.textContent = `Estimated Delivery Time: ${data.estimated_delivery_time}`;
                deliveryCostField.textContent = `£${data.delivery_cost.toFixed(2)}`;
                orderSummaryDeliveryCost.textContent = `£${data.delivery_cost.toFixed(2)}`;
                grandTotalField.textContent = `£${data.grand_total_with_vat.toFixed(2)}`;
                grandTotalToPayField.textContent = `£${data.grand_total_with_vat.toFixed(2)}`;
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                deliveryCostField.textContent = 'Error updating delivery cost';
            }
        });
    });
});


/*

I've temporarily removed the code for stripe.confirmCardPayment because it 
seems like there are some issues with the webhooks that are stopping from getting 
a response from Stripe. This is causing the checkout page to freeze, which isn't 
great for users. I need to do more investigation and testing to sort out these 
webhook problems before I can put the payment confirmation logic back in.

           stripe.confirmCardPayment(clientSecret, {
               payment_method: {
                   card: card,
                   billing_details: {
                       name: $.trim(form.full_name.value),
                       phone: $.trim(form.phone_number.value),
                       email: $.trim(form.email.value),
                       address: {
                           line1: $.trim(form.street_address1.value),
                           line2: $.trim(form.street_address2.value),
                           city: $.trim(form.town_or_city.value),
                           country: $.trim(form.country.value),
                           state: $.trim(form.county.value),
                       }
                   }
               },
               shipping: {
                   name: $.trim(form.full_name.value),
                   phone: $.trim(form.phone_number.value),
                   address: {
                       line1: $.trim(form.street_address1.value),
                       line2: $.trim(form.street_address2.value),
                       city: $.trim(form.town_or_city.value),
                       country: $.trim(form.country.value),
                       postal_code: $.trim(form.postcode.value),
                       state: $.trim(form.county.value),
                   }
               },
           }).then(function (result) {
               if (result.error) {
                   let errorDiv = document.getElementById('card-errors');
                   let html = `
                   <span class="icon" role="alert">
                       <i class="fas fa-times"></i>
                   </span>
                   <span>${result.error.message}</span>`;
                   $(errorDiv).html(html);
                   card.update({ 'disabled': false });
                   $('#submit-button').attr('disabled', false).html('Submit Payment');  // Restore button text
               } else {
                   if (result.paymentIntent.status === 'succeeded') {
                       form.submit();
                   }
               }
           });
*/
