version = "V1.15 - Jan 2025"
last_scaped_date = "01/03/2025"

import streamlit as st
import json
import pandas as pd
from time import sleep
import os
from pathlib import Path
import calendar


def show_about_content(selected_option):
    st.write(
        "This app is allows more review of the AWS Whats New feed : https://aws.amazon.com/new/"
    )
    st.write("Is a WIP! :D")


def display_posts_per_year(data):
    # Group data by year and count posts
    # Get total count first for verification
    total_count = len(data)

    # Group by year and count, ensuring we don't double count
    yearly_counts = data.groupby(data["Date"].dt.year).agg({"Title": "count"}).squeeze()

    # Add verification comment
    st.write(f"Total records: {total_count}")
    # Display summary
    st.subheader("Posts per Year")

    # Create bar chart
    st.bar_chart(yearly_counts)


def display_posts_per_category(data):
    # Get unique years from the data
    years = data["Date"].dt.year.unique().tolist()
    years.sort(reverse=True)
    years.insert(0, "All Years")

    # Create year selector dropdown
    selected_year = st.selectbox(
        "Select Year", years, index=1
    )  # Default to first year (most recent)

    selected_month = None
    if selected_year != "All Years":
        # Get months for selected year
        months_data = data[data["Date"].dt.year == selected_year]
        months = months_data["Date"].dt.month.unique().tolist()
        months.sort()
        months.insert(0, "All Months")
        
        # Create month selector dropdown
        selected_month = st.selectbox(
            "Select Month",
            months,
            format_func=lambda x: "All Months" if x == "All Months" else calendar.month_name[x]
        )

    # Filter data based on selections
    if selected_year != "All Years":
        if selected_month != "All Months":
            filtered_data = data[
                (data["Date"].dt.year == selected_year) &
                (data["Date"].dt.month == selected_month)
            ]
        else:
            filtered_data = data[data["Date"].dt.year == selected_year]
    else:
        filtered_data = data

    # Group data by category and count posts
    category_counts = filtered_data.groupby(filtered_data["Category"]).size()
    total_count = category_counts.sum()

    # Display summary
    period_text = (
        "All Time" if selected_year == "All Years"
        else f"{calendar.month_name[selected_month]} {selected_year}" if selected_month and selected_month != "All Months"
        else str(selected_year)
    )
    st.subheader(f"Posts per Category - {period_text} ({total_count})")

    # Optionally keep the bar chart
    st.bar_chart(category_counts)

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        st.write("Number of Posts")
        for category, count in sorted(category_counts.items(), key=lambda x: x[0]):
            st.write(str(count))

    with col2:
        st.write("Category")
        for category, count in sorted(category_counts.items(), key=lambda x: x[0]):
            st.write(category)

    # Add spacing
    st.markdown("---")

    # Add combined table sorted by count
    st.subheader("Combined View (Sorted by Post Count)")
    st.markdown("| Number of Posts | Category |")
    st.markdown("|----------------|----------|")
    for category, count in sorted(
        category_counts.items(), key=lambda x: x[1], reverse=True
    ):
        st.markdown(f"| {count} | {category} |")



    col1, col2 = st.columns(2)

    with col1:
        # Create year selector dropdown
        selected_year = st.selectbox(
            "Select Year", years, index=1
        )  # Default to first year (most recent)

    with col2:
        # Create month selector dropdown
        months = [
            "All Months",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        selected_month = st.selectbox("Select Month", months)

    # Filter data based on selected year and month
    if selected_year != "All Years":
        filtered_data = data[data["Date"].dt.year == selected_year]
        if selected_month != "All Months":
            # Convert month name to number (1-12)
            month_num = months.index(selected_month)
            filtered_data = filtered_data[filtered_data["Date"].dt.month == month_num]
    else:
        filtered_data = data
        if selected_month != "All Months":
            month_num = months.index(selected_month)
            filtered_data = filtered_data[filtered_data["Date"].dt.month == month_num]

    # Group data by category and count posts
    category_counts = filtered_data.groupby(filtered_data["Category"]).size()
    total_count = category_counts.sum()

    # Display summary
    if selected_month != "All Months" and selected_year != "All Years":
        st.subheader(
            f"Posts per Category for {selected_month} {selected_year} ({total_count})"
        )
    elif selected_month != "All Months":
        st.subheader(
            f"Posts per Category for {selected_month} (All Years) ({total_count})"
        )
    elif selected_year != "All Years":
        st.subheader(f"Posts per Category for {selected_year} ({total_count})")
    else:
        st.subheader(f"Posts per Category (All Time) ({total_count})")

    # Optionally keep the bar chart
    st.bar_chart(category_counts)

    # Create two columns for the data display
    col1, col2 = st.columns(2)

    with col1:
        st.write("Number of Posts")
        for category, count in sorted(category_counts.items(), key=lambda x: x[0]):
            st.write(str(count))

    with col2:
        st.write("Category")
        for category, count in sorted(category_counts.items(), key=lambda x: x[0]):
            st.write(category)

    # Add spacing
    st.markdown("---")

    # Add combined table sorted by count
    st.subheader("Combined View (Sorted by Post Count)")
    st.markdown("| Number of Posts | Category |")
    st.markdown("|----------------|----------|")
    for category, count in sorted(
        category_counts.items(), key=lambda x: x[1], reverse=True
    ):
        st.markdown(f"| {count} | {category} |")


def get_top_service_by_year(data, year):
    year_data = data[data['Date'].dt.year == year]
    service_counts = year_data['Services'].value_counts()
    if not service_counts.empty:
        return service_counts.index[0], service_counts.iloc[0]
    return None, 0

def get_category_summary(data, period_type, period_value):
    if period_type == 'year':
        filtered_data = data[data['Date'].dt.year == period_value]
    else:  # month
        filtered_data = data[
            (data['Date'].dt.year == period_value[0]) & 
            (data['Date'].dt.month == period_value[1])
        ]
    return filtered_data['Category'].value_counts()

def get_category_trends(data, months_lookback):
    end_date = data['Date'].max()
    start_date = end_date - pd.DateOffset(months=months_lookback)
    mask = (data['Date'] >= start_date) & (data['Date'] <= end_date)
    trend_data = data[mask]
    
    trends = trend_data.groupby([pd.Grouper(key='Date', freq='M'), 'Category']).size().unstack(fill_value=0)
    return trends

def show_reports_content(selected_option, all_data):
    if selected_option == "Posts Per Year":
        display_posts_per_year(all_data)
    elif selected_option == "Posts Per Category":
        display_posts_per_category(all_data)
    elif selected_option == "Top Service Analysis":
        st.subheader("Top Service by Year")
        year = st.selectbox("Select Year", sorted(all_data['Date'].dt.year.unique(), reverse=True))
        top_service, count = get_top_service_by_year(all_data, year)
        if top_service:
            st.write(f"Top service in {year}: **{top_service}** with {count} announcements")
            
    elif selected_option == "Category Summary":
        st.subheader("Category Summary")
        period_type = st.radio("Select Period Type", ["Month", "Year"])
        if period_type == "Year":
            year = st.selectbox("Select Year", sorted(all_data['Date'].dt.year.unique(), reverse=True))
            summary = get_category_summary(all_data, 'year', year)
            st.bar_chart(summary)
        else:
            col1, col2 = st.columns(2)
            with col1:
                year = st.selectbox("Select Year", sorted(all_data['Date'].dt.year.unique(), reverse=True))
            with col2:
                month = st.selectbox("Select Month", range(1, 13))
            summary = get_category_summary(all_data, 'month', (year, month))
            st.bar_chart(summary)
            
    elif selected_option == "Category Trends":
        st.subheader("Category Trends")
        year = st.selectbox("Select Year", sorted(all_data['Date'].dt.year.unique(), reverse=True))
        trend_period = st.radio("Select Trend Period", ["1 Month", "6 Months"])
        months = 1 if trend_period == "1 Month" else 6
        trends = get_category_trends(all_data, months)
        st.line_chart(trends)
        
    elif selected_option == "Mission":
        st.write("Our Mission")
        st.success("To provide exceptional service...")


def show_filtered_data_contents(
    selected_option, filtered_data, group_by, show_link, use_markdown
):
    st.markdown(f"Results found: {len(filtered_data)}")
    # Show filtered data
    if len(filtered_data) > 0:
        # Group data
        if group_by == "Day of Month":
            grouped_data = filtered_data.groupby(filtered_data["Date"].dt.date)
            # Iterate
            for date, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                if use_markdown:
                    st.text(f"## {date.strftime('%d/%m/%Y')}")
                else:
                    st.write(date.strftime("%d/%m/%Y"))

                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        if use_markdown:
                            st.text(f"* {row['Title']} [Link]({row['Link']})")
                        else:
                            st.write(f"- {row['Title']} (Link: {row['Link']})")
                    else:
                        if use_markdown:
                            st.text(f"* {row['Title']}")
                        else:
                            st.write(f"- {row['Title']}")
                if use_markdown:
                    st.text("")
                else:
                    st.write("")

        elif group_by == "Month":
            grouped_data = filtered_data.groupby(
                filtered_data["Date"].dt.to_period("M")
            )
            # Iterate
            for month, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                # Write the month as a header
                if use_markdown:
                    st.text(f"## {month}")
                else:
                    st.write(f"{month}")

                # List all titles for that month
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        if use_markdown:
                            st.text(f"* {row['Title']} [Link]({row['Link']})")
                        else:
                            st.write(f"- {row['Title']} (Link: {row['Link']})")
                    else:
                        if use_markdown:
                            st.text(f"* {row['Title']}")
                        else:
                            st.write(f"- {row['Title']}")

                # Add some spacing between month groups
                if use_markdown:
                    st.text("")
                else:
                    st.write("")

        elif group_by == "Year":
            grouped_data = filtered_data.groupby(filtered_data["Date"].dt.year)
            # Iterate
            for year, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                # Write the year as a header
                if use_markdown:
                    st.text(f"## {year}")
                else:
                    st.write(f"{year}")

                # List all titles for that year
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        if use_markdown:
                            st.text(f"* {row['Title']} [Link]({row['Link']})")
                        else:
                            st.write(f"- {row['Title']} (Link: {row['Link']})")
                    else:
                        if use_markdown:
                            st.text(f"* {row['Title']}")
                        else:
                            st.write(f"- {row['Title']}")

                # Add some spacing between year groups
                if use_markdown:
                    st.text("")
                else:
                    st.write("")

        elif group_by == "Category":
            grouped_data = filtered_data.groupby(filtered_data["Category"])
            # Iterate
            for category, group in sorted(grouped_data):
                # Write the category as a header
                if use_markdown:
                    st.text(f"## {category}")
                else:
                    st.write(f"{category}")

                # List all titles for that category
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        if use_markdown:
                            st.text(
                                f"* {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}] [Link]({row['Link']})"
                            )
                        else:
                            st.write(
                                f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}] (Link: {row['Link']})"
                            )
                    else:
                        if use_markdown:
                            st.text(
                                f"* {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}]"
                            )
                        else:
                            st.write(
                                f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}]"
                            )

                # Add some spacing between category groups
                if use_markdown:
                    st.text("")
                else:
                    st.write("")

        elif group_by == "Services":
            # Explode the Services list column
            exploded_df = filtered_data.explode("Services")
            # Remove duplicates within each service group
            exploded_df = exploded_df.drop_duplicates(
                subset=["Services", "Title", "Date"]
            )
            grouped_data = exploded_df.groupby("Services")
            # Iterate
            for service, group in sorted(grouped_data):
                # Write the service as a header
                if use_markdown:
                    st.text(f"## {service}")
                else:
                    st.write(f"{service}")

                # Get unique entries for this service group
                unique_group = group.drop_duplicates(subset=["Title", "Date"])

                # List all titles for that service
                for _, row in unique_group.sort_values(
                    "Date", ascending=False
                ).iterrows():
                    if show_link:
                        if use_markdown:
                            st.text(
                                f"* {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}] [Link]({row['Link']})"
                            )
                        else:
                            st.write(
                                f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}] (Link: {row['Link']})"
                            )
                    else:
                        if use_markdown:
                            st.text(
                                f"* {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}]"
                            )
                        else:
                            st.write(
                                f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}]"
                            )

                # Add some spacing between service groups
                if use_markdown:
                    st.text("")
                else:
                    st.write("")
    else:
        st.write("No announcements found for the selected filters.")


def generate_report_1(df):
    st.subheader("Summary of Announcements")


def process_json_file(input_file_path):
    try:
        # Open and load the JSON file
        with open(input_file_path, "r") as file:
            # Read the entire file content
            file_content = file.read()
            # Parse JSON
            data = json.loads(file_content)

            return data

    except Exception as e:
        print(f"Error processing {input_file_path}: {str(e)}")


def load_whats_new_data():
    directory = "scraped_data"
    # Initialize an empty list to store all records
    all_records = []
    # Process each JSON file in the directory and its subdirectories
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if (
                filename.endswith("_withservices.json")
                and filename != "aws_whats_new-all_withservices.json"
            ):
                input_file_path = os.path.join(root, filename)
                print(f"Filename!: {input_file_path}")
                file_data = process_json_file(input_file_path)
                # print(json.dumps(file_data, indent=4))
                if file_data is not None:
                    # If file_data is a list, extend all_records
                    if isinstance(file_data, list):
                        print("File data is a list")
                        all_records.extend(file_data)
                    # If file_data is a single record, append it
                    else:
                        print("File data is a single record")
                        all_records.append(file_data)

    # Create DataFrame only if we have records
    if not all_records:
        st.error("No data found in the JSON files.")
        return None

    # Create DataFrame from all records
    data = pd.DataFrame(all_records)

    # Convert dates with explicit format
    data["Date"] = pd.to_datetime(data["Date"], format="%d/%m/%Y", dayfirst=True)

    # Check if any data is returned
    if data.empty:
        st.error("No data found in the JSON files.")
        return None

    return data


def filter_data(df, category, year, month, day):
    if category and category != "All":
        df = df[df["Category"] == category]
    if year:
        df = df[df["Date"].dt.year == int(year)]
    if month:
        df = df[df["Date"].dt.month == int(month)]
    if day:
        df = df[df["Date"].dt.day == int(day)]
    return df


def main():
    # Initialize session state for data if not already present
    if "whats_new_data" not in st.session_state:
        data = load_whats_new_data()
        if data is not None:
            st.session_state.whats_new_data = data
        else:
            st.error("Cannot proceed without data. Please check the data file.")
            return

    # Initialize session state for active menu if not already present
    if "active_menu" not in st.session_state:
        st.session_state.active_menu = "About"

    # Top menu bar
    with st.container():
        col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment="top")
        with col1:
            if st.button("About"):
                st.session_state.active_menu = "About"
        with col2:
            if st.button("Reports"):
                st.session_state.active_menu = "Reports"
        with col3:
            if st.button("Whats New Data Filter"):
                st.session_state.active_menu = "Whats New Data Filter"
        with col4:
            st.write(
                "-= " + version + " .:.  Last Scraped: " + last_scaped_date + " =-"
            )
    st.markdown("---")

    # Create two columns - sidebar and main content
    col_sidebar, col_main = st.columns([1, 4])

    # Sidebar content based on active menu
    with col_sidebar:
        # st.subheader(f"{st.session_state.active_menu} Menu")

        # Different options for each menu
        if st.session_state.active_menu == "About":
            sidebar_option = st.write("-= Review AWS What's New App =-")
        elif st.session_state.active_menu == "Reports":
            sidebar_option = st.selectbox(
                "Select Report",
                ["Posts Per Year", "Posts Per Category", "Top Service Analysis", 
                 "Category Summary", "Category Trends"]
            )
            st.write("Author: Paul Dunlop + Amazon Q For Developers")
            st.write(version)
            st.write("Last Scraped: " + last_scaped_date)
            st.write("Proudly sponsored by: HTTPS://AWSBUILDERS.KIWI")
        elif st.session_state.active_menu == "Reports":
            sidebar_option = st.radio(
                "Choose an option:",
                ["Posts Per Year", "Posts Per Category", "Top Service"],
            )
        elif st.session_state.active_menu == "Whats New Data Filter":
            sidebar_option = "Results"

            st.header("Filter")

            # Category filter
            categories = st.session_state.whats_new_data["Category"].unique()
            category = st.selectbox("Select a Category", ["All"] + list(categories))

            # Services filter
            all_services = set()
            for services in st.session_state.whats_new_data["Services"]:
                all_services.update(services)
            service = st.selectbox(
                "Select a Service", ["All"] + sorted(list(all_services))
            )

            # Get current month and year
            current_month = pd.Timestamp.now().month
            current_year = pd.Timestamp.now().year

            # Date filters
            years = [None] + sorted(
                list(st.session_state.whats_new_data["Date"].dt.year.unique()),
                reverse=True,
            )

            # year_index = years.index(current_year) if current_year in years else 0
            year_index = 1
            year = st.selectbox("Select Year", years, index=year_index)
            month = st.selectbox("Select Month", [None] + list(range(1, 13)))
            day = st.selectbox("Select Day", [None] + list(range(1, 32)))

            # Group by options
            group_by = st.selectbox(
                "Group Results By",
                ["Day of Month", "Month", "Year", "Category", "Services"],
            )

            # Show link in results checkbox
            show_link = st.checkbox("Show Link?")

            # Filter the data
            filtered_df = filter_data(
                st.session_state.whats_new_data, category, year, month, day
            )
            if service != "All":
                filtered_df = filtered_df[
                    filtered_df["Services"].apply(lambda x: service in x)
                ]

    # Main content area
    with col_main:
        # Display content based on active menu and sidebar selection
        if st.session_state.active_menu == "About":
            show_about_content(sidebar_option)
        elif st.session_state.active_menu == "Reports":
            show_reports_content(sidebar_option, st.session_state.whats_new_data)
        elif st.session_state.active_menu == "Whats New Data Filter":
            st.write(f"Category: {category}, Year: {year},  Month: {month}, Day: {day}")
            st.write(f"Group By: {group_by} ")
            use_markdown = st.checkbox("Use Markdown Formatting", value=True)
            st.markdown("---")
            show_filtered_data_contents(
                sidebar_option, filtered_df, group_by, show_link, use_markdown
            )
        else:  # Last Menu Item
            show_builders_content(sidebar_option)


if __name__ == "__main__":
    # Configure the page layout
    st.set_page_config(layout="wide")
    main()
