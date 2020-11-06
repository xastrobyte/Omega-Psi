def get_case_html(is_bugs):
    """Retrieves the 
    """
    if is_bugs:
        return (
            """
                            <!--Case Section-->
                            <h2 class="page-section">
                                <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">bugs</code><code>();</code>
                            </h2>
                            <div class="page-section-block">
                            {% if bug_cases|length == 0 %}
                                <h3>No Bugs Found</3>
                            {% else %}
                                <div class="cases-box">
                                    <table class="case-table">
                                        <thead>
                                            <tr>
                                                <th width="5%">Number</th>
                                                <th width="15%">Website or Bot?</th>
                                                <th width="20%">Source</th>
                                                <th width="35%">Description</th>
                                                <th width="15%">Reporter</th>
                                                <th width="5%">Seen?</th>
                                                <th width="5%">Fixed?</th>
                                                <th></th>
                                                <th></th>
                                            <tr>
                                        </thead>
                                        <tbody>
                                            {% for case in bug_cases -%}
                                                <tr>
                                                    <td>#{{ case }}</td>
                                                    <td>{{ bug_cases[case]["source_type"] }}</td>
                                                    <td>{{ bug_cases[case]["source"] }}</td>
                                                    <td>{{ bug_cases[case]["bug"] }}</td>
                                                    <td>{{ bug_cases[case]["author"] }}</td>
                                                    <td id="bug{{ case }}SeenText">
                                                        {% if bug_cases[case]["seen"] %}
                                                            Yes
                                                        {% else %}
                                                            No
                                                        {% endif %}
                                                    </td>
                                                    <td id="bug{{ case }}FixedText">
                                                        {% if bug_cases[case]["fixed"] %}
                                                            Yes
                                                        {% else %}
                                                            No
                                                        {% endif %}
                                                    </td>
                                                    <td><button id="fixBug{{ case }}" type="button" class="page-form-button" onclick="fixBug({{ case }})">Fix</button></td>
                                                    <td>
                                                        {% if bug_cases[case]["seen"] %}
                                                            <button id="markBug{{ case }}Seen" type="button" class="page-form-button" onclick="markBugAsSeen({{ case }})">Seen By {{ bug_cases[case]["seen"] }}</button>
                                                        {% else %}
                                                            <button id="markBug{{ case }}Seen" type="button" class="page-form-button" onclick="markBugAsSeen({{ case }})">Mark As Seen</button>
                                                        {% endif %}
                                                    </td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            {% endif %}
                            </div>
            """
        )
    return (
        """
                        <!--Case Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">suggestions</code><code>();</code>
                        </h2>
                        <div class="page-section-block">
                        {% if suggestion_cases|length == 0 %}
                            <h3>No Suggestions Found</3>
                        {% else %}
                            <div class="cases-box">
                                <table class="case-table">
                                    <thead>
                                        <tr>
                                            <th width="10%">Number</th>
                                            <th width="45%">Description</th>
                                            <th width="15%">Suggester</th>
                                            <th width="5%">Seen?</th>
                                            <th width="5%">Considered?</th>
                                            <th width="45%">Reason</th>
                                            <th></th>
                                            <th></th>
                                        <tr>
                                    </thead>
                                    <tbody>
                                        {% for case in suggestion_cases -%}
                                            <tr>
                                                <td>#{{ case }}</td>
                                                <td>{{ suggestion_cases[case]["suggestion"] }}</td>
                                                <td>{{ suggestion_cases[case]["author"] }}</td>
                                                <td id="suggestion{{ case }}SeenText">
                                                    {% if suggestion_cases[case]["seen"] %}
                                                        Yes
                                                    {% else %}
                                                        No
                                                    {% endif %}
                                                </td>
                                                <td id="suggestion{{ case }}ConsideredText">
                                                    {% if not suggestion_cases[case]["consideration"] %}
                                                        Not Yet
                                                    {% else %}
                                                        {% if suggestion_cases[case]["consideration"]["considered"] %}
                                                            Yes
                                                        {% else %}
                                                            No
                                                        {% endif %}
                                                    {% endif %}
                                                </td>
                                                <td id="suggestion{{ case }}ReasonText">
                                                    {% if not suggestion_cases[case]["consideration"] %}
                                                        None Yet
                                                    {% else %}
                                                        {% if suggestion_cases[case]["consideration"]["considered"] %}
                                                            N/A
                                                        {% else %}
                                                            {{ suggestion_cases[case]["consideration"]["reason"] }}
                                                        {% endif %}
                                                    {% endif %}
                                                </td>
                                                <td><button id="considerSuggestion{{ case }}" type="button" class="page-form-button" onclick="considerSuggestion({{ case }})">Consider/Don't Consider</button></td>
                                                <td>
                                                    {% if suggestion_cases[case]["seen"] %}
                                                        <button id="markSuggestion{{ case }}Seen" type="button" class="page-form-button" onclick="markSuggestionAsSeen({{ case }})">Seen By {{ suggestion_cases[case]["seen"] }}</button>
                                                    {% else %}
                                                        <button id="markSuggestion{{ case }}Seen" type="button" class="page-form-button" onclick="markSuggestionAsSeen({{ case }})">Mark As Seen</button>
                                                    {% endif %}
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% endif %}
                        </div>
        """
    )
    
def get_pending_update_html(on_developer_page = True):
    if on_developer_page:
        return (
            """
                            <!--Pending Update Section-->
                            <h2 class="page-section">
                                <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">pendingUpdate</code><code>();</code>
                            </h2>
                            <div id="pendingUpdateDiv" class="page-section-block" style="text-align: center;">
                                {% if pending_update == None %}
                                    <p id="noPendingUpdate">No Pending Update</p>
                                    <button id="createUpdate" class="page-form-button" onclick="createUpdate()">Create Update</button>
                                {% else %}
                                    {% if pending_update["features"]|length == 0 %}
                                        <p id="noFeatures">No Features Yet</p>
                                        <button id="createUpdate" class="page-from-button">Create Update</button>
                                    {% else %}
                                        <div class="cases-box">
                                            <table id="featuresTable" class="case-table" width="100%">
                                                <thead>
                                                    <tr>
                                                        <th width="92%">Feature</th>
                                                        <th width="8%">Type</th>
                                                        <th>Date</th>
                                                        <th></th>
                                                        <th></th>
                                                    </tr>
                                                </thead>
                                                <tbody id="features">
                                                    {% for feature in pending_update["features"] -%}
                                                        <tr id="feature{{ feature }}">
                                                            <td id="feature{{ feature }}Feature">{{ pending_update["features"][feature]["feature"] }}</td>
                                                            <td id="feature{{ feature }}Type">{{ pending_update["features"][feature]["type"] }}</td>
                                                            <td>{{ pending_update["features"][feature]["human_time"] }}</td>
                                                            <td><button class="page-form-button" onclick="editFeature('{{ feature }}')">Edit</button></td>
                                                            <td><button class="page-form-button" onclick="removeFeature('{{ feature }}')">Remove</button></td>
                                                        </tr>
                                                    {% endfor %}
                                                </tbody>
                                            </table>
                                        </div>
                                    {% endif %}
                                    <button id="addNewFeature" class="page-form-button" onclick="addFeature()">Add New Feature</button>
                                    <button id="commitUpdate" class="page-form-button" onclick="commitUpdate()">Commit Update</button>
                                {% endif %}
                            </div>
            """
        )
    return (
        """
                        <!--Pending Update Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">pendingUpdate</code><code>();</code>
                        </h2>
                        <div id="pendingUpdateDiv" class="page-section-block" style="text-align: center;">
                            {% if pending_update == None %}
                                <p>No Pending Update</p>
                            {% else %}
                                {% if pending_update["features"]|length == 0 %}
                                    <p id="noFeatures">No Features</p>
                                {% else %}
                                    <div class="cases-box">
                                        <table id="featuresTable" class="case-table" width="100%">
                                            <thead>
                                                <tr>
                                                    <th width="92%">Feature</th>
                                                    <th width="8%">Type</th>
                                                    <th>Date</th>
                                                </tr>
                                            </thead>
                                            <tbody id="features">
                                                {% for feature in pending_update["features"] -%}
                                                    <tr id="feature{{ feature }}">
                                                        <td id="feature{{ feature }}Feature">{{ pending_update["features"][feature]["feature"] }}</td>
                                                        <td id="feature{{ feature }}Type">{{ pending_update["features"][feature]["type"] }}</td>
                                                        <td>{{ pending_update["features"][feature]["human_time"] }}</td>
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                {% endif %}
                            {% endif %}
                        </div>
        """
    )

def get_tasks_html(for_feedback_page = False):
    if not for_feedback_page:
        return (
            """
                            <!--Tasklist Section-->
                            <h2 class="page-section">
                                <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">tasks</code><code>();</code>
                            </h2>
                            <div id="tasksDiv" class="page-section-block" style="text-align: center;">
                                <p>below is the current tasklist that developers intend to complete</p>
                                {% if tasks == None %}
                                    <p id="noTasks">No Tasks Yet</p>
                                {% else %}
                                    <div class="cases-box">
                                        <table id="tasksTable" width="100%">
                                            <thead>
                                                <tr>
                                                    <th width="100%">Task</th>
                                                </tr>
                                            </thead>
                                            <tbody id="tasks">
                                                {% for taskID in tasks -%}
                                                    <tr id ="task{{ taskID }}">
                                                        <td id="task{{ taskID }}Task">{{ tasks[taskID] }}</td>
                                                        <td><button class="page-form-button" onclick="editTask('{{ taskID }}')">Edit</button</td>
                                                        <td><button class="page-form-button" onclick="removeTask('{{ taskID }}')">Remove</button></td>
                                                    </tr>
                                                {% endfor %}
                                            </tbody>
                                        </table>
                                    </div>
                                {% endif %}
                                <button id="addNewTask" class="page-form-button" onclick="addTask()">Add New Task</button>
                            </div>
            """
        )
    return (
        """
                        <!--Tasklist Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">tasks</code><code>();</code>
                        </h2>
                        <div id="tasklistDiv" class="page-section-block" style="text-align: center;">
                            <p>below is the current tasklist that developers intend to complete</p>
                            {% if tasks == None %}
                                <p id="noTasks">The Tasklist Is Empty</p>
                            {% else %}
                                <div class="cases-box">
                                    <table id="tasksTable">
                                        <thead>
                                            <tr>
                                                <th>Task</th>
                                            </tr>
                                        </thead>
                                        <tbody id="tasks">
                                            {% for taskID in tasks -%}
                                                <tr id ="task{{ taskID }}">
                                                    <td>{{ tasks[taskID] }}</td>
                                                </tr>
                                            {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            {% endif %}
                        </div>
        """
    )

def get_bot_settings_html(settings):
    if settings == "disabledCommands":
        return (
            """
                        <!--Disabled Commands Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">disabledCommands</code><code>();</code>
                        </h2>
                        <div id="disabledCommandsDiv" class="page-section-block" style="text-align: center;">
                            {% if disabled_commands|length == 0 %}
                                <p id="noDisabledCommands">No Disabled Commands</p>
                            {% else %}
                                <div class="cases-box">
                                    <table id="disabledCommandsTable" width="100%">
                                        <thead>
                                            <tr>
                                                <th width="100%">disabled command</th>
                                                <th></th>
                                            </tr>
                                        </thead>
                                        <tbody id="disabledCommands">
                                        {% for command in disabled_commands -%}
                                            <tr id="disabledCommand{{ command }}">
                                                <td>{{ command }}</td>
                                                <td><button class="page-form-button" onclick="globallyEnableCommand('{{ command }}')">Enable</button>
                                            </tr>
                                        {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            {% endif %}
                            <button id="disableCommand" class="page-form-button" onclick="globallyDisableCommand({{ all_commands }})">Disable Command</button>
                        </div>
            """
        )
    
    elif settings == "disabledCogs":
        return (
            """
                        <!--Disabled Cogs Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">disabledCogs</code><code>();</code>
                        </h2>
                        <div id="disabledCogsDiv" class="page-section-block" style="text-align: center;">
                            {% if disabled_cogs|length == 0 %}
                                <p id="noDisabledCogs">No Disabled Cogs</p>
                            {% else %}
                                <div class="cases-box">
                                    <table id="disabledCogsTable" width="100%">
                                        <thead>
                                            <tr>
                                                <th width="100%">disabled cog</th>
                                                <th></th>
                                            </tr>
                                        </thead>
                                        <tbody id="disabledCogs">
                                        {% for cog in disabled_cogs -%}
                                            <tr id="disabledCog{{ cog }}">
                                                <td>{{ cog }}</td>
                                                <td><button class="page-form-button" onclick="globallyEnableCog('{{ cog }}')">Enable</button>
                                            </tr>
                                        {% endfor %}
                                        </tbody>
                                    </table>
                                </div>
                            {% endif %}
                            <button id="disableCog" class="page-form-button" onclick="globallyDisableCog({{ all_cogs }})">Disable Cog</button>
                        </div>
            """
        )

def get_feedback_html():
    return (
        """
                        <!--Feedback Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">feedback</code><code>();</code>
                        </h2>
                        <div id="feedbackDiv" class="page-section-block" style="text-align: center;">
                            <p>if you found a bug, you can <button class=\"page-form-button\" onclick=\"reportBug()\">report</button> it.</p>
                            <p>if you'd like to make a suggestion, you can <button class=\"page-form-button\" onclick=\"suggest()\">suggest</button> something!</p>
                        </div>
        """
    )

def get_server_settings_html(view_guild = False, section = None):

    # If a guild ID is given, the user is editing a specific guild
    if view_guild:
        if section == "prefix":
                return (
                    """
                        <!--Guild Prefix Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">prefix</code><code>();</code>
                        </h2>
                        <div class="page-section-block" style="text-align: center;">
                            <p>The prefix for {{ guild.name }} is currently <code id="guildPrefix" class="field">{{ guild_prefix }}</code></br>
                            you can <button class="page-form-button" onclick="changePrefix('{{ guild.id }}')">change it here</button></p>
                        </div>
                    """
                )
        elif section == "disabledCommands":
            return (
                """
                    <!--Guild Disabled Commands Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">disabledCommands</code><code>();</code>
                        </h2>
                        <div id="disabledCommandsDiv" class="page-section-block" style="text-align: center;">
                            {% if disabled_commands|length == 0 %}
                                <p id="noDisabledCommands">No Disabled Commands</p>
                            {% else %}
                                <table id="disabledCommandsTable" width="100%">
                                    <thead>
                                        <tr>
                                            <th width="100%">disabled command</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    <tbody id="disabledCommands">
                                    {% for command in disabled_commands -%}
                                        <tr id="disabledCommand{{ command }}">
                                            <td>{{ command }}</td>
                                            <td><button class="page-form-button" onclick="enableCommand('{{ guild.id }}', '{{ command }}')">Enable</button>
                                        </tr>
                                    {% endfor %}
                                    </tbody>
                                </table>
                            {% endif %}
                            <button id="disableCommand" class="page-form-button" onclick="disableCommand('{{ guild.id }}', {{ all_commands }})">Disable Command</button>
                        </div>
                """
            )
        
    # If guild ID is NOT given, the user is looking at which guilds they can manage on the /settings page
    return (
        """
                        <!--Manage Guilds Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">servers</code><code>();</code>
                        </h2>
                        <div class="page-section-block" style="text-align: center;">
                            <p>here's where you can change Omega Psi's settings in servers you manage</p>
                            {% if manageable_guilds|length != 0 %}
                                <table width="100%">
                                    <thead>
                                        <tr>
                                            <th width="75%">Server Name</th>
                                            <th width="25%">Server ID</th>
                                            <th></th>
                                        </tr>
                                    </thead>
                                    {% for guild in manageable_guilds -%}
                                        <tr>
                                            <td>{{ guild.name }}</td>
                                            <td>{{ guild.id }}</td>
                                            <td><input type="button" class="page-form-button" onclick="window.location.href='/server/{{ guild.id }}'" value="Edit"></td>
                                        </tr>
                                    {% endfor %}
                                </table>
                            {% else %}
                                you don't have <code class="field">manage server</code> permissions in any servers that Omega Psi is in :(
                            {% endif %}
                        </div>
        """
    )

def get_user_settings_html():
    return (
        """
                        <!--User Settings Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">settings</code><code>();</code>
                        </h2>
                        <div class="page-section-block" style="text-align: center;">
                            <p>change your own personal settings here!</p>
                            <div class="cases-box">
                                <table width="100%">
                                    <tbody>
                                        <tr>
                                            <td width="100%">change your embed color when using omega psi</td>
                                            <td><input id="userColor" type="color" style="background-color: #293134; border: 1px solid #808080; border-radius: 5px;" value="#{{ user_color }}" onchange="editUserColor('{{ user_color }}')"></td>
                                        </tr>
                                        {% for target in notification_data -%}
                                            <tr>
                                                <td width="100%">{{ notification_descriptions[target] }}</td>
                                                <td><label class="switch">
                                                    <input id="{{ target }}Checkbox" type="checkbox" oninput="manageNotifications(`{{ target }}`)"
                                                    {% if notification_data[target]["active"] %}
                                                        checked
                                                    {% endif %}
                                                    >
                                                    <span class="slider"></span>
                                                </label></td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>

                        <!--Gamestats Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">gamestats</code><code>();</code>
                        </h2>
                        <div class="page-section-block" style="text-align: center;">
                            <table width="100%">
                                <thead>
                                    <tr>
                                        <th width="50%">Minigame</th>
                                        <th width="15%">Wins</th>
                                        <th width="15%">Losses</th>
                                        <th width="20%">Ratio</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for minigame in minigames -%}
                                        <tr>
                                            <td>{{ minigame }}</td>
                                            <td>{{ minigames[minigame]["won"] }}</td>
                                            <td>{{ minigames[minigame]["lost"] }}</td>
                                            <td>{{ minigames[minigame]["ratio"] }}</td>
                                        </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>

                        <!--Case Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">yourBugs</code><code>();</code>
                        </h2>
                        <div class="page-section-block">
                        {% if bug_cases|length == 0 %}
                            <h3>No Bugs Found</3>
                        {% else %}
                            <div class="cases-box">
                                <table class="case-table">
                                    <thead>
                                        <tr>
                                            <th width="5%">Number</th>
                                            <th width="15%">Website or Bot?</th>
                                            <th width="20%">Source</th>
                                            <th width="35%">Description</th>
                                            <th width="15%">Reporter</th>
                                            <th width="5%">Seen?</th>
                                            <th width="5%">Fixed?</th>
                                        <tr>
                                    </thead>
                                    <tbody>
                                        {% for case in bug_cases -%}
                                            <tr>
                                                <td>#{{ case }}</td>
                                                <td>{{ bug_cases[case]["source_type"] }}</td>
                                                <td>{{ bug_cases[case]["source"] }}</td>
                                                <td>{{ bug_cases[case]["bug"] }}</td>
                                                <td>{{ bug_cases[case]["author"] }}</td>
                                                <td id="bug{{ case }}SeenText">
                                                    {% if bug_cases[case]["seen"] %}
                                                        Yes
                                                    {% else %}
                                                        No
                                                    {% endif %}
                                                </td>
                                                <td id="bug{{ case }}FixedText">
                                                    {% if bug_cases[case]["fixed"] %}
                                                        Yes
                                                    {% else %}
                                                        No
                                                    {% endif %}
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% endif %}
                        </div>

                        <!--Suggestion Section-->
                        <h2 class="page-section">
                            <span class="section-name"><code class="field">page</code><code>.</code></span><code class="field">yourSuggestions</code><code>();</code>
                        </h2>
                        <div class="page-section-block">
                        {% if suggestion_cases|length == 0 %}
                            <h3>No Suggestions Found</3>
                        {% else %}
                            <div class="cases-box">
                                <table class="case-table">
                                    <thead>
                                        <tr>
                                            <th width="10%">Number</th>
                                            <th width="45%">Description</th>
                                            <th width="15%">Suggester</th>
                                            <th width="5%">Seen?</th>
                                            <th width="5%">Considered?</th>
                                            <th width="45%">Reason</th>
                                        <tr>
                                    </thead>
                                    <tbody>
                                        {% for case in suggestion_cases -%}
                                            <tr>
                                                <td>#{{ case }}</td>
                                                <td>{{ suggestion_cases[case]["suggestion"] }}</td>
                                                <td>{{ suggestion_cases[case]["author"] }}</td>
                                                <td id="suggestion{{ case }}SeenText">
                                                    {% if suggestion_cases[case]["seen"] %}
                                                        Yes
                                                    {% else %}
                                                        No
                                                    {% endif %}
                                                </td>
                                                <td id="suggestion{{ case }}ConsideredText">
                                                    {% if not suggestion_cases[case]["consideration"] %}
                                                        Not Yet
                                                    {% else %}
                                                        {% if suggestion_cases[case]["consideration"]["considered"] %}
                                                            Yes
                                                        {% else %}
                                                            No
                                                        {% endif %}
                                                    {% endif %}
                                                </td>
                                                <td id="suggestion{{ case }}ReasonText">
                                                    {% if not suggestion_cases[case]["consideration"] %}
                                                        None Yet
                                                    {% else %}
                                                        {% if suggestion_cases[case]["consideration"]["considered"] %}
                                                            N/A
                                                        {% else %}
                                                            {{ suggestion_cases[case]["consideration"]["reason"] }}
                                                        {% endif %}
                                                    {% endif %}
                                                </td>
                                            </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        {% endif %}
                        </div>
        """
    )