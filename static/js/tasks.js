/**
 * Asks the user to describe a new task to add to the database
 */
async function addTask() {

    // Ask the user for the task information:
    //  - task text
    const { value: task } = await Swal.fire({
        title: 'Enter the new task',
        input: 'text',
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) {
            return 'You need to specify the task to add!'
            }
        },
        customClass: {
            container: 'swal-container',
            popup: 'swal-popup',
            content: 'swal-content',
            title: 'swal-title',
            confirmButton: 'swal-confirm',
            input: 'swal-input'
        }
    })

    // Send a POST request to /tasks to add the task to the database
    if (task) {
        $.ajax({
            url: `${BASE_URL}/tasks`,
            type: "POST",
            data: JSON.stringify({
                task: task
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the tasks
        //  and let the user know that the task has been added
        }).done(function(data) {

            // Check if the tasks table already exists, only add the task row
            if (document.getElementById("tasksTable")) {
                document.getElementById("tasks").appendChild(createTaskElements(data));
            }

            // The tasks table does not exist, create it and add the task
            else {
                document.getElementById("noTasks").remove();
                document.getElementById("tasksDiv").insertBefore(
                    createTaskElements(data, true),
                    document.getElementById("addNewTask")
                );
            }

            // Let the user know the task was added
            Swal.fire({
                title: "Task Created!",
                text: `"${task}" has been added to the tasklist.`,
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
 * Given an ID for a task, asks the user to update the task information
 * 
 * @param taskID The ID of the task to edit and update
 */
async function editTask(taskID) {

    // Ask the user for the new task information:
    //  - task text
    var origTask = document.getElementById(`task${taskID}Task`).innerHTML;
    const { value: task } = await Swal.fire({
        title: 'Update the task',
        input: 'text',
        inputValue: origTask,
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) {
            return 'You need to specify the task!'
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

    // Send a PUT request to /tasks to update the task in the database
    if (task) {
        $.ajax({
            url: `${BASE_URL}/tasks`,
            type: "PUT",
            data: JSON.stringify({
                taskID: taskID,
                task: task
            }),
            contentType: "application/json; charset=utf-8"

        // If the request succeeds, update the HTML elements related to the tasks
        //  and let the user know that the task has been added
        }).done(function(data) {

            // Update the task HTML element
            document.getElementById(`task${taskID}Task`).innerHTML = task;

            // Let the user know the task was added
            Swal.fire({
                title: (origTask != task) ? "Task Updated!" : "Nothing was changed",
                text: (origTask != task) ? `"${origTask}" has been changed to "${task}"` : "",
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
 * Removes the task with the specified ID
 * 
 * @param taskID The ID of the task to find and remove
 */
function removeTask(taskID) {

    // Send a DELETE request to /tasks to remove the task from the database
    $.ajax({
        url: `${BASE_URL}/tasks`,
        type: "DELETE",
        data: JSON.stringify({
            taskID: taskID
        }),
        contentType: "application/json; charset=utf-8"

    // If the request succeeds, remove the HTML elements related to the task
    //  and let the user know that the task has been removed
    }).done(function(data) {

        // Remove the HTML elements
        document.getElementById(`task${taskID}`).remove();

        // Check if the tasks has no children, remove the tasks table and add "noTasks" <p> element
        if (document.getElementById("tasks").children.length == 0) {
            document.getElementById("tasksTable").remove();
            var noTasks = document.createElement("p");
            noTasks.id = "noTasks";
            var noTasksText = document.createTextNode("No Tasks Yet");
            noTasks.appendChild(noTasksText);
            document.getElementById("tasksDiv").insertBefore(
                noTasks,
                document.getElementById("addNewTask")
            )
        }

        // Let the user know the task was removed
        Swal.fire({
            title: "Task Removed!",
            text: `"${data.task}" was removed from the tasklist.`,
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
 * Creates the HTML elements needed to view tasks
 * 
 * @param task The task that is being added
 * @param createTable Whether or not to create the tasksTable
 */
function createTaskElements(task, createTable = false) {

    // Check if the table needs to be created
    if (createTable) {

        // Create the <table>, <thead>, and <tbody> elements
        var table = document.createElement("table");
        table.id = "tasksTable";
        table.width = "100%";

        var thead = document.createElement("thead");
        var tbody = document.createElement("tbody");
        tbody.id = "tasks";

        var headers = document.createElement("tr");

        var taskHeader = document.createElement("th");
        taskHeader.innerHTML = "Task";
        taskHeader.width = "100%";

        // Add the headers to the header, the header to the thead, and the thead to the table
        headers.appendChild(taskHeader);
        thead.appendChild(headers);
        tbody.appendChild(createTaskElements(task));
        table.appendChild(thead);
        table.appendChild(tbody);

        return table;
    }

    // The table does not need to be created
    else {
        
        // Create the <tr> and <td>s
        var tr = document.createElement("tr");
        tr.id = `task${task.id}`;

        var taskColumn = document.createElement("td");
        taskColumn.id = `task${task.id}Task`;
        taskColumn.innerHTML = task.task;
        var editColumn = document.createElement("td");
        var editButton = document.createElement("button");
        editButton.innerHTML = "Edit";
        editButton.className = "page-form-button";
        editButton.setAttribute("onclick", `editTask('${task.id}')`);
        editColumn.appendChild(editButton);
        var removeColumn = document.createElement("td");
        var removeButton = document.createElement("button");
        removeButton.innerHTML = "Remove";
        removeButton.className = "page-form-button";
        removeButton.setAttribute("onclick", `removeTask('${task.id}')`)
        removeColumn.appendChild(removeButton);

        // Add the <td>s to the <tr>
        tr.appendChild(taskColumn);
        tr.appendChild(editColumn);
        tr.appendChild(removeColumn);

        return tr;
    }
}