from category.predicates import is_nsfw_or_private, guild_only, is_nsfw_and_guild, is_developer, can_manage_guild

keys = {
    "red command": {
        "color": "#FF0080",
        "description": "Any of these commands can only be run in NSFW channels or Private DMs."
    },
    "orange command": {
        "color": "#EC7600",
        "description": "These commands can only be run in servers."
    },
    "yellow command": {
        "color": "#CDCD00",
        "description": "These commands can only be run in NSFW channels in servers."
    },
    "blue command": {
        "color": "#678CB1",
        "description": "These commands can only be run by bot developers."
    },
    "green command": {
        "color": "#80ff80",
        "description": "These commands can only be run by people who have manage server permissions in a server."
    },
    "white command": {
        "color": "#EEEEEE",
        "description": "These are just regular commands and can be run anywhere!"
    }
}

class Page:

    def __init__(self, *, title = None, description = None, homepage = False, target = None, ignore = False, sections = [], custom_html = None, custom_title = None, custom_description = None, custom_icon = None):

        self._sections = sections

        self._custom_title = custom_title
        self._custom_description = custom_description
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
            <table class=\"command-table\" style=\"width: 100%;\">
                {}
            </table>
            """
        )
        commands = ""
        for cmd in self.get_commands():

            # Check for specific checks
            special = True
            if is_developer in cmd.checks:
                color = keys["blue command"]["color"]
            elif is_nsfw_or_private in cmd.checks:
                color = keys["red command"]["color"]
            elif can_manage_guild in cmd.checks:
                color = keys["green command"]["color"]
            elif guild_only in cmd.checks:
                color = keys["orange command"]["color"]
            elif is_nsfw_and_guild in cmd.checks:
                color = keys["yellow command"]["color"]
            
            # No specific checks
            else:
                special = False

            # Create table row for command
            command = (
                """
                <tr class=\"command-tr\" style="width: 100%;">
                    <td style=\"width: 25%;\"><code{}>{}</code></td>
                    <td style=\"width: 100%; text-align: center;\">{}</td>
                </tr>\n
                <tr>
                </tr>
                """
            ).format(
                " style=\"color: {};\"".format(
                    color
                ) if special else "",
                cmd.name,
                cmd.description
            )

            commands += command + "\n"

        return html.format(
            self.get_title(),
            self.get_title(),
            self.get_description(),
            command_html.format(commands)
        )

class HomeSection:

    def __init__(self, *, title = None, description = None, forms = []):

        self._title = title
        self._description = description

        self._forms = forms
    
    def get_title(self):
        return self._title
    
    def get_description(self):
        return self._description
    
    def get_forms(self):
        return self._forms
    
    def generate_html(self):
        
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

class UserInfoForm:

    def __init__(self, *, form_user_name = None, form_user_discriminator = None, button_text = None, target = None):
        
        self._form_user_name = form_user_name
        self._form_user_discriminator = form_user_discriminator
        self._button_text = button_text

        self._target = target
    
    def get_form_user_name(self):
        return self._form_user_name
    
    def get_form_user_discriminator(self):
        return self._form_user_discriminator
    
    def get_button_text(self):
        return self._button_text
    
    def get_target(self):
        return self._target
    
    def generate_html(self):

        return (
            """
            <form action="{}" method="POST">
                <input type="text" class="page-form-input" name="{}" placeholder="enter username here">
                <input type="text" class="page-form-input" name="{}" placeholder="enter discriminator here">
                <input type="submit" class="page-form-button" value="{}">
            </form>
            """
        ).format(
            self.get_target(),
            self.get_form_user_name(),
            self.get_form_user_discriminator(),
            self.get_button_text(),
        )