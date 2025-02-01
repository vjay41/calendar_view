# Server Patching Schedule Application

This project is a web application designed to manage and visualize server patching schedules. It provides a calendar interface with dynamic filtering and export capabilities.

## Features

### Database Table Setup
- **Table Creation**: A `patching_schedule` table is created with columns for:
  - `seal_id`
  - `deployment_id`
  - `application_name`
  - `asset_name`
  - `environment`
  - `location`
  - `asset_function`
  - `event_type`
  - `description`
  - `start_time`
  - `end_time`
- **Table Reset**: The table is dropped and recreated each time the data insertion script is run, ensuring a fresh start for testing and development.

### Data Insertion
- **Sample Data**: A script is provided to insert 100 sample records into the `patching_schedule` table.
- **Randomized Values**: Sample data includes random values for each column, with `start_time` and `end_time` set within the current and next two months.

### Flask Application
- **Server Setup**: A Flask app is set up to serve data and handle requests.
- **Endpoints**:
  - Fetch unique `Deployment_IDs` sorted alphabetically.
  - Fetch unique `locations` sorted alphabetically, optionally filtered by `Deployment_ID`.
  - Fetch events based on filters such as `start`, `end`, `deployment_id`, `environment`, and `location`.

### Frontend with FullCalendar
- **Calendar Interface**: Implemented using FullCalendar to display events from the `patching_schedule` table.
- **Event Color-Coding**: Events are color-coded based on `Deployment_ID`, with each ID assigned a unique color.
- **Tooltips**: Display detailed information for events, including:
  - `seal_id`
  - `deployment_id`
  - `application_name`
  - `asset_function`
  - `event_type`
  - `description`
  - `location`

### Filter Functionality
- **Dropdown Filters**: Available for `Deployment_ID`, `environment`, and `location`.
- **Dynamic Location Filter**: The `location` dropdown updates dynamically based on the selected `Deployment_ID`.
- **Event Filtering**: Filters are applied to the calendar view, allowing users to refine the events displayed based on their selections.

### Export Functionality
- **Excel Export**: An export feature is provided to download the filtered events as an Excel file, with the filename indicating the date range of the events.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/server-patching-schedule.git
   cd server-patching-schedule
2. **Set Up the Virtual Environment**:
    ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
4. **Set Up the Database**:
   - Ensure PostgreSQL is installed and running.
   - Update the database connection parameters in the script as needed.

5. **Run the Data Insertion Script**:
   ```bash
   python sample_data_insert.py
6. **Start the Flask Application**:
   ```bash
   python app.py
7. **Access the Application**:
   - Open your web browser and go to http://localhost:5000.

