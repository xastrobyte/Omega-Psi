class Website:

    def __init__(self, *, pages = []):

        self._pages = pages

    def get_pages(self):
        return self._pages
    
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
    <footer>
        <small><code>Copyright &copy; 2018<script>new Date().getFullYear()>2018&&document.write("-"+new Date().getFullYear());</script>, Jonah Pierce</code></small>
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
                page.generate_html()
            )

            f = open("templates/{}.html".format(
                page.get_title()
            ), "w")
            f.write(htmlCopy)
            f.close()