from cogs.predicates import is_developer_predicate, is_nsfw_and_guild_predicate, is_nsfw_or_private_predicate, guild_manager_predicate, guild_only_predicate

keys = {
    "red command": {
        "color": "#FF0080",
        "description": "This command can only be run in NSFW channels or Private DMs."
    },
    "orange command": {
        "color": "#EC7600",
        "description": "This command can only be run in servers."
    },
    "yellow command": {
        "color": "#CDCD00",
        "description": "This command can only be run in NSFW channels in servers."
    },
    "blue command": {
        "color": "#678CB1",
        "description": "This command can only be run by bot developers."
    },
    "green command": {
        "color": "#80ff80",
        "description": "This command can only be run by people who have manage server permissions in a server."
    }
}

class Page:

    def __init__(self, *, title = None, description = None, homepage = False, target = None, ignore = False, sections = [], custom_html = None, custom_title = None, custom_description = None, custom_icon = None):

        self._sections = sections

        self._custom_title = custom_title if custom_title != None else title
        self._custom_description = custom_description if custom_description != None else description
        self._custom_icon = custom_icon
        self._custom_html = custom_html

        self._title = title
        self._description = description
        self._homepage = homepage

        self._target = target

        self._ignore = ignore
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description
    
    def is_homepage(self):
        return self._homepage
    
    def get_target(self):
        return self._target
    
    def get_sections(self):
        return self._sections

    def get_custom_title(self):
        return self._custom_title
    
    def get_custom_description(self):
        return self._custom_description
    
    def get_custom_icon(self):
        return self._custom_icon
    
    def get_custom_html(self):
        return self._custom_html
    
    def ignore(self):
        return self._ignore
    
    def generate_html(self):

        html = (
                """
                <h1 class="page-title">
                    <code class="field">website</code><code>.</code><code class="field">{}</code><code>();</code>
                </h1>

                <div class="page-title-block" style="max-width: 75%;">
                    <p style="text-align: center;">
                        {}
                    </p>
                </div>

                {}

                <br>
                <br>
                """
        )

        # Generate section html if there is not a custom html
        sections = ""
        if self.get_custom_html() == None:
            for section in self.get_sections():
                sections += section.generate_html() + "\n"
        
        return html.format(
            self.get_title(),
            self.get_description(),
            sections if self.get_custom_html() == None else self.get_custom_html()
        )

class KeySection:

    def __init__(self, *, keys = keys):

        self._keys = keys
    
    def generate_html(self):
        
        html = (
                """
                <h2 class="page-section">
                    <a name="key"></a>
                    <code class="field">page</code><code>.</code><code class="field">key</code><code>();</code>
                </h2>
                <div class="page-section-block" style="text-align: center;">
                    {}
                </div>
                """
        )

        # Create key html
        keys_html = (
            """
            <table class=\"command-table\" style=\"width: 100%;\">
                {}
            </table>
            """
        )
        keys = ""
        for key in self._keys:

            key_html = (
                """
                <tr class=\"command-tr\" style="width: 100%;">
                    <td style=\"width: 25%;\"><code style=\"color: {};\">{}</code></td>
                    <td style=\"width: 100%; text-align: center;\">{}</td>
                </tr>\n
                """
            ).format(
                self._keys[key]["color"],
                key,
                self._keys[key]["description"]
            )

            keys += key_html + "\n"
        
        return html.format(
            keys_html.format(
                keys
            )
        )

class Section:

    def __init__(self, *, title = None, description = None, commands = []):
        self._title = title
        self._commands = commands

        self._description = description
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description
    
    def get_commands(self):
        return self._commands
    
    def generate_html(self):
        html = (
                """
                <h2 class="page-section">
                    <a name="{}"></a>
                    <code class="field">page</code><code>.</code><code class="field">{}</code><code>();</code>
                </h2>
                <div class="page-section-block" style="text-align: center;">
                    <p style="text-align: center;">
                        {}
                    </p>
                    {}
                </div>
                """
        )

        # Generate command html
        command_html = (
            """
            <ul style=\"text-align: left; list-style-type: none; width: 100%;\">
                {}
            </ul>
            """
        )
        commands = ""
        for cmd in self.get_commands():
            commands += Section.get_subcommand_html(cmd) + "\n"

        return html.format(
            self.get_title(),
            self.get_title(),
            self.get_description(),
            command_html.format(commands)
        )
    
    @staticmethod
    def get_subcommand_html(command):

        # Check for specific checks
        special = True
        if is_developer_predicate in command.checks:
            color = keys["blue command"]["color"]
            tooltip = keys["blue command"]["description"]
        elif is_nsfw_or_private_predicate in command.checks:
            color = keys["red command"]["color"]
            tooltip = keys["red command"]["description"]
        elif guild_manager_predicate in command.checks:
            color = keys["green command"]["color"]
            tooltip = keys["green command"]["description"]
        elif guild_only_predicate in command.checks:
            color = keys["orange command"]["color"]
            tooltip = keys["orange command"]["description"]
        elif is_nsfw_and_guild_predicate in command.checks:
            color = keys["yellow command"]["color"]
            tooltip = keys["yellow command"]["description"]
        
        # No specific checks
        else:
            special = False

        # Check if the command has any subcommands
        try:
            subcommands = command.commands

            # Create an unnumbered list for the command and a list of list items for its subcommands
            command_ul = (
                """
                <li width="100%">
                    <table width="100%">
                        <tr>
                            <td{} width="20%">{}</td>
                            <td>{}</td>
                        </tr>
                    </table>
                    <ul style="list-style-type: none;">
                        {}
                    </ul>
                </li>
                """
            )

            subcommand_lis = []
            for subcommand in subcommands:
                subcommand_lis.append(
                    Section.get_subcommand_html(subcommand)
                )

            return command_ul.format(
                " style=\"color: {};\"".format(
                    color
                ) if special else "",
                (
                    """
                    <div class=\"tooltip\">{}
                        <span class=\"tooltiptext\">{}</span>
                    </div>
                    """
                ).format(command.name, tooltip) if special else command.name,
                command.description,
                "\n".join(subcommand_lis)
            )
        
        # The command has no subcommands
        except:
            return (
                """
                <li width="100%">
                    <table width="100%">
                        <tr>
                            <td{} width="20%">{}</td>
                            <td>{}</td>
                        </tr>
                    </table>
                </li>
                """
            ).format(
                " style=\"color: {};\"".format(
                    color
                ) if special else "",
                (
                    """
                    <div class=\"tooltip\">{}
                        <span class=\"tooltiptext\">{}</span>
                    </div>
                    """
                ).format(command.name, tooltip) if special else command.name,
                command.description
            )

class HomeSection:

    def __init__(self, *, title = None, description = None, forms = [], custom_html = None):

        self._title = title
        self._description = description

        self._forms = forms
        self._custom_html = custom_html
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description
    
    def get_forms(self):
        return self._forms
    
    def generate_html(self):

        if not self._custom_html:
        
            # Setup html
            html = (
                    """
                    <h2 class="page-section">
                        <a name="{}"></a>
                        <code class="field">page</code><code>.</code><code class="field">{}</code><code>();</code>
                    </h2>
                    <div class="page-section-block" style="text-align: center;">
                        <p style="text-align: left;">
                            {}
                        </p>
                        {}
                    </div>
                    """
            )

            forms = ""

            for form in self.get_forms():
                forms += form.generate_html()

            return html.format(
                self.get_title(),
                self.get_title(),
                self.get_description(),
                forms
            )

        else:
            return self._custom_html

class Form:

    def __init__(self, *, form_user_id = None, form_id = None, form_command = None, form_description = None, button_text = None, target = None):
        
        self._form_id = form_id
        self._form_command = form_command
        self._form_description = form_description
        self._form_user_id = form_user_id
        self._button_text = button_text

        self._target = target
    
    def get_form_id(self):
        return self._form_id
    
    def get_form_command(self):
        return self._form_command
    
    def get_form_description(self):
        return self._form_description
    
    def get_form_user_id(self):
        return self._form_user_id
    
    def get_button_text(self):
        return self._button_text
    
    def get_target(self):
        return self._target
    
    def generate_html(self):

        return (
            """
            <form id="{0}">
                <input type="hidden" id="{0}UserId" name="userId" value="{1}"> <br>
                <input type="button" class="page-form-button" value="{2}" onclick="{3}">
            </form>
            """
        ).format(
            self.get_form_id(),
            self.get_form_user_id(),
            self.get_button_text(),
            self.get_target()
        )