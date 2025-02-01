# Project Features Summary

## Database Table Setup
- **Table Creation**: A `patching_schedule` table is created with the following columns:
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

## Data Insertion
- **Sample Data**: A script is provided to insert 100 sample records into the `patching_schedule` table.
- **Randomized Values**: Sample data includes random values for each column, with `start_time` and `end_time` set within the current and next two months.

## Flask Application
- **Server Setup**: A Flask app is set up to serve data and handle requests.
- **Endpoints**:
  - Fetch unique `Deployment_IDs` sorted alphabetically.
  - Fetch unique `locations` sorted alphabetically, optionally filtered by `Deployment_ID`.
  - Fetch events based on filters such as `start`, `end`, `deployment_id`, `environment`, and `location`.

## Frontend with FullCalendar
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

## Filter Functionality
- **Dropdown Filters**: Available for `Deployment_ID`, `environment`, and `location`.
- **Dynamic Location Filter**: The `location` dropdown updates dynamically based on the selected `Deployment_ID`.
- **Event Filtering**: Filters are applied to the calendar view, allowing users to refine the events displayed based on their selections.

## Export Functionality
- **Excel Export**: An export feature is provided to download the filtered events as an Excel file, with the filename indicating the date range of the events.
