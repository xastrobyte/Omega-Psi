/**
 * Changes the current users embed color when using Omega Psi on discord
 */
function editUserColor(originalColor) {

    // Call a POST request to /settings/user to update the user's embed color
    //  only if the color is different
    var color = document.getElementById("userColor").value;
    $.ajax({
        url: `${BASE_URL}/settings/user`,
        type: "POST",
        data: JSON.stringify({
            userColor: color
        }),
        contentType: "application/json; charset=utf-8"
    
    // If the request succeeds, let the user know the color was changed
    }).done(function(data) {
        Swal.fire({
            title: (originalColor == color)? "Nothing was changed": "Color changed",
            text: (originalColor == color)? "": `Your color was changed from "${originalColor}" to "${color}"`,
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm'
            }
        })

    // If the request fails, let the user know why
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
 * Let's the user change the prefix for Omega Psi in a specified guild
 */
async function changePrefix(guildID) {

    // Ask the user to type in a new prefix
    var originalPrefix = document.getElementById("guildPrefix").innerHTML;
    const { value: newPrefix } = await Swal.fire({
        title: "New Prefix",
        text: "Enter in a new prefix",
        input: 'text',
        inputValue: originalPrefix,
        showCancelButton: true,
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            content: 'swal-content',
            title: 'swal-title',
            confirmButton: 'swal-confirm',
            cancelButton: 'swal-confirm',
            input: 'swal-input'
        }
    })

    // Call a POST request on /settings/server to change the prefix
    if (newPrefix) {

        // Check if the last letter in the prefix is an alphabet letter, add a space to the 
        //  prefix
        lastLetter = newPrefix.charAt(newPrefix.length - 1);
        var prefix = newPrefix;
        if (lastLetter.toUpperCase() != lastLetter.toLowerCase())
            prefix = newPrefix + " ";
        $.ajax({
            url: `${BASE_URL}/settings/server`,
            type: "POST",
            data: JSON.stringify({
                guildID: guildID,
                prefix: prefix
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, let the user know and update the prefix on the settings page
        }).done(function(data) {

            document.getElementById("guildPrefix").innerHTML = prefix;
            Swal.fire({
                title: (prefix == originalPrefix)? "Nothing was changed": "Prefix changed!",
                text: (prefix == originalPrefix)? "": `The prefix was changed from "${originalPrefix}" to "${prefix}"`,
                customClass: {
                    container: 'swal-container',
                    popup: 'swal-popup',
                    content: 'swal-content',
                    title: 'swal-title',
                    confirmButton: 'swal-confirm'
                }
            })

        // If the request fails, let the user know why
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
 * Let's the user enable a command that's currently disabled
 */
function enableCommand(guildID, command) {

    // Call a PUT request on /settings/server to enable the command
    $.ajax({
        url: `${BASE_URL}/settings/server`,
        type: "PUT",
        data: JSON.stringify({
            guildID: guildID,
            enable: true,
            command: command
        }),
        contentType: "application/json; charset=utf-8"
    
    // If the request succeeds, remove/add the command to the disabled commands table
    //  and let the user know the command was enabled/disabled
    }).done(function(data) {

        // Check if there are no disabled commands, reinsert the "No Disabled Commands" text
        document.getElementById(`disabledCommand${command}`).remove();
        if (document.getElementById("disabledCommands").children.length == 0) {
            document.getElementById("disabledCommandsTable").remove();
            var p = document.createElement("p");
            p.id = "noDisabledCommands";
            var text = document.createTextNode("No Disabled Commands");
            p.appendChild(text);
            document.getElementById("disabledCommandsDiv").insertBefore(
                p,
                document.getElementById("disableCommand")
            );
        }

        Swal.fire({
            title: "Command Enabled",
            text: `The "${command}" command has been enabled!`,
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm',
                input: 'swal-input'
            }
        })

    // If the request fails, let the user know why
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
 * Let's the user choose a command to disable
 */
async function disableCommand(guildID) {

    // Get an array of all commands that are active in the specified guild
    $.ajax({
        url: `${BASE_URL}/settings/server`,
        type: "GET",
        data: {
            guildID: guildID
        },
        contentType: "application/json; charset=utf-8"
    
    // If the GET request succeeds, continue with asking the user which command to disable
    }).done(async function(data) {
        var allCommands = data;

        // Ask the user to select a command to disable
        var command;
        await Swal.fire({
            title: "Select Command",
            text: "Select a command to disable in this server",
            input: 'select',
            inputOptions: allCommands,
            customClass: {
                container: 'swal-container',
                popup: 'swal-popup',
                content: 'swal-content',
                title: 'swal-title',
                confirmButton: 'swal-confirm',
                input: 'swal-input'
            },
            inputValidator: (result) => {
                if (result) { command = allCommands[result]; }
            }
        })

        // Call a PUT request on /settings/server to disable the command
        if (command) {
            $.ajax({
                url: `${BASE_URL}/settings/server`,
                type: "PUT",
                data: JSON.stringify({
                    guildID: guildID,
                    enable: false,
                    command: command
                }),
                contentType: "application/json; charset=utf-8"
            
            // If the request succeeds, add the command to the disabled commands table
            //  and let the user know the command was disabled
            }).done(function(data) {

                // Check if disabling a command, add the disabled elements to the proper Node
                if (document.getElementById("disabledCommandsTable")) {
                    document.getElementById("disabledCommands").appendChild(createDisabledElements(guildID, command));
                } else {
                    document.getElementById("noDisabledCommands").remove();
                    document.getElementById("disabledCommandsDiv").insertBefore(
                        createDisabledElements(guildID, command, true),
                        document.getElementById("disableCommand")
                    );
                }

                Swal.fire({
                    title: "Command Disabled",
                    text: `The "${command}" command has been disabled!`,
                    customClass: {
                        container: 'swal-container',
                        popup: 'swal-popup',
                        content: 'swal-content',
                        title: 'swal-title',
                        confirmButton: 'swal-confirm',
                        input: 'swal-input'
                    }
                })

            // If the request fails, let the user know why
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

    // If the GET request fails, log it to the console
    }).fail(function(error) {
        console.log(error);
    })
    
}

/**
 * Creates the elements needed for a disabled command
 */
function createDisabledElements(guildID, command, createTable = false) {

    // Create the table
    if (createTable) {

        // Create the table, thead, tbody elements
        var table = document.createElement("table");
        table.id = "disabledCommandsTable";
        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        tbody.id = "disabledCommands";

        // Create the tr:th, and tr:td elements
        var headerTr = document.createElement("tr");
        var headerTh = document.createElement("th");
        headerTh.width = "100%";
        headerTh.innerHTML = "disabled command";
        headerTr.appendChild(headerTh);
        thead.appendChild(headerTr);

        // Add the disabled command element to the body
        tbody.appendChild(createDisabledElements(guildID, command));
        table.appendChild(thead);
        table.appendChild(tbody);
        return table;
    }

    // Only create the row for the disabled command
    else {

        // Create the tr:td element
        var tr = document.createElement("tr");
        tr.id = `disabledCommand${command}`;
        var commandCell = document.createElement("td");
        commandCell.innerHTML = command;
        var enableCell = document.createElement("td");
        var enableButton = document.createElement("button");
        enableButton.className = "page-form-button";
        enableButton.innerHTML = "Enable";
        enableButton.setAttribute("onclick", `enableCommand('${guildID}', '${command}')`);
        enableCell.appendChild(enableButton);
        tr.appendChild(commandCell);
        tr.appendChild(enableCell);
        return tr;

    }
}