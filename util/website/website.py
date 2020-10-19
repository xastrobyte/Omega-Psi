class Website:

    def __init__(self, *, pages = [], footer = None):

        self._pages = pages
        self._footer = footer

    def get_pages(self):
        return self._pages
    
    def get_footer(self):
        return self._footer
    
    def generate_html(self):

        head = (
"""
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="/static/styles.css" rel="stylesheet" type="text/css">

    {}

    <link rel="shortcut icon" href="{{ url_for('static', filename='/favicon.ico') }}">
    <link rel="apple-touch-icon" sizes="180x180" href="{{ url_for('static', filename='/apple-touch-icon.png') }}">
    <link rel="icon" type="image/png" sizes="32x32" href="{{ url_for('static', filename='/favicon-32x32.png') }}">
    <link rel="icon" type="image/png" sizes="16x16" href="{{ url_for('static', filename='/favicon-16x16.png') }}">
    <link rel="manifest" href="{{ url_for('static', filename='/site.webmanifest') }}">
    <link rel="mask-icon" href="{{ url_for('static', filename='/safari-pinned-tab.svg') }}" color="#202020">
    <meta name="msapplication-TileColor" content="#202020">
    <meta name="msapplication-TileImage" content="{{ url_for('static', filename='/mstile-144x144.png') }}">
    <meta name="theme-color" content="#202020">
    <meta name="msapplication-config" content="{{ url_for('static', filename='/browserconfig.xml') }}">
    
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/sweetalert2@9"></script>
    <script src="/static/js/bugs.js"></script>
    <script src="/static/js/suggestions.js"></script>
    <script src="/static/js/settings.js"></script>
    <script src="/static/js/pendingUpdate.js"></script>
    <script src="/static/js/tasks.js"></script>

</head>
"""
        )

        meta = (
    """
    <meta property="theme-color" content="#EC7600" />
    <meta property="og:title" content="website.{}();" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="https://omegapsi.fellowhashbrown.com/{}" />
    <meta property="og:image" content="{}" />

    <meta property="og:description" content="{}" />
    <meta property="og:site_name" content="{}" />
    <title>{}</title>
    """
        )

        html = (
"""
<html>

    {}

    <body>
        <div class="page-body">

            <!-- Navigation Bar -->
            <nav class="nav-bar">
                <img src="https://i.imgur.com/Hy5Gyut.png" class="social-image" style="width: 50px; height: 50px;">
                <div id="nav-toggle">
                    <input type="checkbox">
                    <span></span>
                    <span></span>
                    <span></span>
                    
                    <ul class="nav-links">
                        {}
                    </ul>
                </div>
            </nav>

            <!-- Content -->
            <div class="content">
                {}
            </div>
        </div>
    </body>
    <footer class="footer">
        {}
    </footer>
</html>
"""
        )

        navigation_bar = {}

        for page in self.get_pages():
            navigation_bar[page.get_title()] = ""

            for nav_page in self.get_pages():

                if not nav_page.ignore():

                    navigation_link = (
                """
                <li class=\"nav-item\">
                    <a class="nav-link{}\" href=\"{}\">{}</a>
                </li>\n
                """
                    )

                    navigation_bar[page.get_title()] += navigation_link.format(
                        " active" if (page == nav_page) else "",
                        "/" if nav_page.is_homepage() else (
                            nav_page.get_target() if nav_page.get_target() != None else ("/" + nav_page.get_title())
                        ),
                        nav_page.get_title()
                    )

        for page in self.get_pages():
            htmlCopy = html.format(
                head.replace(
                    "{}",
                    meta.format(
                        page.get_title().lower(),
                        page.get_title() if page.is_homepage() else "",
                        "https://i.imgur.com/Hy5Gyut.png" if page.get_custom_icon() == None else page.get_custom_icon(),
                        page.get_custom_description(),
                        "Omega Psi" if page.get_custom_title() == None else page.get_custom_title(),
                        "Omega Psi" if page.get_custom_title() == None else page.get_custom_title()
                    )
                ),
                navigation_bar[page.get_title()],
                page.generate_html(),
                self.get_footer().generate_html()
            )

            f = open("templates/{}.html".format(
                page.get_title()
            ), "w")
            f.write(htmlCopy)
            f.close()

class Link:
    def __init__(self, *, url = None, text = None):
        self._url = url
        self._text = text
    
    def get_text(self):
        return self._text
    
    def get_url(self):
        return self._url
    
    def generate_html(self):
        return "<a href=\"{}\" class=\"link\" style=\"font-family: cutive mono, monospace;\">{}</a>".format(
            self.get_url(), self.get_text()
        )

class Footer:
    def __init__(self, *, copyright_name = None, copyright_year = None, links = []):
        self._copyright_name = copyright_name
        self._copyright_year = copyright_year
        self._links = links
    
    def get_copyright_name(self):
        return self._copyright_name
    
    def get_copyright_year(self):
        return self._copyright_year
    
    def get_links(self):
        return self._links
    
    def generate_html(self):
        html = "<p style=\"text-align: center;\">{2}<small style=\"background: #202020;\"><code>Copyright &copy; {0}<script>new Date().getFullYear()>{0}&&document.write(\"-\"+new Date().getFullYear());</script>, {1}</code></small></p>\n".format(
            self.get_copyright_year(),
            self.get_copyright_name(),
            " | ".join([
                "{}".format(link.generate_html()) for link in self.get_links()
            ])
        )
        
        return html