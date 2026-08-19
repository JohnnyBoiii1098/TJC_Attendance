import flet as ft
import psycopg2
import math
import datetime
import os
import webbrowser

# --- Database Configuration ---
DB_CONFIG = {
    "host": "100.108.78.111",
    "port": 5432,
    "dbname": "TJC",
    "user": "postgres",
    "password": "Nevve80085"
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def solid_border(width_val, color_val):
    return ft.Border(
        top=ft.BorderSide(width_val, color_val),
        bottom=ft.BorderSide(width_val, color_val),
        left=ft.BorderSide(width_val, color_val),
        right=ft.BorderSide(width_val, color_val)
    )


def main(page: ft.Page):
    # --- Page Alignment & Setup ---
    page.title = "TJC Attendance"
    page.bgcolor = "#f3f4f6"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    block_radius = 8
    categories = ["Alto", "Bass", "Soprano", "Tenor", "Band", "Conductors"]

    def show_alert(message_text):
        page.snack_bar = ft.SnackBar(content=ft.Text(message_text, color="white"), bgcolor="#374151")
        page.snack_bar.open = True
        page.update()

    def card_container(card_content, card_width=None):
        return ft.Container(
            content=card_content,
            bgcolor="white",
            padding=25,
            border_radius=block_radius,
            width=card_width,
            border=solid_border(1, "#e5e7eb"),
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color="#00000010", offset=ft.Offset(0, 4))
        )

    content_container = ft.Container(expand=True)

    main_wrapper = ft.Container(
        content=content_container,
        width=1100,
        padding=25,
        alignment=ft.Alignment(0, -1),
        expand=True
    )

    def navigate(_, route_name):
        if route_name == "home":
            content_container.content = build_home_view()
        elif route_name == "add":
            content_container.content = build_add_view()
        elif route_name == "mark":
            content_container.content = build_mark_view()
        elif route_name == "viewer":
            content_container.content = build_viewer_view()
        elif route_name == "credits":
            content_container.content = build_credits_view()
        page.update()

    # --- Header / Navigation Bar ---
    page.appbar = ft.AppBar(
        title=ft.Row([
            ft.Container(
                content=ft.Text("TJC", weight=ft.FontWeight.BOLD, color="#D4AF37", size=18),
                bgcolor="#001f3f", padding=10, border_radius=block_radius
            ),
            ft.Text("Attendance Portal", weight=ft.FontWeight.BOLD, color="#ffffff", size=18)
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor="#001f3f",
        center_title=False,
        toolbar_height=70,
        actions=[
            ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color="white",
                icon_size=20,
                tooltip="Home",
                on_click=lambda event_arg: navigate(event_arg, "home")
            )
        ]
    )

    page.add(main_wrapper)

    # ==========================================
    # PAGE 1: HOME PAGE
    # ==========================================
    def build_home_view():
        return ft.Column([
            ft.Divider(height=50, color="transparent"),
            ft.Text("The Josephite Choir", size=40, weight=ft.FontWeight.BOLD, color="#1f2937"),
            ft.Text("For The Greater Glory Of God", size=18, italic=True, color="#6b7280"),
            ft.Divider(height=40, color="transparent"),
            ft.Row([
                card_container(ft.Column([
                    ft.Icon(ft.Icons.PERSON_ADD, size=40, color="#2563eb"),
                    ft.Text("Add Student", weight=ft.FontWeight.BOLD, size=16),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "add"),
                              bgcolor="#2563eb", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    card_width=200),

                card_container(ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=40, color="#16a34a"),
                    ft.Text("Mark Attendance", weight=ft.FontWeight.BOLD, size=16),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "mark"),
                              bgcolor="#16a34a", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    card_width=200),

                card_container(ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=40, color="#9333ea"),
                    ft.Text("Day Viewer & Print", weight=ft.FontWeight.BOLD, size=16),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "viewer"),
                              bgcolor="#9333ea", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    card_width=200),

                card_container(ft.Column([
                    ft.Icon(ft.Icons.CALCULATE, size=40, color="#ca8a04"),
                    ft.Text("Credits Calculator", weight=ft.FontWeight.BOLD, size=16),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "credits"),
                              bgcolor="#ca8a04", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    card_width=200),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=30, wrap=True)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    # ==========================================
    # PAGE 2: ADD STUDENT
    # ==========================================
    def build_add_view():
        student_name = ft.TextField(label="Full Name", border_radius=block_radius, width=300)
        reg_no = ft.TextField(label="Registration ID", border_radius=block_radius, width=300)
        part = ft.Dropdown(label="Select Category", options=[ft.DropdownOption(c) for c in categories],
                           border_radius=block_radius, width=300)

        def on_register(_):
            if not student_name.value or not reg_no.value or not part.value:
                show_alert("Please fill all fields.")
                return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO students (student_name, reg_no, part) VALUES (%s, %s, %s)',
                            (student_name.value, reg_no.value, part.value))
                conn.commit()
                conn.close()
                show_alert("Student added successfully!")
                student_name.value, reg_no.value, part.value = "", "", None
                page.update()
            except psycopg2.Error as ex:
                show_alert(f"Database Error: {ex}")

        return ft.Column([
            ft.Text("Register New Member", size=26, weight=ft.FontWeight.BOLD, color="#1f2937"),
            card_container(ft.Column([student_name, reg_no, part, ft.Divider(color="transparent"),
                                      ft.Button(content=ft.Text("Add Student", weight=ft.FontWeight.BOLD),
                                                on_click=on_register, bgcolor="#1f2937", color="white", height=50,
                                                width=300)], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                           card_width=400)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)

    # ==========================================
    # PAGE 3: MARK ATTENDANCE
    # ==========================================
    def build_mark_view():
        event_name = ft.TextField(label="Event Name (e.g. Sunday Mass)", border_radius=block_radius, expand=True)
        event_hours = ft.TextField(label="Duration (Hours)", value="2", keyboard_type=ft.KeyboardType.NUMBER,
                                   border_radius=block_radius, width=150)

        selected_time = datetime.datetime.now().time()

        def handle_time_change(_):
            nonlocal selected_time
            if time_picker.value:
                selected_time = time_picker.value
                time_btn.content = ft.Text(f"Time: {selected_time.strftime('%H:%M')}")
                page.update()

        time_picker = ft.TimePicker(on_change=handle_time_change)
        page.overlay.append(time_picker)

        time_btn = ft.Button(
            content=ft.Text(f"Time: {selected_time.strftime('%H:%M')}"),
            icon=ft.Icons.ACCESS_TIME,
            on_click=lambda _: setattr(time_picker, 'open', True) or page.update()
        )

        search_field = ft.TextField(
            label="Search by Reg No...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=block_radius,
            expand=True,
            on_change=lambda _: filter_roster()
        )

        attendance_list = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)
        switches_map = {}
        all_students_cache = []

        def render_filtered_list(rows):
            attendance_list.controls.clear()
            switches_map.clear()

            if not rows:
                attendance_list.controls.append(
                    ft.Text("No students found. Please add students first.", italic=True, color="grey"))
                page.update()
                return

            current_group = ""
            for row_data in rows:
                if row_data[2] != current_group:
                    current_group = row_data[2]
                    attendance_list.controls.append(
                        ft.Text(f"— {current_group} —", weight=ft.FontWeight.BOLD, size=18, color="#2563eb"))

                present_switch = ft.Switch(label="Present", value=False, active_color="#16a34a")
                switches_map[row_data[1]] = present_switch

                attendance_list.controls.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Column([ft.Text(row_data[0].upper(), weight=ft.FontWeight.BOLD),
                                       ft.Text(row_data[1], size=12, color="grey")]),
                            present_switch
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10, border=solid_border(1, "#e5e7eb")
                    )
                )
            page.update()

        def load_roster():
            nonlocal all_students_cache
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT student_name, reg_no, part FROM students ORDER BY part, student_name')
                all_students_cache = cur.fetchall()
                conn.close()
                render_filtered_list(all_students_cache)
            except psycopg2.Error as ex:
                show_alert(f"DB Error loading roster: {ex}")

        def filter_roster():
            query = search_field.value.strip().lower() if search_field.value else ""
            if not query:
                render_filtered_list(all_students_cache)
            else:
                filtered = [s for s in all_students_cache if query in s[1].lower()]
                render_filtered_list(filtered)

        def save_event(_):
            if not event_name.value or not event_hours.value:
                show_alert("Event Name and Duration required.")
                return
            if not switches_map:
                show_alert("No students available to save attendance for.")
                return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('BEGIN')

                today = datetime.date.today()
                hours = float(event_hours.value)
                full_event_title = f"{event_name.value} ({selected_time.strftime('%H:%M')})"

                cur.execute(
                    'INSERT INTO events (event_name, event_date, duration_hours) VALUES (%s, %s, %s) RETURNING event_id',
                    (full_event_title, today, hours))
                row_result = cur.fetchone()
                if row_result is not None:
                    event_id = row_result[0]
                    for reg_number, switch_ctrl in switches_map.items():
                        cur.execute('INSERT INTO attendance_logs (event_id, reg_no, is_present) VALUES (%s, %s, %s)',
                                    (event_id, reg_number, switch_ctrl.value))

                cur.execute('COMMIT')
                conn.close()
                show_alert("Event & Attendance Saved Successfully!")
                event_name.value = ""
                search_field.value = ""
                load_roster()
                page.update()
            except (psycopg2.Error, ValueError) as ex:
                show_alert(f"Error: {ex}")

        load_roster()

        return ft.Column([
            ft.Text("Mark Daily Attendance", size=26, weight=ft.FontWeight.BOLD, color="#1f2937"),
            card_container(ft.Column([
                ft.Row([event_name, event_hours]),
                ft.Row([time_btn]),
                ft.Row([search_field]),
                ft.Button(content=ft.Text("Save Event & Roster"), on_click=save_event, bgcolor="#16a34a", color="white",
                          height=45)
            ])),
            card_container(attendance_list, card_width=800)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # PAGE 4: DAY-WISE VIEWER & PRINT
    # ==========================================
    def build_viewer_view():
        selected_date = datetime.date.today()
        all_events_cache = []

        event_search = ft.TextField(
            label="Search Event Name...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=block_radius,
            expand=True,
            on_change=lambda _: filter_events()
        )

        event_dropdown = ft.Dropdown(label="Select Event on this Day", expand=True,
                                     on_select=lambda _: load_event_roster())
        roster_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("Name")), ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Part")),
                     ft.DataColumn(ft.Text("Status"))], rows=[])

        current_event_data = []

        def update_date(_):
            nonlocal selected_date
            if date_picker.value:
                selected_date = date_picker.value
                date_btn.content = ft.Text(str(selected_date))
                load_events_for_date()
                page.update()

        date_picker = ft.DatePicker(on_change=update_date)
        page.overlay.append(date_picker)

        def open_calendar(_):
            date_picker.open = True
            page.update()

        date_btn = ft.Button(content=ft.Text(str(selected_date)), icon=ft.Icons.CALENDAR_MONTH, on_click=open_calendar)

        def load_events_for_date():
            nonlocal all_events_cache
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT event_id, event_name, duration_hours FROM events WHERE event_date = %s',
                            (selected_date,))
                all_events_cache = cur.fetchall()
                conn.close()
                filter_events()
            except psycopg2.Error:
                pass

        def filter_events():
            query = event_search.value.strip().lower() if event_search.value else ""
            if not query:
                filtered = all_events_cache
            else:
                filtered = [e for e in all_events_cache if query in e[1].lower()]

            event_dropdown.options = [ft.DropdownOption(key=str(e[0]), text=f"{e[1]} ({e[2]} Hrs)") for e in filtered]
            event_dropdown.value = None
            roster_table.rows.clear()
            current_event_data.clear()
            page.update()

        def load_event_roster():
            if not event_dropdown.value: return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('''
                    SELECT s.student_name, s.reg_no, s.part, a.is_present 
                    FROM students s 
                    JOIN attendance_logs a ON s.reg_no = a.reg_no 
                    WHERE a.event_id = %s 
                    ORDER BY s.part, s.student_name
                ''', (int(event_dropdown.value),))
                rows = cur.fetchall()
                conn.close()

                roster_table.rows.clear()
                current_event_data.clear()

                for r in rows:
                    status_text = "Present" if r[3] else "Absent"
                    color = "#16a34a" if r[3] else "#ef4444"
                    current_event_data.append([r[0], r[1], r[2], status_text])

                    roster_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(r[0])), ft.DataCell(ft.Text(r[1])), ft.DataCell(ft.Text(r[2])),
                        ft.DataCell(ft.Text(status_text, color=color, weight=ft.FontWeight.BOLD))
                    ]))
                page.update()
            except psycopg2.Error:
                pass

        # --- HTML GENERATION TO LOCAL FOLDER ---
        def generate_html_report(_):
            if not current_event_data:
                show_alert("No event selected to print.")
                return

            event_name_str = "Unknown Event"
            event_duration_str = "0"
            for e in all_events_cache:
                if str(e[0]) == event_dropdown.value:
                    event_name_str = str(e[1])
                    event_duration_str = str(e[2])
                    break

            # Save it securely to a local 'assets' folder inside the project
            assets_dir = os.path.join(os.getcwd(), "assets")
            os.makedirs(assets_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%H%M%S")
            filename = f"TJC_Attendance_{str(selected_date)}_{timestamp}.html"
            file_path = os.path.join(assets_dir, filename)

            try:
                # Build the HTML content
                html_content = f"""
                <html>
                <head>
                    <title>Attendance Report - {selected_date}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; padding: 30px; margin: auto; max-width: 900px; }}
                        h1 {{ text-align: center; color: #1f2937; margin-bottom: 5px; text-transform: uppercase; }}
                        h3 {{ text-align: center; color: #6b7280; margin-top: 0; margin-bottom: 5px; }}
                        h4 {{ text-align: center; color: #6b7280; margin-top: 0; margin-bottom: 30px; font-weight: normal; }}
                        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
                        th, td {{ border: 1px solid #e5e7eb; padding: 12px; text-align: left; }}
                        th {{ background-color: #f3f4f6; color: #374151; font-weight: bold; }}
                        tr:nth-child(even) {{ background-color: #fafafa; }}
                        .present {{ color: #16a34a; font-weight: bold; text-align: center; }}
                        .absent {{ color: #dc2626; font-weight: bold; text-align: center; }}
                        .num-col {{ text-align: center; width: 40px; color: #6b7280; }}
                    </style>
                </head>
                <body>
                    <h1>{event_name_str}</h1>
                    <h3>The Josephite Choir - Attendance Report</h3>
                    <h4>Date: {selected_date} &nbsp; | &nbsp; Duration: {event_duration_str} Hours</h4>
                    <table>
                        <tr>
                            <th class="num-col">#</th>
                            <th>Student Name</th>
                            <th>Reg No</th>
                            <th>Category</th>
                            <th style="text-align: center;">Status</th>
                        </tr>
                """

                for index, row in enumerate(current_event_data, start=1):
                    status_class = "present" if row[3] == "Present" else "absent"
                    html_content += f"""
                        <tr>
                            <td class="num-col">{index}</td>
                            <td>{row[0]}</td>
                            <td>{row[1]}</td>
                            <td>{row[2]}</td>
                            <td class="{status_class}">{row[3]}</td>
                        </tr>
                    """

                html_content += """
                    </table>
                </body>
                </html>
                """

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)

                file_url = f"file:///{file_path.replace(os.sep, '/')}"

                # --- Create the UI Dialog using Flet 1.0 async clipboard ---
                async def copy_to_clipboard(e):
                    # Uses the Flet 1.0 standalone Clipboard service
                    await ft.Clipboard().set(file_url)
                    show_alert("Copied to clipboard! Paste it into Chrome or Edge.")

                def close_dialog(e):
                    success_dlg.open = False
                    page.update()

                success_dlg = ft.AlertDialog(
                    title=ft.Text("Report Generated!", color="#16a34a", weight=ft.FontWeight.BOLD),
                    content=ft.Column([
                        ft.Text(
                            "The report was saved securely inside the app's internal folder. Copy the link below and paste it into any web browser to view or print it.",
                            size=14, color="#374151"),
                        ft.TextField(value=file_url, read_only=True, border_radius=5, height=50, text_size=13,
                                     color="#2563eb", bgcolor="#f3f4f6")
                    ], tight=True, spacing=15),
                    actions=[
                        ft.Button(content=ft.Text("Copy URL"), icon=ft.Icons.COPY, on_click=copy_to_clipboard,
                                  bgcolor="#2563eb", color="white"),
                        ft.Button(content=ft.Text("Open in Browser"), icon=ft.Icons.OPEN_IN_BROWSER, url=file_url,
                                  bgcolor="#1f2937", color="white"),
                        ft.Button(content=ft.Text("Close"), on_click=close_dialog)
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )

                page.overlay.append(success_dlg)
                success_dlg.open = True
                page.update()

            except Exception as e:
                show_alert(f"Failed to generate report: {e}")

        load_events_for_date()

        return ft.Column([
            ft.Text("Historical Viewer & Print", size=26, weight=ft.FontWeight.BOLD, color="#1f2937"),
            card_container(ft.Column([
                ft.Row([date_btn, ft.Container(expand=True),
                        ft.Button(content=ft.Text("Generate Report"), on_click=generate_html_report,
                                  icon=ft.Icons.PRINT, bgcolor="#dc2626", color="white")]),
                ft.Divider(color="transparent", height=5),
                ft.Row([event_search, event_dropdown])
            ])),
            card_container(ft.Column([roster_table], scroll=ft.ScrollMode.AUTO), card_width=800)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # PAGE 5: CREDITS CALCULATOR
    # ==========================================
    def build_credits_view():
        part_filter = ft.Dropdown(
            options=[ft.DropdownOption("All Parts")] + [ft.DropdownOption(c) for c in categories],
            value="All Parts", width=250, border_radius=block_radius,
            on_select=lambda _: load_credits()
        )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Category", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Total Hrs", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Credits", weight=ft.FontWeight.BOLD)),
            ],
            rows=[], border=solid_border(1, "#e5e7eb"), border_radius=block_radius, heading_row_color="#f9fafb"
        )

        def load_credits():
            try:
                conn = get_db_connection()
                cur = conn.cursor()

                query = '''
                    SELECT s.student_name, s.reg_no, s.part, COALESCE(SUM(e.duration_hours), 0) as total_hours
                    FROM students s
                    LEFT JOIN attendance_logs a ON s.reg_no = a.reg_no AND a.is_present = TRUE
                    LEFT JOIN events e ON a.event_id = e.event_id
                '''
                if part_filter.value != "All Parts":
                    query += f" WHERE s.part = '{part_filter.value}'"

                query += " GROUP BY s.reg_no ORDER BY total_hours DESC"
                cur.execute(query)
                rows = cur.fetchall()
                conn.close()

                table.rows.clear()
                for row_data in rows:
                    hours = float(row_data[3])
                    credits_earned = math.floor(abs(hours / 30))
                    table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(row_data[0].upper(), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(row_data[1])),
                        ft.DataCell(ft.Text(row_data[2])),
                        ft.DataCell(ft.Text(str(hours), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(str(credits_earned), color="#ca8a04", weight=ft.FontWeight.BOLD)),
                    ]))
                page.update()
            except psycopg2.Error as ex:
                show_alert(f"Error: {ex}")

        load_credits()

        return ft.Column([
            card_container(
                ft.Row([ft.Text("Credits Ledger", size=26, weight=ft.FontWeight.BOLD, color="#1f2937"), part_filter],
                       alignment=ft.MainAxisAlignment.SPACE_BETWEEN)),
            ft.Row([card_container(ft.Column([table], scroll=ft.ScrollMode.AUTO))],
                   alignment=ft.MainAxisAlignment.CENTER)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    navigate(None, "home")


ft.run(main)