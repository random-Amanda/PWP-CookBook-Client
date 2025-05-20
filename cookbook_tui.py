"""
Cookbook TUI Client

This module provides a text-based user interface (TUI) for interacting with a RESTful API

Requirements:
- `curses` (Unix only; Windows may require `windows-curses`)
- `requests` for HTTP communication
"""

import curses
import json
import requests

API_BASE = "http://localhost:5000/"
HEADERS = {
    "Accept": "application/vnd.mason+json",
    "Content-Type": "application/json",
    "API-KEY": "1zwrquvMcegY35tELcea2sX35ENnGVxep9rnZ9WyPAs",
}


def fetch_data(url):
    """
    Fetches JSON data from the specified URL using a GET request.
    Args:
        url (str): The API endpoint to request.
    Returns:
        dict: Parsed JSON response if successful, or a dict with an 'error' key on failure.
    """
    try:
        res = requests.get(url, headers=HEADERS)
        return res.json() if res.ok else {"error": res.text}
    except Exception as e:
        return {"error": str(e)}


def post_data(url, payload):
    """
    Sends a POST request with a JSON payload to the specified URL.
    Args:
        url (str): The API endpoint to post to.
        payload (dict): The data to send in the request body.
    Returns:
        Response | None: The response object if successful, or None on failure.
    """
    try:
        res = requests.post(url, headers=HEADERS, json=payload)
        return res
    except Exception as e:
        return None


def render_menu(stdscr, title, options, cursor_idx):
    """
    Renders a navigable menu in a curses window.
    Args:
        stdscr (curses.window): The curses window where the menu is displayed.
        title (str): The title to display at the top of the menu.
        options (List[str]): A list of menu option strings.
        cursor_idx (int): The index of the currently selected option.
    """
    stdscr.clear()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    h, w = stdscr.getmaxyx()
    stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
    stdscr.addstr(1, 2, title[: w - 4])
    stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

    for idx, item in enumerate(options):
        y = 3 + idx
        if idx == cursor_idx:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, 4, item[: w - 8])
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.attron(curses.color_pair(3))
            stdscr.addstr(y, 4, item[: w - 8])
            stdscr.attroff(curses.color_pair(3))

    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(h - 2, 2, "↑/↓ to navigate | Enter to select | q to quit")
    stdscr.attroff(curses.color_pair(3))
    stdscr.refresh()


def get_user_input(stdscr, prompt, default="", width=50):
    """
    Prompts the user for input using a centered input box in the curses window.
    Args:
        stdscr (curses.window): The curses standard screen window.
        prompt (str): The prompt text to display.
        default (str): Default value to return if the user provides no input.
        width (int): Width of the input box.
    Returns:
        str: The user's input or the default value if no input was entered.
    """
    curses.echo()
    curses.curs_set(1)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Get terminal size
    max_y, max_x = stdscr.getmaxyx()
    win_height = 5
    win_width = min(width, max_x - 4)
    start_y = (max_y - win_height) // 2
    start_x = (max_x - win_width) // 2

    # Create input window
    win = curses.newwin(win_height, win_width, start_y, start_x)
    win.bkgd(" ", curses.color_pair(2))
    win.attron(curses.color_pair(1))
    win.box()
    win.attroff(curses.color_pair(1))

    prompt_full = f"{prompt} [{default}]" if default else prompt
    win.attron(curses.color_pair(2) | curses.A_BOLD)
    win.addstr(1, 2, prompt_full[: win_width - 4])
    win.attroff(curses.A_BOLD)

    win.addstr(2, 2, "> ")
    win.refresh()

    input_str = win.getstr(2, 4, win_width - 6).decode().strip()
    curses.noecho()
    curses.curs_set(0)

    # Clear the window and refresh the main screen
    win.clear()
    win.refresh()
    stdscr.touchwin()
    stdscr.refresh()

    return input_str or default


def tui_main(stdscr):
    """
    Main loop of the TUI application. Displays the main menu and routes to
    appropriate handlers based on user selection.
    Args:
        stdscr (curses.window): The main curses window.
    """
    curses.curs_set(0)
    cursor = 0
    options = ["Recipes", "Ingredients", "Users", "Exit"]

    while True:
        render_menu(stdscr, "Cookbook TUI", options, cursor)
        key = stdscr.getch()

        if key == curses.KEY_UP:
            cursor = (cursor - 1) % len(options)
        elif key == curses.KEY_DOWN:
            cursor = (cursor + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[cursor] == "Exit":
                break
            if options[cursor] == "Recipes":
                handle_recipes(stdscr)
            elif options[cursor] == "Ingredients":
                handle_ingredients(stdscr)
            elif options[cursor] == "Users":
                handle_users(stdscr)


def handle_users(stdscr):
    """
    Displays a list of users and allows adding, viewing, and managing them.
    Args:
        stdscr (curses.window): The curses window used for rendering.
    """

    def reload_users():
        data = fetch_data(f"{API_BASE}/api/users/")
        return data.get("items", [])

    users = reload_users()
    data = fetch_data(f"{API_BASE}/api/users/")
    idx = 0
    if not users:
        stdscr.addstr(0, 0, "No users found.")
        stdscr.getch()
        return

    while True:
        options = [f"{u['user_id']}. {u['username']} ({u['email']})" for u in users]
        options += ["", "Add New User", "Back"]
        render_menu(stdscr, "User Management", options, idx)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            if options[idx] == "Add New User":
                add_user(stdscr, data["@controls"]["cookbook:add-user"]["href"])
                users = reload_users()
                idx = 0
            else:
                user = users[idx]
                show_user_details(stdscr, user["@controls"]["self"]["href"])
                users = reload_users()
                idx = 0


def handle_recipes(stdscr):
    """
    Displays a list of recipes and allows adding, viewing, and editing them.
    Args:
        stdscr (curses.window): The curses window used for rendering.
    """

    def reload_recipes():
        data = fetch_data(f"{API_BASE}/api/recipes/")
        return data.get("items", [])

    recipes = reload_recipes()
    data = fetch_data(f"{API_BASE}/api/recipes/")
    idx = 0
    if not recipes:
        stdscr.addstr(0, 0, "No recipes found.")
        stdscr.getch()
        return

    while True:
        options = [f" {r['recipe_id']}. {r['title']} " for r in recipes]
        options += ["", "Add New Recipe", "Back"]
        render_menu(stdscr, "Recipe Management", options, idx)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            if options[idx] == "Add New Recipe":
                add_recipe(stdscr, data["@controls"]["cookbook:add-recipe"]["href"])
                recipes = reload_recipes()
                idx = 0
            else:
                recipe = recipes[idx]
                show_recipe_details(stdscr, recipe["@controls"]["self"]["href"])
                recipes = reload_recipes()
                idx = 0


def handle_ingredients(stdscr):
    """
    Displays a list of ingredients and allows adding, viewing, and managing them.
    Args:
        stdscr (curses.window): The curses window used for rendering.
    """

    def reload_ingredients():
        data = fetch_data(f"{API_BASE}/api/ingredients/")
        return data.get("items", [])

    ingredients = reload_ingredients()
    data = fetch_data(f"{API_BASE}/api/ingredients/")
    idx = 0
    if not ingredients:
        stdscr.addstr(0, 0, "No ingredients found.")
        stdscr.getch()
        return

    while True:
        options = [f"{i['ingredient_id']}. {i['name']}" for i in ingredients]
        options += ["", "Add New Ingredient", "Back"]
        render_menu(stdscr, "Ingredient Management", options, idx)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            elif options[idx] == "Add New Ingredient":
                add_ingredient(
                    stdscr, data["@controls"]["cookbook:add-ingredient"]["href"]
                )
                ingredients = reload_ingredients()
                idx = 0
            else:
                ingredient = ingredients[idx]
                show_ingredient_details(stdscr, ingredient["@controls"]["self"]["href"])
                ingredients = reload_ingredients()
                idx = 0


def add_ingredient(stdscr, href):
    """
    Collects user input and submits a new ingredient to the API.
    Args:
        stdscr (curses.window): The curses window.
        href (str): The API endpoint to post the ingredient to.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, "Add New Ingredient", curses.A_BOLD)
    name = get_user_input(stdscr, "Name:")
    description = get_user_input(stdscr, "Description:")

    if not name or not description:
        stdscr.addstr(0, 0, "All fields are required. Press any key to exit.")
        stdscr.getch()
        return

    payload = {"name": name, "description": description}

    response = post_data(f"{API_BASE}{href}", payload)
    stdscr.addstr(
        0,
        0,
        "Ingredient created successfully. Press any key to exit"
        if response.status_code == 201
        else "Failed to create ingredient.  Press any key to exit",
    )
    stdscr.getch()


def add_user(stdscr, href):
    """
    Collects user input and submits a new user to the API.
    Args:
        stdscr (curses.window): The curses window.
        href (str): The API endpoint to post the user to.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, "Add New User", curses.A_BOLD)
    username = get_user_input(stdscr, "Username:")
    email = get_user_input(stdscr, "Email:")
    password = get_user_input(stdscr, "Password:")
    if not username or not email or not password:
        stdscr.addstr(0, 0, "All fields are required. Press any key to exit.")
        stdscr.getch()
        return

    payload = {"username": username, "email": email, "password": password}

    response = post_data(f"{API_BASE}{href}", payload)
    stdscr.addstr(
        0,
        0,
        "User created successfully. Press any key to exit."
        if response.status_code == 201
        else "Failed to create user. Press any key to exit.",
    )
    stdscr.getch()


def show_user_details(stdscr, href):
    """
    Displays detailed information about a user and allows editing or deleting them.
    Args:
        stdscr (curses.window): The curses window.
        href (str): The API endpoint to fetch user details from.
    """
    data = fetch_data(f"{API_BASE}{href}")
    options = ["Edit User", "Delete User", "Back"]
    idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Username: {data.get('username')}", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Email: {data.get('email')}")
        stdscr.addstr(2, 0, f"Password: {data.get('password')}")

        for i, opt in enumerate(options):
            mode = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(4 + i, 0, opt, mode)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            elif options[idx] == "Edit User":
                stdscr.clear()
                stdscr.addstr(0, 0, "Editing User...", curses.A_BOLD)
                payload = {
                    "username": get_user_input(stdscr, "New username:")
                    or data["username"],
                    "email": get_user_input(stdscr, "New email:") or data["email"],
                    "password": get_user_input(stdscr, "New password:")
                    or data["password"],
                }
                put_url = data["@controls"]["cookbook:update-user"]["href"]
                requests.put(f"{API_BASE}{put_url}", headers=HEADERS, json=payload)
                stdscr.addstr(0, 0, "User updated. Press any key to exit.")
                stdscr.getch()
                return
            elif options[idx] == "Delete User":
                stdscr.clear()
                del_url = data["@controls"]["cookbook:delete-user"]["href"]
                requests.delete(f"{API_BASE}{del_url}", headers=HEADERS)
                stdscr.addstr(0, 0, "User deleted. Press any key to exit.")
                stdscr.getch()
                return


def show_recipe_details(stdscr, href):
    """
    Displays recipe details including ingredients and reviews, and allows editing.
    Args:
        stdscr (curses.window): The curses window.
        href (str): The API endpoint to fetch recipe details from.
    """
    data = fetch_data(f"{API_BASE}{href}")
    title = data.get("title", "No title")
    ingredients = data.get("recipeIngredients", [])
    reviews = data.get("reviews", [])

    options = [
        "Add Review",
        "Delete Review",
        "Add Ingredient",
        "Edit Recipe",
        "Edit Recipe Ingredients",
        "Back",
    ]
    idx = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Define box dimensions
        box_width = len(title) + 8
        box_y = 0
        box_x = max(0, (w - box_width) // 2)

        # Draw a box around the title
        stdscr.attron(curses.A_BOLD)
        stdscr.addstr(box_y, box_x, "+" + "-" * (box_width - 2) + "+")
        stdscr.addstr(box_y + 1, box_x, "|")
        stdscr.addstr(box_y + 1, box_x + box_width - 1, "|")

        # Center the title inside the box
        centered_title = f"  {title.upper()}  "
        title_x = box_x + (box_width - len(centered_title)) // 2
        stdscr.addstr(box_y + 1, title_x, centered_title)

        stdscr.addstr(box_y + 2, box_x, "+" + "-" * (box_width - 2) + "+")
        stdscr.attroff(curses.A_BOLD)

        # stdscr.clear()
        # stdscr.addstr(0, 0, f"Title: {title}", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Preparation: {data.get('preparation_time')}")
        stdscr.addstr(2, 0, f"Cooking: {data.get('cooking_time')}")
        stdscr.addstr(4, 0, "Ingredients:")
        for i, ing in enumerate(ingredients):
            stdscr.addstr(
                5 + i,
                2,
                f"- {ing.get('ingredient_id')} ({ing.get('qty')}{ing.get('metric')})",
            )

        offset = 6 + len(ingredients)
        stdscr.addstr(offset, 0, "Reviews:")
        for j, rev in enumerate(reviews):
            stdscr.addstr(
                offset + 1 + j,
                2,
                f"- Review ID: {rev.get('review_id')} : {rev.get('rating')} stars: {rev.get('feedback')}",
            )

        for k, opt in enumerate(options):
            mode = curses.A_REVERSE if k == idx else curses.A_NORMAL
            stdscr.addstr(offset + 3 + len(reviews) + k, 0, opt, mode)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            elif options[idx] == "Add Review":
                stdscr.clear()
                review_payload = {
                    "user_id": int(
                        get_user_input(stdscr, "Enter your user ID:") or data["user_id"]
                    ),
                    "rating": int(get_user_input(stdscr, "Enter rating (1-5):") or 1),
                    "feedback": get_user_input(stdscr, "Enter feedback:"),
                }
                href_post = data["@controls"]["cookbook:add-review"]["href"]
                post_data(f"{API_BASE}{href_post}", review_payload)
                stdscr.addstr(0, 0, "Review submitted. Press any key to exit.")
                stdscr.getch()
                return show_recipe_details(stdscr, href)
            elif options[idx] == "Add Ingredient":
                stdscr.clear()
                ing_payload = {
                    "ingredient_id": int(
                        get_user_input(stdscr, "Enter ingredient ID:") or 0
                    ),
                    "qty": float(get_user_input(stdscr, "Enter quantity:") or 0),
                    "metric": get_user_input(stdscr, "Enter unit (e.g., g, ml):"),
                }
                if (
                    ing_payload["ingredient_id"] == 0
                    or ing_payload["qty"] == 0
                    or not ing_payload["metric"]
                ):
                    stdscr.addstr(
                        0, 0, "All fields are required. Press any key to exit."
                    )
                    stdscr.getch()
                    return
                href_post = data["@controls"]["cookbook:add-ingredient"]["href"]
                if post_data(f"{API_BASE}{href_post}", ing_payload):
                    stdscr.addstr(0, 0, "Ingredient added. Press any key to exit.")
                else:
                    stdscr.addstr(
                        0, 0, "Failed to add ingredient. Press any key to exit."
                    )
                stdscr.getch()
                return show_recipe_details(stdscr, href)
            elif options[idx] == "Edit Recipe":
                edit_recipe(stdscr, data)
                return
            elif options[idx] == "Edit Recipe Ingredients":
                edit_recipeIngredients(stdscr, ingredients)
                return
            elif options[idx] == "Delete Review":
                show_review_details(stdscr, reviews)
                return


def edit_recipe(stdscr, data):
    """
    Allows the user to edit basic recipe metadata and submit changes to the API.
    Args:
        stdscr (curses.window): The curses window.
        data (dict): The existing recipe data to edit.
    """
    stdscr.clear()
    stdscr.addstr(0, 0, "Editing Recipe...", curses.A_BOLD)
    stdscr.refresh()

    payload = {
        "title": get_user_input(stdscr, f"New title ({data['title']}):")
        or data["title"],
        "description": get_user_input(stdscr, "New description:")
        or data.get("description", ""),
        "steps": get_user_input(stdscr, "New steps (JSON):") or data.get("steps", ""),
        "preparation_time": get_user_input(stdscr, "New preparation time:")
        or data.get("preparation_time", ""),
        "cooking_time": get_user_input(stdscr, "New cooking time:")
        or data.get("cooking_time", ""),
        "serving": int(
            get_user_input(stdscr, "New serving count:") or data.get("serving", 1)
        ),
        "user_id": int(
            get_user_input(stdscr, "User ID (keep same):") or data["user_id"]
        ),
    }

    put_url = data["@controls"]["cookbook:update-recipe"]["href"]
    requests.put(f"{API_BASE}{put_url}", headers=HEADERS, json=payload)
    stdscr.addstr(0, 0, "Recipe updated. Press any key to exit.")
    stdscr.getch()


def edit_recipeIngredients(stdscr, ingredients):
    """
    Display a menu to view and select recipe ingredients for editing.
    Args:
        stdscr: The curses window object used for terminal display.
        ingredients (list): A list of ingredient dictionaries
    """
    if not ingredients:
        stdscr.addstr(5, 0, "No ingredients found.")
        stdscr.getch()
        return

    idx = 0
    while True:
        options = [
            f"- {ing.get('ingredient_id')} ({ing.get('qty')}{ing.get('metric')})"
            for ing in ingredients
        ]
        render_menu(stdscr, "Recipe Ingredients", options + ["Back"], idx)
        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % (len(options) + 1)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % (len(options) + 1)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if idx == len(options):
                return
            ingredient = ingredients[idx]
            show_recipe_ingredient_details(stdscr, ingredient)


def show_review_details(stdscr, reviews):
    """
    Display a menu to view and delete recipe reviews.
    Args:
        stdscr: The curses window object used for terminal display.
        reviews (list): A list of review dictionaries.
    """
    if not reviews:
        stdscr.addstr(5, 0, "No reviews found.")
        stdscr.getch()
        return

    idx = 0
    while True:
        options = [
            f"- Review {rev.get('review_id')} (User: {rev.get('user_id')}, Rating: {rev.get('rating')})"
            for rev in reviews
        ]
        render_menu(stdscr, "Recipe Reviews", options + ["Back"], idx)
        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % (len(options) + 1)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % (len(options) + 1)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if idx == len(options):
                return
            review = reviews[idx]
            del_url = review["@controls"]["cookbook:delete-review"]["href"]
            requests.delete(f"{API_BASE}{del_url}", headers=HEADERS)
            stdscr.addstr(0, 0, "Recipe Review deleted. Press any key to exit.")
            stdscr.getch()
            return


def show_recipe_ingredient_details(stdscr, ingredient):
    """
    Display and handle actions for a specific recipe ingredient.
    Args:
        stdscr: The curses window object used for terminal display.
        ingredient (dict): A dictionary representing an ingredients.
    """
    options = ["Edit Recipe Ingredient", "Delete Recipe Ingredient", "Back"]
    idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(
            0, 0, f"Ingredient Id: {ingredient.get('ingredient_id')}", curses.A_BOLD
        )
        stdscr.addstr(
            1, 0, f"Qty and Metric: {ingredient.get('qty')}{ingredient.get('metric')}"
        )

        for i, opt in enumerate(options):
            mode = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(3 + i, 0, opt, mode)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            elif options[idx] == "Edit Recipe Ingredient":
                stdscr.clear()
                payload = {
                    "ingredient_id": int(ingredient["ingredient_id"]),
                    "qty": int(
                        get_user_input(stdscr, "New Quantity:") or ingredient["qty"]
                    ),
                    "metric": get_user_input(stdscr, "New Metric:")
                    or ingredient["metric"],
                }
                put_url = ingredient["@controls"]["cookbook:update-ingredient"]["href"]
                requests.put(f"{API_BASE}{put_url}", headers=HEADERS, json=payload)
                stdscr.addstr(0, 0, "Recipe Ingredient updated. Press any key to exit.")
                stdscr.getch()
                return
            elif options[idx] == "Delete Recipe Ingredient":
                stdscr.clear()
                payload = {
                    "ingredient_id": int(ingredient["ingredient_id"]),
                }
                del_url = ingredient["@controls"]["cookbook:delete-ingredient"]["href"]
                requests.delete(f"{API_BASE}{del_url}", headers=HEADERS, json=payload)
                stdscr.addstr(0, 0, "Recipe Ingredient deleted. Press any key to exit.")
                stdscr.getch()
                return


def show_ingredient_details(stdscr, href):
    """
    Fetch and display details of a standalone ingredient, with options to edit or delete.
    Args:
        stdscr: The curses window object used for terminal display.
        href (str): The relative URL to fetch the ingredient's data.
    """
    data = fetch_data(f"{API_BASE}{href}")
    options = ["Edit Ingredient", "Delete Ingredient", "Back"]
    idx = 0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f"Ingredient: {data.get('name')}", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Description: {data.get('description')}")

        for i, opt in enumerate(options):
            mode = curses.A_REVERSE if i == idx else curses.A_NORMAL
            stdscr.addstr(3 + i, 0, opt, mode)

        key = stdscr.getch()
        if key == curses.KEY_UP:
            idx = (idx - 1) % len(options)
        elif key == curses.KEY_DOWN:
            idx = (idx + 1) % len(options)
        elif key in (curses.KEY_ENTER, ord("\n")):
            if options[idx] == "Back":
                return
            elif options[idx] == "Edit Ingredient":
                stdscr.clear()
                stdscr.addstr(0, 0, "Editing Ingredient...", curses.A_BOLD)
                payload = {
                    "name": get_user_input(stdscr, "New name:") or data["name"],
                    "description": get_user_input(stdscr, "New description:")
                    or data.get("description", ""),
                }
                put_url = data["@controls"]["cookbook:update-ingredient"]["href"]
                requests.put(f"{API_BASE}{put_url}", headers=HEADERS, json=payload)
                stdscr.addstr(0, 0, "Ingredient updated. Press any key to exit.")
                stdscr.getch()
                return
            elif options[idx] == "Delete Ingredient":
                stdscr.clear()
                del_url = data["@controls"]["cookbook:delete-ingredient"]["href"]
                requests.delete(f"{API_BASE}{del_url}", headers=HEADERS)
                stdscr.addstr(0, 0, "Ingredient deleted. Press any key to exit.")
                stdscr.getch()
                return


def add_recipe(stdscr, href):
    """
    Prompt the user to input details for a new recipe and submit it via the API.
    Args:
        stdscr: The curses window object used for terminal display.
        href (str): The relative URL to post the new recipe data.
    """
    stdscr.clear()
    title = get_user_input(stdscr, "Enter recipe title:")
    description = get_user_input(stdscr, "Enter description:")
    steps = get_user_input(stdscr, "Enter steps (JSON string):")
    prep_time = get_user_input(stdscr, "Enter preparation time:")
    cook_time = get_user_input(stdscr, "Enter cooking time:")
    serving_input = get_user_input(stdscr, "Enter number of servings:")
    serving = int(serving_input) if serving_input.strip() else -1
    userid_input = get_user_input(stdscr, "Enter number of user ID:")
    user_id = int(userid_input) if userid_input.strip() else -1

    if (
        not title
        or not description
        or not steps
        or not prep_time
        or not cook_time
        or serving == -1
        or user_id == -1
    ):
        stdscr.addstr(0, 0, "All fields are required. Press any key to exit.")
        stdscr.getch()
        return

    payload = {
        "title": title,
        "description": description,
        "steps": steps,
        "preparation_time": prep_time,
        "cooking_time": cook_time,
        "serving": serving,
        "user_id": user_id,
    }

    response = post_data(f"{API_BASE}{href}", payload)
    stdscr.addstr(
        0,
        0,
        "Recipe created successfully. Press any key to exit."
        if response.status_code == 201
        else "Failed to create recipe.",
    )
    stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(tui_main)
