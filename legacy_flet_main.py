import flet as ft
import psycopg2
import math
import datetime
import os
import sys

# --- Database Configuration ---
DB_CONFIG = {
    "host": "127.0.0.1",
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


async def main(page: ft.Page):
    # --- Page Alignment & Responsive Setup (STRETCH ENABLED) ---
    page.title = "TJC Attendance"
    page.bgcolor = "#f3f4f6"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    page.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
    page.scroll = ft.ScrollMode.AUTO

    block_radius = 8
    categories = ["Alto", "Bass", "Soprano", "Tenor", "Band", "Conductors"]

    # --- BRAND COLORS ---
    NAVY = "#001f3f"
    GOLD = "#D4AF37"

    # --- ALERTS & POPUPS ---
    def show_alert(message_text):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message_text, color=GOLD, weight=ft.FontWeight.BOLD),
            bgcolor=NAVY
        )
        page.snack_bar.open = True
        page.update()

    def show_success_popup(title_text, message_text):
        def close_popup(e):
            popup.open = False
            page.update()

        popup = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=GOLD),
                ft.Text(title_text, color=NAVY, weight=ft.FontWeight.BOLD)
            ]),
            content=ft.Text(message_text, size=14),
            actions=[ft.Button(content=ft.Text("OK"), on_click=close_popup, bgcolor=NAVY, color=GOLD)],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(popup)
        popup.open = True
        page.update()

    def card_container(card_content, expand_val=False):
        return ft.Container(
            content=card_content,
            bgcolor="white",
            padding=20,
            border_radius=block_radius,
            border=solid_border(1, "#e5e7eb"),
            shadow=ft.BoxShadow(blur_radius=15, spread_radius=2, color="#00000010", offset=ft.Offset(0, 4)),
            expand=expand_val
        )

    content_container = ft.Container(expand=True)

    main_wrapper = ft.Container(
        content=content_container,
        padding=15,
        expand=True
    )

    # --- ROCK SOLID NAVIGATION ---
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
                content=ft.Text("TJC", weight=ft.FontWeight.BOLD, color=GOLD, size=18),
                bgcolor=NAVY, padding=10, border_radius=block_radius,
                border=solid_border(1, GOLD)
            ),
            ft.Text("Attendance Portal", weight=ft.FontWeight.BOLD, color="#ffffff", size=16)
        ], alignment=ft.MainAxisAlignment.START),
        bgcolor=NAVY,
        center_title=False,
        toolbar_height=70,
        actions=[
            ft.IconButton(
                icon=ft.Icons.HOME,
                icon_color=GOLD,
                icon_size=24,
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
            ft.Container(height=20),
            ft.Text("The Josephite Choir", size=32, weight=ft.FontWeight.BOLD, color=NAVY,
                    text_align=ft.TextAlign.CENTER),
            ft.Text("For The Greater Glory Of God", size=16, italic=True, color=GOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(height=30),

            ft.ResponsiveRow([
                ft.Container(card_container(ft.Column([
                    ft.Icon(ft.Icons.PERSON_ADD, size=35, color=NAVY),
                    ft.Text("Add Student", weight=ft.FontWeight.BOLD, size=15),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "add"),
                              bgcolor=NAVY, color=GOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    col={"sm": 6, "xs": 12}),

                ft.Container(card_container(ft.Column([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, size=35, color=NAVY),
                    ft.Text("Mark Attendance", weight=ft.FontWeight.BOLD, size=15),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "mark"),
                              bgcolor=NAVY, color=GOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    col={"sm": 6, "xs": 12}),

                ft.Container(card_container(ft.Column([
                    ft.Icon(ft.Icons.CALENDAR_MONTH, size=35, color=NAVY),
                    ft.Text("Day Viewer & Print", weight=ft.FontWeight.BOLD, size=15),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "viewer"),
                              bgcolor=NAVY, color=GOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    col={"sm": 6, "xs": 12}),

                ft.Container(card_container(ft.Column([
                    ft.Icon(ft.Icons.CALCULATE, size=35, color=NAVY),
                    ft.Text("Credits Calculator", weight=ft.FontWeight.BOLD, size=15),
                    ft.Button(content=ft.Text("Open"), on_click=lambda event_arg: navigate(event_arg, "credits"),
                              bgcolor=NAVY, color=GOLD)
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)),
                    col={"sm": 6, "xs": 12}),
            ], spacing=20)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # ==========================================
    # PAGE 2: ADD STUDENT
    # ==========================================
    def build_add_view():
        student_name = ft.TextField(label="Full Name", border_radius=block_radius, expand=True)
        reg_no = ft.TextField(label="Registration ID", border_radius=block_radius, expand=True)
        part = ft.Dropdown(
            label="Select Category",
            options=[ft.dropdown.Option(key=c, text=c) for c in categories],
            border_radius=block_radius,
            expand=True
        )

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

                show_success_popup("Student Registered!",
                                   f"{student_name.value} has been successfully added to the {part.value} section.")

                student_name.value, reg_no.value, part.value = "", "", None
                page.update()
            except psycopg2.Error as ex:
                show_alert(f"Database Error: {ex}")

        return ft.Column([
            ft.Text("Register New Member", size=24, weight=ft.FontWeight.BOLD, color=NAVY),
            card_container(ft.Column([
                student_name,
                reg_no,
                part,
                ft.Container(height=10),
                ft.Row([ft.Button(content=ft.Text("Add Student", weight=ft.FontWeight.BOLD), on_click=on_register,
                                  bgcolor=NAVY, color=GOLD, height=50, expand=True)])
            ]), expand_val=False)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # ==========================================
    # PAGE 3: MARK ATTENDANCE
    # ==========================================
    def build_mark_view():
        event_name = ft.TextField(label="Event Name", border_radius=block_radius, expand=True)
        event_hours = ft.TextField(label="Hours", value="2", keyboard_type=ft.KeyboardType.NUMBER,
                                   border_radius=block_radius, width=100)

        selected_time = datetime.datetime.now().time()

        def handle_time_change(_):
            nonlocal selected_time
            if time_picker.value:
                selected_time = time_picker.value
                time_btn.content = ft.Text(f"{selected_time.strftime('%H:%M')}")
                page.update()

        time_picker = ft.TimePicker(on_change=handle_time_change)
        page.overlay.append(time_picker)

        time_btn = ft.Button(
            content=ft.Text(f"{selected_time.strftime('%H:%M')}"),
            icon=ft.Icons.ACCESS_TIME,
            on_click=lambda _: setattr(time_picker, 'open', True) or page.update(),
            height=50,
            bgcolor=NAVY,
            color=GOLD
        )

        selected_mark_date = datetime.date.today()

        def handle_date_change(_):
            nonlocal selected_mark_date
            if date_picker.value:
                selected_mark_date = date_picker.value.date() if isinstance(date_picker.value,
                                                                            datetime.datetime) else date_picker.value
                date_btn.content = ft.Text(str(selected_mark_date))
                page.update()

        date_picker = ft.DatePicker(on_change=handle_date_change)
        page.overlay.append(date_picker)

        date_btn = ft.Button(
            content=ft.Text(str(selected_mark_date)),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=lambda _: setattr(date_picker, 'open', True) or page.update(),
            height=50,
            bgcolor=NAVY,
            color=GOLD
        )

        search_field = ft.TextField(
            label="Search Name or ID...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=block_radius,
            expand=True
        )

        part_filter = ft.Dropdown(
            options=[ft.dropdown.Option(key="All Parts", text="All Parts")] + [ft.dropdown.Option(key=c, text=c) for c
                                                                               in categories],
            value="All Parts",
            border_radius=block_radius,
            expand=True
        )

        attendance_list = ft.ListView(expand=True, spacing=10)
        switches_map = {}
        all_students_cache = []

        def render_filtered_list(rows):
            new_controls = []
            switches_map.clear()

            if not rows:
                new_controls.append(ft.Text("No students found.", italic=True, color="grey"))
            else:
                current_group = ""
                for row_data in rows:
                    if row_data[2] != current_group:
                        current_group = row_data[2]
                        new_controls.append(
                            ft.Text(f"{current_group}", weight=ft.FontWeight.BOLD, size=16, color=NAVY))

                    present_switch = ft.Switch(value=False, active_color="#16a34a")
                    switches_map[row_data[1]] = present_switch

                    new_controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(row_data[0].upper(), weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(row_data[1], size=12, color="grey")
                                ], spacing=2, expand=True),
                                present_switch
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=10, border=solid_border(1, "#e5e7eb"), border_radius=5
                        )
                    )

            attendance_list.controls = new_controls
            page.update()

        def load_roster():
            nonlocal all_students_cache
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('SELECT student_name, reg_no, part FROM students ORDER BY part, student_name')
                all_students_cache = cur.fetchall()
                conn.close()
                filter_roster()
            except psycopg2.Error as ex:
                show_alert(f"DB Error: {ex}")

        def filter_roster(e=None):
            query = search_field.value.strip().lower() if search_field.value else ""
            if e:
                if hasattr(e, "control") and e.control and e.control.value:
                    part_filter.value = e.control.value
                elif hasattr(e, "data") and e.data:
                    part_filter.value = e.data

            selected_part = part_filter.value or "All Parts"

            filtered = []
            for s in all_students_cache:
                matches_search = not query or query in s[1].lower() or query in s[0].lower()
                matches_part = selected_part == "All Parts" or selected_part == s[2]

                if matches_search and matches_part:
                    filtered.append(s)

            render_filtered_list(filtered)

        search_field.on_change = filter_roster
        part_filter.on_change = filter_roster

        def save_event(_):
            if not event_name.value or not event_hours.value:
                show_alert("Event Name and Duration required.")
                return
            if not switches_map:
                show_alert("No students available.")
                return
            try:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('BEGIN')

                hours = float(event_hours.value)
                full_event_title = f"{event_name.value} ({selected_time.strftime('%H:%M')})"

                cur.execute(
                    'INSERT INTO events (event_name, event_date, duration_hours) VALUES (%s, %s, %s) RETURNING event_id',
                    (full_event_title, selected_mark_date, hours))
                row_result = cur.fetchone()
                if row_result is not None:
                    event_id = row_result[0]
                    for reg_number, switch_ctrl in switches_map.items():
                        cur.execute('INSERT INTO attendance_logs (event_id, reg_no, is_present) VALUES (%s, %s, %s)',
                                    (event_id, reg_number, switch_ctrl.value))

                cur.execute('COMMIT')
                conn.close()

                show_success_popup("Attendance Saved!",
                                   f"The attendance for '{full_event_title}' on {selected_mark_date} has been recorded.")

                event_name.value = ""
                search_field.value = ""
                part_filter.value = "All Parts"
                load_roster()
            except (psycopg2.Error, ValueError) as ex:
                show_alert(f"Error: {ex}")

        load_roster()

        return ft.Column([
            ft.Text("Mark Attendance", size=24, weight=ft.FontWeight.BOLD, color=NAVY),
            card_container(ft.Column([
                ft.Row([event_name, event_hours]),
                ft.Row([search_field, date_btn, time_btn]),
                ft.Row([part_filter]),
                ft.Row([ft.Button(content=ft.Text("Save Event", weight=ft.FontWeight.BOLD), on_click=save_event,
                                  bgcolor=NAVY, color=GOLD, height=45, expand=True)])
            ]), expand_val=False),
            card_container(attendance_list, expand_val=True)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # ==========================================
    # PAGE 4: DAY-WISE VIEWER & PRINT
    # ==========================================
    def build_viewer_view():
        selected_date = datetime.date.today()
        all_events_cache = []

        event_search = ft.TextField(
            label="Search Event...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=block_radius,
            expand=True
        )

        event_dropdown = ft.Dropdown(
            label="Select Event",
            expand=True
        )

        roster_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Part")),
                ft.DataColumn(ft.Text("Status"))
            ],
            rows=[],
            expand=True
        )

        current_event_data = []

        def update_date(_):
            nonlocal selected_date
            if date_picker_view.value:
                selected_date = date_picker_view.value.date() if isinstance(date_picker_view.value,
                                                                            datetime.datetime) else date_picker_view.value
                date_btn_view.content = ft.Text(str(selected_date))
                load_events_for_date()
                page.update()

        date_picker_view = ft.DatePicker(on_change=update_date)
        page.overlay.append(date_picker_view)

        def open_calendar(_):
            date_picker_view.open = True
            page.update()

        date_btn_view = ft.Button(
            content=ft.Text(str(selected_date)),
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=open_calendar,
            height=50,
            bgcolor=NAVY,
            color=GOLD
        )

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
            except psycopg2.Error as ex:
                show_alert(f"DB Error loading dates: {ex}")

        def filter_events(e=None):
            query = event_search.value.strip().lower() if event_search.value else ""
            if not query:
                filtered = all_events_cache
            else:
                filtered = [ev for ev in all_events_cache if query in ev[1].lower()]

            event_dropdown.options = [ft.dropdown.Option(key=str(ev[0]), text=f"{ev[1]} ({ev[2]}h)") for ev in filtered]
            event_dropdown.value = None
            roster_table.rows.clear()
            current_event_data.clear()
            page.update()

        def load_event_roster(e=None):
            if e:
                if hasattr(e, "control") and e.control and e.control.value:
                    event_dropdown.value = e.control.value
                elif hasattr(e, "data") and e.data:
                    event_dropdown.value = e.data

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
            except psycopg2.Error as ex:
                show_alert(f"DB Error loading roster: {ex}")

        event_search.on_change = filter_events
        event_dropdown.on_change = load_event_roster

        def generate_report(_):
            if not current_event_data:
                show_alert("No event selected.")
                return

            event_name_str = "Unknown Event"
            event_duration_str = "0"
            for e in all_events_cache:
                if str(e[0]) == event_dropdown.value:
                    event_name_str = str(e[1])
                    event_duration_str = str(e[2])
                    break

            script_dir = os.path.dirname(os.path.abspath(__file__))
            assets_dir = os.path.join(script_dir, "assets")
            os.makedirs(assets_dir, exist_ok=True)

            timestamp = datetime.datetime.now().strftime("%H%M%S")
            html_filename = f"Report_{timestamp}.html"
            csv_filename = f"Report_{timestamp}.csv"

            html_path = os.path.join(assets_dir, html_filename)
            csv_path = os.path.join(assets_dir, csv_filename)

            html_content = f"""
            <html>
            <head>
                <title>Report - {selected_date}</title>
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: sans-serif; padding: 20px; max-width: 900px; margin: auto; }}
                    h2 {{ text-align: center; color: {NAVY}; margin-bottom: 5px; text-transform: uppercase; }}
                    h4 {{ text-align: center; color: {GOLD}; font-weight: bold; margin-top: 0; }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ border: 1px solid #e5e7eb; padding: 10px; text-align: left; }}
                    th {{ background-color: {NAVY}; color: {GOLD}; }}
                    .present {{ color: #16a34a; font-weight: bold; }}
                    .absent {{ color: #dc2626; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h2>{event_name_str}</h2>
                <h4>{selected_date} | {event_duration_str} Hours</h4>
                <table>
                    <tr><th>Name</th><th>Reg No</th><th>Part</th><th>Status</th></tr>
            """
            for row in current_event_data:
                status_class = "present" if row[3] == "Present" else "absent"
                html_content += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td class='{status_class}'>{row[3]}</td></tr>"
            html_content += "</table></body></html>"

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            csv_content = f"Event: {event_name_str}\nDate: {selected_date}\n\nName,ID,Part,Status\n"
            for row in current_event_data:
                csv_content += f"{row[0]},{row[1]},{row[2]},{row[3]}\n"

            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            html_url = f"/{html_filename}"
            csv_url = f"/{csv_filename}"

            def open_html(e):
                page.launch_url(html_url, web_popup_window_name="_blank")

            def open_csv(e):
                page.launch_url(csv_url, web_popup_window_name="_blank")

            def close_dialog(e):
                success_dlg.open = False
                page.update()

            success_dlg = ft.AlertDialog(
                title=ft.Text("Report Ready!", color=NAVY, weight=ft.FontWeight.BOLD),
                content=ft.Text("Choose a format to view or download:", size=14),
                actions=[
                    ft.Button(content=ft.Text("Webpage"), icon=ft.Icons.LANGUAGE, on_click=open_html, bgcolor=NAVY,
                              color=GOLD),
                    ft.Button(content=ft.Text("Spreadsheet"), icon=ft.Icons.TABLE_CHART, on_click=open_csv,
                              bgcolor=NAVY, color=GOLD),
                    ft.Button(content=ft.Text("Close"), on_click=close_dialog, bgcolor=NAVY, color=GOLD)
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

            try:
                page.overlay.append(success_dlg)
                success_dlg.open = True
                page.update()
            except Exception as e:
                show_alert(f"Failed to display: {e}")

        load_events_for_date()

        return ft.Column([
            ft.Text("Historical Viewer", size=24, weight=ft.FontWeight.BOLD, color=NAVY),
            card_container(ft.Column([
                ft.Row([date_btn_view, ft.Container(expand=True),
                        ft.IconButton(icon=ft.Icons.PRINT, icon_color=GOLD, bgcolor=NAVY, on_click=generate_report,
                                      tooltip="Generate Report")]),
                ft.Container(height=5),
                ft.Row([event_search]),
                ft.Row([event_dropdown])
            ]), expand_val=False),
            card_container(ft.Column([roster_table], scroll=ft.ScrollMode.AUTO, expand=True), expand_val=True)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # ==========================================
    # PAGE 5: CREDITS CALCULATOR (STRICT CATEGORY ISOLATION)
    # ==========================================
    def build_credits_view():
        part_filter = ft.Dropdown(
            options=[ft.dropdown.Option(key="All Parts", text="All Parts")] + [ft.dropdown.Option(key=c, text=c) for c
                                                                               in categories],
            value="All Parts", border_radius=block_radius, expand=True
        )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Category")),
                ft.DataColumn(ft.Text("Total Hrs")),
                ft.DataColumn(ft.Text("Credits")),
            ],
            rows=[],
            border=solid_border(1, "#e5e7eb"),
            border_radius=block_radius,
            heading_row_color="#f9fafb",
            expand=True
        )

        def load_credits(e=None):
            if e:
                if hasattr(e, "control") and e.control and e.control.value:
                    part_filter.value = e.control.value
                elif hasattr(e, "data") and e.data:
                    part_filter.value = e.data

            selected_filter = part_filter.value or "All Parts"

            try:
                conn = get_db_connection()
                cur = conn.cursor()

                query = '''
                    SELECT s.student_name, s.reg_no, s.part, COALESCE(SUM(ev.duration_hours), 0) as total_hours
                    FROM students s
                    LEFT JOIN attendance_logs a ON s.reg_no = a.reg_no AND a.is_present = TRUE
                    LEFT JOIN events ev ON a.event_id = ev.event_id
                '''

                params = []
                # Strict SQL isolation filter: Hides all other parts completely
                if selected_filter != "All Parts":
                    query += " WHERE s.part = %s"
                    params.append(selected_filter)

                query += " GROUP BY s.reg_no, s.student_name, s.part ORDER BY s.student_name ASC"

                cur.execute(query, tuple(params))
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
                        ft.DataCell(ft.Text(str(credits_earned), color=GOLD, weight=ft.FontWeight.BOLD)),
                    ]))

                table.update()
                page.update()

            except Exception as ex:
                show_alert(f"Filter Error: {ex}")

        part_filter.on_change = load_credits
        load_credits()

        return ft.Column([
            ft.Text("Credits Ledger", size=24, weight=ft.FontWeight.BOLD, color=NAVY),
            card_container(ft.Column([part_filter]), expand_val=False),
            card_container(ft.Column([table], scroll=ft.ScrollMode.AUTO, expand=True), expand_val=True)
        ], expand=True, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    # Boot the application safely directly to the Home View
    navigate(None, "home")


# --- THE FIX: Python's safety guard for web servers ---
if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
    os.makedirs(ASSETS_DIR, exist_ok=True)

    ft.run(
        main,
        assets_dir=ASSETS_DIR,
        port=8000,
        host="127.0.0.1",
        view=ft.AppView.WEB_BROWSER
    )