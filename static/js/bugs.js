const BASE_URL = "https://omegapsi.fellowhashbrown.com";

/**
 * Reports a bug to Omega Psi and sends the user an alert saying that
 * their report has been sent to all the developers of Omega Psi
 */
async function reportBug() {

    // Ask the user for the bug information
    //  - bug source type (website or bot)
    //  - bug source (page or command)
    //  - bug description
    var sourceType, source, description;
    await Swal.mixin({
        title: 'Report a Bug',
        confirmButtonText: "Next &rarr;",
        showCancelButton: true,
        progressSteps: ['1', '2', '3'],
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            content: 'swal-content',
            title: 'swal-title',
            confirmButton: 'swal-confirm',
            cancelButton: 'swal-cancel',
            input: 'swal-input'
        }
    }).queue([
        {
            input: "select",
            inputOptions: {
                bot: "Bot",
                website: "Website"
            },
            inputPlaceholder: "Select a source",
            inputValidator: (value) => {

                // Check if the source was from the bot or the website
                if (value === 'bot') {
                    Swal.insertQueueStep(
                        {
                            input: "text",
                            inputPlaceholder: "What command did the bug happen on?",
                            inputValidator: (value) => {
                                if (!value) { return "You must specify the command where the bug happened!"; }
                            }
                        }, 1
                    );
                } else {
                    Swal.insertQueueStep(
                        {
                            input: "text",
                            inputPlaceholder: "Where on the website did the bug happen on?",
                            inputValidator: (value) => {
                                if (!value) { return "You must specify where the bug happened!"; }
                            }
                        }, 1
                    );
                }
            }
        },
        {
            input: "textarea",
            inputPlaceholder: "Give a decent description of the bug. If you need to include steps to reproduce, please do so because it helps with finding the bug!"
        }
    ]).then((result) => {
        if(result.value) { [sourceType, source, description] = result.value; }
    })

    // Send a POST request to /reportBug to add the bug to the database
    if (sourceType && source && description) {
        $.ajax({
            url: `${BASE_URL}/reportBug`,
            type: "POST",
            data: JSON.stringify({
                sourceType: sourceType,
                source: source,
                description: description
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, let the user know their bug has been reported
        }).done(function(data) {
            Swal.fire({
                title: "Bug Reported!",
                text: `Thank you for reporting this bug. Once a developer sees it, you'll be notified through Discord as long as you allow messages from Omega Psi!`,
                icon: "success",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm'
                }
            })
    
        // If the request fails, let the user know why it failed
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
                    confirmButton: 'swal-confirm',
                    input: 'swal-input'
                }
            })
        })
    }
}

/**
 * Marks a specified bug as seen in the database
 */
function markBugAsSeen(caseNumber, ignoreSwal = false) {

    // Send a PUT request to /reportBug to update the bug to marked as seen
    $.ajax({
        url: `${BASE_URL}/reportBug`,
        type: "PUT",
        data: JSON.stringify({
            caseNumber: caseNumber
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, update the HTML elements related to the bug
    //  and let the developer know that the bug was marked as seen
    }).done(function(data) {

        // Update the bug's HTML elements
        document.getElementById(`bug${caseNumber}SeenText`).innerHTML = "Yes";
        document.getElementById(`markBug${caseNumber}Seen`).innerHTML = `Seen By ${data.developer}`;
        if (!ignoreSwal) {
            Swal.fire({
                title: "Bug Marked As Seen!",
                text: `Bug #${caseNumber} has been marked as seen`,
                icon: "success",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm'
                }
            })
        }

    // If the request fails, the bug has already been marked as seen
    }).fail(function(error) {
        if (!ignoreSwal) {
            Swal.fire({
                title: "Bug Already Seen",
                text: `Bug #${caseNumber} has already been seen by ${error.responseJSON.developer}`,
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
        }
    })
}

/**
 * Allows a developer to mark a specified bug as fixed
 */
async function fixBug(caseNumber) {

    // Mark the bug as seen
    markBugAsSeen(caseNumber, true); // This will ignore any Sweet Alert popup messages from being displayed

    // Send a PUT request to /reportBug to fix the bug
    $.ajax({
        url: `${BASE_URL}/reportBug`,
        type: "PUT",
        data: JSON.stringify({
            caseNumber: caseNumber,
            fixed: true
        }),
        contentType: "application/json; charset=utf-8"
    
    // If the request succeeds, let the developer know and update the HTML elements pertaining to the bug
    //  Also mark the bug as seen if it has not already been seen
    }).done(function(data) {

        // Update the bug's HTML elements
        document.getElementById(`bug${caseNumber}FixedText`).innerHTML = "Yes";
        Swal.fire({
            title: "Bug Marked as Fixed!",
            text: `Bug #${caseNumber} has been marked as fixed`,
            icon: "success",
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm'
            }
        })

    // If the request fails, let the developer know why it failed
    }).fail(function(error) {
        Swal.fire({
            title: "Bug Already Fixed",
            text: `Bug #${caseNumber} has already been fixed`,
            icon: "error",
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