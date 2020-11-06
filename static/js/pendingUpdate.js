/**
 * Creates a new pending update in Omega Psi if one does not already exist
 */
function createUpdate() {

    // Send a POST request to /pendingUpdate to create a new pending update
    $.ajax({
        url: `${BASE_URL}/pendingUpdate`,
        type: "POST",
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, update the HTML elements related to the pending update
    //  and let the user know the update was created
    }).done(function(data) {

        // Create the "No Features Yet" text and the "Add New Feature" and "Commit Update" button
        var p = document.createElement("p");
        p.id = "noFeatures";
        var textNode = document.createTextNode("No Features Yet");
        p.appendChild(textNode);

        var button = document.createElement("button");
        button.id = "addNewFeature";
        button.className = "page-form-button";
        button.setAttribute("onclick", "addFeature()");
        button.innerHTML = "Add New Feature";

        // Clear the pending update div and add the html elements
        document.getElementById("noPendingUpdate").remove();
        document.getElementById("createUpdate").remove();
        document.getElementById("pendingUpdateDiv").appendChild(p);
        document.getElementById("pendingUpdateDiv").appendChild(button);

        // Let the user know the update was created
        Swal.fire({
            title: "Pending Update Created!",
            text: "A new pending update has been created. Use the Add New Feature buttons to add a feature to the update.",
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
                confirmButton: 'swal-confirm'
            }
        })
    })
}

/**
 * Asks the user to provide a version number and a description of a new
 * update to send to the bot
 */
async function commitUpdate() {

    // Ask the user for the update information:
    //  - version number
    //  - version description
    var version, description;
    await Swal.mixin({
        title: "Commit Update",
        input: 'text',
        confirmButtonText: "Next &rarr;",
        showCancelButton: true,
        progressSteps: ['1', '2'],
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
            inputPlaceholder: "Enter the version",
            inputValidator: (value) => {
                if (!value) { return "You need to specify the version number!"; }
            }
        },
        {
            inputPlaceholder: "Description of the update",
            inputValidator: (value) => {
                if (!value) { return "You must specify a description of the version!"; }
            }
        }
    ]).then((result) => {
        if(result.value) { [version, description] = result.value; }
    })

    // Send a PUT request to /pendingUpdate/commit to commit the update
    if (version && description) {
        $.ajax({
            url: `${BASE_URL}/pendingUpdate/commit`,
            type: "POST",
            data: JSON.stringify({
                version: version,
                description: description
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the pending update
        //  and let the user know the update was committed
        }).done(function(data) {

            // Clear the pending update div
            document.getElementById("featuresTable").remove();
            document.getElementById("addNewFeature").remove();
            document.getElementById("commitUpdate").remove();
            var p = document.createElement("p");
            p.id = "noPendingUpdate";
            var textNode = document.createTextNode("No Pending Update");
            p.appendChild(textNode);

            var button = document.createElement("button");
            button.className = "page-form-button";
            button.id = "createUpdate";
            button.setAttribute("onclick", "createUpdate()");
            button.innerHTML = "Create Update";

            // Update the pending update div with the text and button
            //  to create a new update
            document.getElementById("pendingUpdateDiv").appendChild(p);
            document.getElementById("pendingUpdateDiv").appendChild(button);

            Swal.fire({
                title: "Update Committed!",
                text: `Version ${version} has been committed to Omega Psi!`,
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
}

// * * * //

/**
 * Asks the user to describe a new feature to add to the database
 */
async function addFeature() {

    // Ask the user for the feature information:
    //  - feature text
    //  - feature type
    var feature, featureType;
    await Swal.mixin({
        title: 'New Feature',
        confirmButtonText: "Next &rarr;",
        showCancelButton: true,
        progressSteps: ['1', '2'],
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
            input: "text",
            inputPlaceholder: "Enter the feature",
            inputValidator: (value) => {
                if (!value) { return "You need to specify the new feature!"; }
            }
        },
        {
            input: 'select',
            inputOptions: {
                added: "Added",
                removed: "Removed",
                changed: "Changed",
                deprecated: "Deprecated",
                fixed: "Fixed",
                security: "Security"
            },
            inputPlaceholder: "What type of feature is this?",
            inputValidator: (value) => {
                if (!value) { return "You must specify the type of feature this is!"; }
            }
        }
    ]).then((result) => {
        if(result.value) { [feature, featureType] = result.value; }
    })

    // Send a POST request to /pendingUpdate/feature to add the feature to the database
    if (feature && featureType) {
        $.ajax({
            url: `${BASE_URL}/pendingUpdate/feature`,
            type: "POST",
            data: JSON.stringify({
                feature: feature,
                featureType: featureType
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the features
        //  and let the user know that the feature has been added
        }).done(function(data) {

            // Check if there is already a features table, only add the new feature to the table
            if (document.getElementById("featuresTable")) {
                element = createFeatureElements(data);
                document.getElementById("features").appendChild(element);
            }

            // There is no features table, add it to the pendingUpdateDiv
            else {
                document.getElementById("noFeatures").remove();
                document.getElementById("pendingUpdateDiv").insertBefore(
                    createFeatureElements(data, true),
                    document.getElementById("addNewFeature")
                );
            }

            // Let the user know that the feature has been added
            Swal.fire({
                title: "Feature Added!",
                text: `"${feature}" has been added as a feature`,
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
}

/**
 * Given an ID for a feature, asks the user to update the feature information
 * 
 * @param featureID The ID of the feature to edit and update
 * @param feature The current value of the feature
 */
async function editFeature(featureID) {

    // Ask the user for the new feature information:
    // - feature text
    // - feature type
    var origFeature = document.getElementById(`feature${featureID}Feature`).innerHTML;
    var origFeatureType = document.getElementById(`feature${featureID}Type`).innerHTML;
    var feature, featureType;
    await Swal.mixin({
        title: 'New Feature',
        confirmButtonText: "Next &rarr;",
        showCancelButton: true,
        progressSteps: ['1', '2'],
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
            input: "text",
            inputValue: origFeature,
            inputPlaceholder: "Enter the feature",
            inputValidator: (value) => {
                if (!value) { return "You need to specify the feature!"; }
            }
        },
        {
            input: 'select',
            inputValue: origFeatureType,
            inputOptions: {
                added: "Added",
                removed: "Removed",
                changed: "Changed",
                deprecated: "Deprecated",
                fixed: "Fixed",
                security: "Security"
            },
            inputPlaceholder: "What type of feature is this?",
            inputValidator: (value) => {
                if (!value) { return "You must specify the type of feature this is!"; }
            }
        }
    ]).then((result) => {
        if(result.value) { [feature, featureType] = result.value; }
    })

    // Send a POST request to /pendingUpdate/feature to update the feature in the database
    if (feature && featureType) {
        $.ajax({
            url: `${BASE_URL}/pendingUpdate/feature`,
            type: "PUT",
            data: JSON.stringify({
                featureID: featureID,
                feature: feature,
                featureType: featureType
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the feature
        //  and let the user know that the feature has been updated
        }).done(function(data) {

            // Update the feature column and type column
            document.getElementById(`feature${data.id}Feature`).innerHTML = feature;
            document.getElementById(`feature${data.id}Type`).innerHTML = featureType;

            // Let the user know the feature was changed and what aspects changed
            var changedResults = "";
            if (origFeature != feature && origFeatureType != featureType) { changedResults = `"${origFeature}" was changed to "${feature}" and the type was changed from "${origFeatureType}" to "${featureType}"`; }
            else if (origFeature != feature) { changedResults = `"${origFeature}" was changed to "${feature}"`; }
            else if (origFeatureType != featureType) { changedResults = `The type was changed from "${origFeatureType}" to "${featureType}"`; }
            
            // If nothing is changed, let them know
            else {
                Swal.fire({
                    title: "Nothing Was Changed",
                    icon: "success",
                    customClass: {
                        container: 'swal-container',
                        popup: 'swal-popup',
                        content: 'swal-content',
                        title: 'swal-title',
                        confirmButton: 'swal-confirm'
                    }
                })
                return;
            }

            // Something was changed
            Swal.fire({
                title: "Feature Changed!",
                text: changedResults,
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
}

/**
 * Removes the feature with the specified ID
 * 
 * @param featureID The ID of the feature to find and remove
 */
function removeFeature(featureID) {

    // Send a DELETE request to /pendingUpdate/feature to remove the feature from the database
    $.ajax({
        url: `${BASE_URL}/pendingUpdate/feature`,
        type: "DELETE",
        data: JSON.stringify({
            featureID: featureID
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, remove the HTML elements related to the feature
    //  and let the user know that the feature has been removed
    }).done(function(data) {

        // Remove the row of the feature and let the user know it was removed
        document.getElementById(`feature${featureID}`).remove();
        if (document.getElementById("features").children.length == 0) {
            document.getElementById("featuresTable").remove();
            var p = document.createElement("p");
            p.id = "noFeatures";
            var textNode = document.createTextNode("No Features Yet");
            p.appendChild(textNode);

            document.getElementById("pendingUpdateDiv").insertBefore(
                p,
                document.getElementById("addNewFeature")
            );
        }

        // Let the user know that the feature has been removed
        Swal.fire({
            title: "Feature Removed!",
            text: `"${data.feature}" has been removed as a feature`,
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

/**
 * Creates the features table or the feature object to add to the pending update
 * If the feature is null, a table is created
 * 
 * @param feature The feature to add
 * @param createTable Whether or not to create the table
 */
function createFeatureElements(feature, createTable = false) {

    // Check if the table needs to be created
    if (createTable) {

        // Create the <table>, <thead>, and <tbody> elements
        var table = document.createElement("table");
        table.id = "featuresTable";
        table.width = "100%";

        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        tbody.id = "features";

        var headers = document.createElement("tr");

        var featureHeader = document.createElement("th");
        featureHeader.innerHTML = "Feature";
        featureHeader.width = "92%";
        var typeHeader = document.createElement("th");
        typeHeader.innerHTML = "Type";
        typeHeader.width = "8%";
        var dateHeader = document.createElement("th");
        dateHeader.innerHTML = "Date";

        // Add the headers to the header, the header to the thead, and the thead to the table
        headers.appendChild(featureHeader);
        headers.appendChild(typeHeader);
        headers.appendChild(dateHeader);
        thead.appendChild(headers);
        tbody.appendChild(createFeatureElements(feature));
        table.appendChild(thead);
        table.appendChild(tbody);

        return table;
    }

    // The table does not need to be created, only create the row
    else {

        // Create the <tr> and <td>s
        var tr = document.createElement("tr");
        tr.id = `feature${feature.id}`;

        var featureColumn = document.createElement("td");
        featureColumn.id = `feature${feature.id}Feature`
        featureColumn.innerHTML = feature.feature;
        var typeColumn = document.createElement("td");
        typeColumn.id = `feature${feature.id}Type`
        typeColumn.innerHTML = feature.type;
        var dateColumn = document.createElement("td");
        dateColumn.id = `feature${feature.id}Date`
        dateColumn.innerHTML = feature.datetime;
        var editColumn = document.createElement("td");
        var editButton = document.createElement("button");
        editButton.innerHTML = "Edit";
        editButton.className = "page-form-button";
        editButton.setAttribute("onclick", `editFeature('${feature.id}')`);
        editColumn.appendChild(editButton);
        var removeColumn = document.createElement("td");
        var removeButton = document.createElement("button");
        removeButton.innerHTML = "Remove";
        removeButton.className = "page-form-button";
        removeButton.setAttribute("onclick", `removeFeature('${feature.id}')`)
        removeColumn.appendChild(removeButton);

        // Add the <td>s to the <tr>
        tr.appendChild(featureColumn);
        tr.appendChild(typeColumn);
        tr.appendChild(dateColumn);
        tr.appendChild(editColumn);
        tr.appendChild(removeColumn);

        return tr;
    }
}