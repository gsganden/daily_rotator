from fasthtml.common import *
from datetime import datetime
import pytz

app, rt = fast_app()

# Configuration
MIN_ITEMS = 1


def calculate_rotation(num_items: int, tz: str) -> int:
    """Calculate which item to use based on number of items and current date."""
    if num_items < MIN_ITEMS:
        raise ValueError(f"Number of items must be at least {MIN_ITEMS}")

    timezone = pytz.timezone(tz)
    now = datetime.now(timezone)
    then = datetime(1970, 1, 1, tzinfo=timezone)
    return (now - then).days % num_items + 1


@rt("/{num_items:int}")
def get(num_items: int, request):
    tz = request.query_params.get("tz")
    if not tz:
        # If no timezone specified, return a page that auto-detects and redirects
        return Titled(
            "Redirecting...",
            Script(f"""
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                window.location.href = "/{num_items}?tz=" + encodeURIComponent(tz);
                """),
        )

    timezone = pytz.timezone(tz)
    now = datetime.now(timezone)
    item_number = calculate_rotation(num_items, tz)
    date_str = now.strftime("%A, %B %d, %Y")

    return Titled(
        "Daily Rotation",
        P("A simple tool that helps you rotate through numbered items daily."),
        P(
            f"Use item ",
            Strong(item_number),
            f" today! ({date_str} in {tz})",
            class_="result",
        ),
        P("Change number of items:"),
        rotation_form(),
        Script(timezone_script),
    )


@rt("/")
def home():
    return Titled(
        "Daily Rotation",
        P("A simple tool that helps you rotate through numbered items daily. You can use it to cycle through saxophone reeds, daily workouts, study subjects, or anything else that needs regular rotation."),
        P("Enter the number of items you want to rotate through:"),
        rotation_form(),
        Script(timezone_script),
    )


@rt("/select")
def select(request):
    try:
        items = int(request.query_params.get("items", "1"))
        tz = request.query_params.get("tz")
        if not tz:
            # If no timezone specified, return a page that auto-detects and redirects
            return Titled(
                "Redirecting...",
                Script(f"""
                    const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                    window.location.href = "/{items}?tz=" + encodeURIComponent(tz);
                    """),
            )
        # Validate input before redirecting
        calculate_rotation(items, tz)
        return Redirect(f"/{items}?tz={tz}")
    except (ValueError, TypeError):
        return Titled(
            "Error",
            H1("Invalid Input"),
            P(f"Please enter a number of at least {MIN_ITEMS}"),
            rotation_form(),
            Script(timezone_script),
        )


def rotation_form():
    return Form(
        Input(
            type="number",
            name="items",
            min=str(MIN_ITEMS),
            placeholder=f"Number of items (minimum {MIN_ITEMS})",
            required=True,
        ),
        Input(type="hidden", name="tz", id="timezone-input"),
        Button("Get Today's Item", type="submit"),
        method="GET",
        action="/select",
        class_="rotation-form",
    )


timezone_script = """
    function setTimezone() {
        // Check if timezone is in URL
        const urlParams = new URLSearchParams(window.location.search);
        const urlTz = urlParams.get('tz');
        
        if (urlTz) {
            // Use timezone from URL
            document.getElementById('timezone-input').value = urlTz;
        } else {
            // Auto-detect timezone if not in URL
            try {
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                document.getElementById('timezone-input').value = tz;
            } catch (e) {
                console.error('Could not detect timezone:', e);
            }
        }
    }
    setTimezone();
"""


@rt("/styles.css")
def styles():
    return CSS("""
        body {
            max-width: 800px;
            margin: 2rem auto;
            padding: 1rem;
            font-family: system-ui, -apple-system, sans-serif;
            line-height: 1.5;
        }
        p {
            color: #4b5563;
        }
        .result {
            color: #4b5563;
            font-size: 2rem;
            margin: 2rem 0;
        }
        .result strong {
            color: #2563eb;
            font-size: 2.5rem;
            padding: 0 0.2em;
        }
        .rotation-form {
            margin: 2rem 0;
            display: flex;
            gap: 1rem;
            align-items: center;
        }
        .error {
            color: #dc2626;
        }
    """)


serve()
