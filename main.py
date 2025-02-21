from fasthtml.common import *
from datetime import datetime, date
import pytz

app, rt = fast_app()

# Configuration
MIN_ITEMS = 1


def calculate_rotation(num_items: int, tz: str, start_date: date = date(1970, 1, 1), start_item: int = 1) -> int:
    """Calculate which item to use based on number of items and current date."""
    if not (1 <= start_item <= num_items):
        raise ValueError(f"Start item must be between 1 and {num_items}")

    timezone = pytz.timezone(tz)
    now = datetime.now(timezone).date()
    days_since_start = (now - start_date).days
    
    # Calculate the item number, taking into account the start_item
    return ((days_since_start + (start_item - 1)) % num_items) + 1


@rt("/{num_items:int}/{start_date}/{start_item:int}")
@rt("/{num_items:int}/{start_date}")
@rt("/{num_items:int}")
def get(num_items: int, request, start_date: str = None, start_item: int = 1):
    """Handle rotation calculation with optional start date and item."""
    tz = request.query_params.get("tz")
    if not tz:
        # If no timezone specified, return a page that auto-detects and redirects
        base_url = f"/{num_items}"
        if start_date:
            base_url += f"/{start_date}"
            if start_item != 1:
                base_url += f"/{start_item}"
        return Titled(
            "Redirecting...",
            Script(f"""
                const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
                window.location.href = "{base_url}?tz=" + encodeURIComponent(tz);
                """),
        )

    try:
        # Parse start date if provided, otherwise use default
        parsed_start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").date()
            if start_date
            else date(1970, 1, 1)
        )
        
        item_number = calculate_rotation(num_items, tz, parsed_start_date, start_item)
        
        timezone = pytz.timezone(tz)
        now = datetime.now(timezone)
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
            P("Change settings:"),
            rotation_form(num_items, parsed_start_date, start_item),
            Script(timezone_script),
        )
    except (ValueError, TypeError):
        return Titled(
            "Error",
            H1("Invalid Input"),
            P("Please enter valid start date and item number"),
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
        start_date = request.query_params.get("start_date", "").strip()
        start_item = request.query_params.get("start_item", "").strip()
        tz = request.query_params.get("tz", "")

        # Build the base URL with required parameters
        url = f"/{items}"
        
        # Add optional parameters to path
        if start_date:
            url += f"/{start_date}"
            if start_item and start_item != "1":
                url += f"/{start_item}"
        
        # Add timezone as query parameter if present
        if tz:
            url += f"?tz={tz}"
        
        return Redirect(url)
    except (ValueError, TypeError):
        return Titled(
            "Error",
            H1("Invalid Input"),
            P(f"Please enter a number of at least {MIN_ITEMS}"),
            rotation_form(),
            Script(timezone_script),
        )


def rotation_form(current_items=None, start_date=None, start_item=None):
    # Use Jan 1, 1970 as default if no start_date provided
    display_date = start_date if start_date else date(1970, 1, 1)
    
    return Form(
        Div(
            Label("Number of items:", For="items"),
            Input(
                type="number",
                name="items",
                id="items",
                min=str(MIN_ITEMS),
                value=str(current_items) if current_items else "",
                placeholder=f"Minimum {MIN_ITEMS}",
                required=True,
            ),
            class_="form-group",
        ),
        Div(
            Label("Start date:", For="start_date"),
            Input(
                type="date",
                name="start_date",
                id="start_date",
                value=display_date.strftime("%Y-%m-%d"),
                placeholder="Default: Jan 1, 1970",
            ),
            class_="form-group",
        ),
        Div(
            Label("Start with item:", For="start_item"),
            Input(
                type="number",
                name="start_item",
                id="start_item",
                min="1",
                value=str(start_item) if start_item else "",
                placeholder="Default: 1",
            ),
            class_="form-group",
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
        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            min-width: 200px;
        }
        
        .rotation-form {
            flex-direction: column;
            align-items: flex-start;
        }
        
        label {
            color: #4b5563;
            font-weight: 500;
        }
        
        input {
            padding: 0.5rem;
            border: 1px solid #d1d5db;
            border-radius: 0.25rem;
            width: 100%;
        }
        
        button {
            margin-top: 1rem;
            padding: 0.5rem 1rem;
            background-color: #2563eb;
            color: white;
            border: none;
            border-radius: 0.25rem;
            cursor: pointer;
        }
        
        button:hover {
            background-color: #1d4ed8;
        }
    """)


serve()
