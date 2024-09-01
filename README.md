## Description

This Telegram bot is designed to remind users about upcoming birthdays. The bot allows users to save birthday information and retrieve a list of the nearest birthdays. The project is written in Python using the `aiogram` library and SQLite database for data storage.

### Features

1. **Adding Birthday Information:** 
   Users can save information about their contacts, including full names and birth dates.

2. **Daily Reminders:**
   The bot automatically sends reminders to users at a specific time if a birthday is occurring on that day.

3. **Displaying Upcoming Birthdays:**
   Users can request a list of birthdays happening within the next 30 days. The bot returns a sorted list of birthdays from the nearest to the furthest.

### Technologies Used

- **Python 3.8+**
- **Aiogram** — a library for building Telegram bots.
- **SQLite** — a database for storing user information and birthdays.
- **Asyncio** — for implementing asynchronous tasks and time management.

### Installation and Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/telegram-birthday-bot.git
    ```

2. Navigate to the project directory:
    ```bash
    cd telegram-birthday-bot
    ```

3. Install the necessary dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Create and set up the SQLite database:
    - Create the `users` table with the necessary fields to store user information and their birthdays.
    - Use the provided SQL queries to initialize the tables.

5. Run the bot:
    ```bash
    python main.py
    ```

### Example Usage

- Run the `/start` command to begin interacting with the bot.
- Add a new birthday through a guided dialog.
- Retrieve the list of upcoming birthdays using the "Upcoming Birthdays" command.
- Receive daily reminders of upcoming events.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
