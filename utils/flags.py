"""
Flag URL helper using flagcdn.com
Returns a flag image URL for any WC26 team name.
Usage: get_flag_url("France") → "https://flagcdn.com/w40/fr.png"
"""

TEAM_TO_ISO = {
    # Hosts
    "United States":          "us",
    "Canada":                 "ca",
    "Mexico":                 "mx",
    # UEFA
    "England":                "gb-eng",
    "France":                 "fr",
    "Germany":                "de",
    "Spain":                  "es",
    "Portugal":               "pt",
    "Netherlands":            "nl",
    "Belgium":                "be",
    "Switzerland":            "ch",
    "Croatia":                "hr",
    "Norway":                 "no",
    "Scotland":               "gb-sct",
    "Austria":                "at",
    "Bosnia and Herzegovina": "ba",
    "Sweden":                 "se",
    "Turkiye":                "tr",
    "Czechia":                "cz",
    # CONMEBOL
    "Argentina":              "ar",
    "Brazil":                 "br",
    "Colombia":               "co",
    "Ecuador":                "ec",
    "Paraguay":               "py",
    "Uruguay":                "uy",
    # AFC
    "Japan":                  "jp",
    "South Korea":            "kr",
    "Australia":              "au",
    "Iran":                   "ir",
    "Saudi Arabia":           "sa",
    "Qatar":                  "qa",
    "Jordan":                 "jo",
    "Uzbekistan":             "uz",
    # CAF
    "Morocco":                "ma",
    "Senegal":                "sn",
    "Ghana":                  "gh",
    "Tunisia":                "tn",
    "Algeria":                "dz",
    "Egypt":                  "eg",
    "Ivory Coast":            "ci",
    "South Africa":           "za",
    "Cape Verde":             "cv",
    "DR Congo":               "cd",
    # CONCACAF non-hosts
    "Panama":                 "pa",
    "Curacao":                "cw",
    "Haiti":                  "ht",
    # OFC
    "New Zealand":            "nz",
    # Interconf
    "Iraq":                   "iq",
    # WC22 teams not in WC26
    "Wales":                  "gb-wls",
    "Poland":                 "pl",
    "Denmark":                "dk",
    "Cameroon":               "cm",
    "Serbia":                 "rs",
    "Belgium":                "be",
}

def get_flag_url(team_name: str, size: int = 40) -> str:
    """
    Returns flagcdn.com URL for a team name.
    size: width in pixels (20, 40, 80, 160, 320, 640, 1280)
    """
    iso = TEAM_TO_ISO.get(team_name, "").lower()
    if not iso:
        return ""
    return f"https://flagcdn.com/w{size}/{iso}.png"


def flag_img_html(team_name: str, size: int = 24) -> str:
    """Returns an HTML img tag for inline use in st.markdown."""
    url = get_flag_url(team_name, size=40)
    if not url:
        return ""
    return f'<img src="{url}" width="{size}" style="vertical-align:middle; border-radius:2px; margin-right:6px;">'


def team_with_flag(team_name: str, size: int = 20) -> str:
    """Returns flag + team name as markdown-safe HTML string."""
    flag = flag_img_html(team_name, size=size)
    return f"{flag}{team_name}"
