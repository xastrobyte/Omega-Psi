/**
 * Asks the user to describe a new file to add to the database
 */
async function addFile() {

    // Ask the user for the file information
    //  - filename
    const { value: filename } = await Swal.fire({
        title: 'Enter the filename',
        input: 'text',
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) { return 'You need to specify the filename!'; }
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

    // Send a POST request to /fileChanges/file to add the file to the database
    if (filename) {
        $.ajax({
            url: `${BASE_URL}/fileChange/file`,
            type: "POST",
            data: JSON.stringify({
                filename: filename
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the files
        //  and let the user know that the file has been added
        }).done(function(data) {

            // Check if the fileChanges unnumbered list exists
            //  add the file to the list
            if (document.getElementById("fileChanges")) {
                document.getElementById("fileChanges").appendChild(createFileElement(data));
            }

            // The fileChanges unnumbered list does not exist
            //  create it
            else {
                document.getElementById("noFileChanges").remove();
                document.getElementById("fileChangeDiv").insertBefore(
                    createFileElement(data, true),
                    document.getElementById("addNewFile")
                );
            }

            // Let the user know the file was added
            Swal.fire({
                title: "File Added!",
                text: `"${filename}" was added to the database!`,
                icon: "success",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm',
                    input: 'swal-input'
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
 * Given an ID for a file, asks the user to update the file information
 * 
 * @param fileID The ID of the file to edit and update
 */
async function editFile(fileID) {

    // Ask the user for the new file information
    //  - filename
    var origFilename = document.getElementById(`file${fileID}File`).innerHTML;
    const { value: filename } = await Swal.fire({
        title: 'Enter the new filename',
        input: 'text',
        inputValue: origFilename,
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) {
            return 'You need to specify the filename!'
            }
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

    // Send a PUT request to /fileChanges/file to update the file in the database
    if (filename) {
        $.ajax({
            url: `${BASE_URL}/fileChange/file`,
            type: "PUT",
            data: JSON.stringify({
                fileID: fileID,
                filename: filename
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the file
        //  and let the user know that the file has been updated
        }).done(function(data) {

            // Update the file HTML
            document.getElementById(`file${fileID}File`).innerHTML = filename;

            // Let the user know the file was added
            Swal.fire({
                title: (origFilename != filename)? "File Edited!" : "Nothing was changed",
                text: (origFilename != filename)? `"${origFilename}" was changed to "${filename}"` : "",
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
 * Removes the file with the specified ID
 * 
 * @param fileID The ID of the file to find and remove
 */
function removeFile(fileID) {

    // Send a DELETE request to /fileChanges/file to remove the file from the database
    $.ajax({
        url: `${BASE_URL}/fileChange/file`,
        type: "DELETE",
        data: JSON.stringify({
            fileID: fileID
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, remove the HTML elements related to the file
    //  and let the user know that the file has been removed
    }).done(function(data) {

        // Remove the file HTML element
        document.getElementById(`file${fileID}`).remove();

        // Check if there are no files
        if (document.getElementById("fileChanges").children.length == 0) {
            document.getElementById("fileChanges").remove();
            var noFiles = document.createElement("p");
            noFiles.id = "noFileChanges";
            var noFilesText = document.createTextNode("No File Changes");
            noFiles.appendChild(noFilesText);
            document.getElementById("fileChangeDiv").insertBefore(
                noFiles,
                document.getElementById("addNewFile")
            );
        }

        // Let the user know the file was added
        Swal.fire({
            title: "File Removed!",
            text: `"${data.filename}" was removed from the file changes!`,
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

// * * * //

/**
 * Asks the user to describe a new fileChange to add to the database
 */
async function addFileChange(fileID) {

    // Ask the user for the fileChange information
    //  - change text
    const { value: change } = await Swal.fire({
        title: 'Enter the new change',
        input: 'text',
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) {
            return 'You need to specify the change!'
            }
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

    // Send a POST request to /fileChange/change to add the fileChange to the database
    if (change) {
        $.ajax({
            url: `${BASE_URL}/fileChange/change`,
            type: "POST",
            data: JSON.stringify({
                fileID: fileID,
                change: change
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the fileChanges
        //  and let the user know that the fileChange has been added
        }).done(function(data) {
            
            // Add the change elements to the table
            document.getElementById(`file${fileID}Changes`).appendChild(createChangeElement(fileID, data));

            // Let the user know that the change was added
            Swal.fire({
                title: "Change Added!",
                text: `"${change}" was added to the file!`,
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
 * Given an ID for a fileChange, asks the user to update the fileChange information
 * 
 * @param fileChangeID The ID of the file where the change is to edit and update
 * @param changeID the ID of the change to edit and update
 */
async function editFileChange(fileChangeID, changeID) {

    // Ask the user for the new fileChange information
    //  - change text
    var origChange = document.getElementById(`change${changeID}Change`).innerHTML;
    const { value: change } = await Swal.fire({
        title: 'Enter the updated change',
        input: 'text',
        inputValue: origChange,
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) { return 'You need to specify the updated change!'; }
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

    // Send a PUT request to /fileChanges/change to update the fileChange in the database
    if (change) {
         $.ajax({
            url: `${BASE_URL}/fileChange/change`,
            type: "POST",
            data: JSON.stringify({
                fileID: fileID,
                changeID: changeID,
                change: change
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the fileChange
        //  and let the user know that the fileChange has been updated
        }).done(function(data) {

            // Update the HTML element
            document.createElement(`change${change}Change`).innerHTML = change;

            // Let the user know that file change has been updated
            Swal.fire({
                title: (origChange != change)? "Change Updated!" : "Nothing was changed",
                text: (origChange != change)? `"${origChange}" was changed to "${change}"` : "",
                icon: "success",
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm',
                    input: 'swal-input'
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
 * Removes the fileChange with the specified ID
 * 
 * @param fileChangeID The ID of the fileChange to find and remove
 */
function removeFileChange(fileID, changeID) {

    // Send a DELETE request to /fileChanges/change to remove the fileChange from the database
    $.ajax({
        url: `${BASE_URL}/fileChange/change`,
        type: "DELETE",
        data: JSON.stringify({
            fileID: fileID,
            changeID: changeID
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, remove the HTML elements related to the fileChange
    //  and let the user know that the fileChange has been removed
    }).done(function(data) {

        // Remove the change
        document.getElementById(`change${changeID}`).remove();

        // Let the user know that file change has been updated
        Swal.fire({
            title: "Change Removed!",
            text: `"${data.change}" was removed as a change from the file`,
            icon: "success",
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm',
                input: 'swal-input'
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

/**
 * Creates the HTML elements that are required to view Files for file changes
 * 
 * @param file The JSON object of the file
 */
function createFileElement(fileJSON, createUnnumberedList = false) {

    // Create the listitem, table, thead, and tbody elements
    var fileListItem = document.createElement("li");
    fileListItem.id = `file${fileJSON.id}`;
    var table = document.createElement("table");
    table.width = "100%";
    var thead = document.createElement("thead");
    var tbody = document.createElement("tbody");
    tbody.id = `file${fileJSON.id}Changes`

    // Create the thead elements and the tbody elements
    var theadRow = document.createElement("tr");
    var nameCell = document.createElement("td");
    nameCell.innerHTML = fileJSON.filename;
    nameCell.id = `file${fileJSON.id}File`;
    var emptyCell = document.createElement("td");
    emptyCell.width = "80%";
    var addNewChangeCell = document.createElement("td");
    var addNewChangeButton = document.createElement("button");
    addNewChangeButton.innerHTML = "Add New Change";
    addNewChangeButton.className = "page-form-button";
    addNewChangeButton.setAttribute("onclick", `addFileChange('${fileJSON.id}')`);
    var editCell = document.createElement("td");
    var editButton = document.createElement("button");
    editButton.innerHTML = "Edit";
    editButton.className = "page-form-button";
    editButton.setAttribute("onclick", `editFile('${fileJSON.id}')`);
    var removeCell = document.createElement("td");
    var removeButton = document.createElement("button");
    removeButton.innerHTML = "Remove";
    removeButton.className = "page-form-button";
    removeButton.setAttribute("onclick", `removeFile('${fileJSON.id}')`);

    addNewChangeCell.appendChild(addNewChangeButton);
    editCell.appendChild(editButton);
    removeCell.appendChild(removeButton);

    // Add the head elements to the head theadRow and 
    //  add the headrow to the thead element
    theadRow.appendChild(nameCell);
    theadRow.appendChild(emptyCell);
    theadRow.appendChild(addNewChangeCell);
    theadRow.appendChild(editCell);
    theadRow.appendChild(removeCell);
    thead.appendChild(theadRow);

    // Add the thead and tbody to the table and the table
    //  to the listitem
    table.appendChild(thead);
    table.appendChild(tbody);
    fileListItem.appendChild(table);

    // Create and return the list if it needs to be created
    if (createUnnumberedList) { 
        var fileList = document.createElement("ul");
        fileList.id = "fileChanges";
        fileList.style = "list-style-type: none;";
        fileList.appendChild(fileListItem);
        return fileList;
    }
    return fileListItem;
}

/**
 * Creates the HTML elements that are required to view changes in a file
 * 
 * @param filename The file that the change belongs to
 * @param changeJSON The JSON object for a change in a file
 */
function createChangeElement(fileID, changeJSON) {

    // Create the tr, and td elements
    var tr = document.createElement("tr");
    tr.id = `change${changeJSON.id}`;

    var emptyCell = document.createElement("td");
    var changeCell = document.createElement("td");
    changeCell.id = `change${changeJSON.id}Change`;
    changeCell.innerHTML = changeJSON.change;
    var editCell = document.createElement("td");
    var editButton = document.createElement("button");
    editButton.innerHTML = "Edit";
    editButton.className = "page-form-button";
    editButton.setAttribute("onclick", `editFileChange('${fileID}', '${changeJSON.id}')`);

    var removeCell = document.createElement("td");
    var removeButton = document.createElement("button");
    removeButton.innerHTML = "Remove";
    removeButton.className = "page-form-button";
    removeButton.setAttribute("onclick", `removeFileChange('${fileID}', '${changeJSON.id}')`);

    // Add the td elements to the tr
    editCell.appendChild(editButton);
    removeCell.appendChild(removeButton);

    tr.appendChild(emptyCell);
    tr.appendChild(changeCell);
    tr.appendChild(editCell);
    tr.appendChild(removeCell);

    return tr;
}