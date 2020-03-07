/**
 * Sends a suggestion to Omega Psi and sends the user an alert saying that
 * their suggestion has been sent to all the developers of Omega Psi
 */
async function suggest() {

    // Ask the user for the suggestion information
    //  - suggestion text
    const { value: suggestion } = await Swal.fire({
        title: "New Suggestion",
        input: "textarea",
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) { return "You need you specify the suggestion!"; }
        },
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            content: 'swal-content',
            title: 'swal-title',
            confirmButton: 'swal-confirm',
            cancelButton: 'swal-cancel',
            input: 'swal-input'
        }
    })

    // Send a POST request to /suggest to add the suggestion to the database
    if (suggestion) {
        $.ajax({
            url: `${BASE_URL}/suggest`,
            type: "POST",
            data: JSON.stringify({
                description: suggestion
            }),
            contentType: "application/json; charset=utf-8"
        
        // If the request succeeds, let the user know that
        //  their suggestion has been marked as seen
        }).done(function(data) {
            Swal.fire({
                title: "Suggestion Sent!",
                text: "Thank you for making this suggestion. Whenever a developer views it, you'll be notified (as long as you allow messages from Omega Psi)",
                icon: "success",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm'
                }
            })

        // If the request fails send the user a message on why
        }).fail(function(error) {
            Swal.fire({
                title: "Something Went Wrong :(",
                text: error.responseJSON.error,
                icon: "failed",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm'
                }
            })
        })
    }
}

/**
 * Marks a specified bug as seen in the database
 * 
 * @param caseNumber The suggestion case number to update
 */
function markSuggestionAsSeen(caseNumber) {

    // Send a PUT request to /suggest to update the suggestion to marked as seen
    $.ajax({
        url: `${BASE_URL}/suggest`,
        type: "PUT",
        data: JSON.stringify({
            caseNumber: caseNumber
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, update the HTML elements related to the suggestion
    //  and let the developer know that the suggestion was marked as seen
    }).done(function(data) {

        // Update the suggestion's HTML elements
        document.getElementById(`suggestion${caseNumber}SeenText`).innerHTML = "Yes";
        document.getElementById(`markSuggestion${caseNumber}Seen`).innerHTML = `Seen By ${data.developer}`;
        Swal.fire({
            title: "Suggestion Marked As Seen!",
            text: `Suggestion #${caseNumber} has been marked as seen`,
            icon: "success",
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm'
            }
        })

    // If the request fails, the suggestion has already been marked as seen
    }).fail(function(error) {
        Swal.fire({
            title: "Suggestion Already Seen",
            text: `Suggestion #${caseNumber} has already been seen by ${error.responseJSON.developer}`,
            icon: "error",
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm',
                input: 'swal-input'
            }
        })
    })
}