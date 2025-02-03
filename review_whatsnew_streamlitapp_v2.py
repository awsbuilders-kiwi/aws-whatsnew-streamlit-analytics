version = "V1.15 - Jan 2025"
last_scaped_date = "04/02/2025"

import streamlit as st
import json
import pandas as pd
from time import sleep
import os
from pathlib import Path


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

    # Filter data based on selected year
    if selected_year != "All Years":
        filtered_data = data[data["Date"].dt.year == selected_year]
    else:
        filtered_data = data

    # Group data by category and count posts
    category_counts = filtered_data.groupby(filtered_data["Category"]).size()
    total_count = category_counts.sum()

    # Display summary
    st.subheader(f"Posts per Category ({total_count})")

    # Create bar chart
    st.bar_chart(category_counts)


def show_reports_content(selected_option, all_data):
    if selected_option == "Posts Per Year":
        display_posts_per_year(all_data)
    elif selected_option == "Posts Per Category":
        display_posts_per_category(all_data)
    elif selected_option == "Mission":
        st.write("Our Mission")
        st.success("To provide exceptional service...")


def show_filtered_data_contents(selected_option, filtered_data, group_by, show_link):
    st.markdown(f"Results found: {len(filtered_data)}")
    # Show filtered data
    if len(filtered_data) > 0:
        # Group data
        if group_by == "Day of Month":
            grouped_data = filtered_data.groupby(filtered_data["Date"].dt.date)
            # Iterate
            # for date, group in grouped_data:
            for date, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                # Write the date as a header
                st.markdown(f"**{date.strftime('%d/%m/%Y')}**")

                # List all titles for that date
                # for _, row in group.iterrows():
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        st.markdown(f"- {row['Title']} [Link]({row['Link']})")
                    else:
                        st.markdown(f"- {row['Title']}")
                # Add some spacing between date groups
                st.markdown("")
        elif group_by == "Month":
            grouped_data = filtered_data.groupby(
                filtered_data["Date"].dt.to_period("M")
            )
            # Iterate
            # for month, group in grouped_data:
            for month, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                # Write the month as a header
                st.markdown(f"**{month}**")

                # List all titles for that month
                # for _, row in group.iterrows():
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        st.markdown(f"- {row['Title']} [Link]({row['Link']})")
                    else:
                        st.markdown(f"- {row['Title']}")

                # Add some spacing between month groups
                st.markdown("")
        elif group_by == "Year":
            grouped_data = filtered_data.groupby(filtered_data["Date"].dt.year)
            # Iterate
            # for year, group in grouped_data:
            for year, group in sorted(grouped_data, key=lambda x: x[0], reverse=True):
                # Write the year as a header
                st.markdown(f"**{year}**")

                # List all titles for that year
                # for _, row in group.iterrows():
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        st.markdown(f"- {row['Title']} [Link]({row['Link']})")
                    else:
                        st.markdown(f"- {row['Title']}")

                # Add some spacing between year groups
                st.markdown("")
        elif group_by == "Category":
            grouped_data = filtered_data.groupby(filtered_data["Category"])
            # Iterate
            # for category, group in grouped_data:
            for category, group in sorted(grouped_data):
                # Write the date as a header
                st.markdown(f"**{category}**")

                # List all titles for that date
                # for _, row in group.iterrows():
                for _, row in group.sort_values("Date", ascending=False).iterrows():
                    if show_link:
                        st.markdown(
                            f"- {row['Title']}  [{row['Date'].strftime('%d/%m/%Y')}] [Link]({row['Link']})"
                        )
                    else:
                        st.markdown(
                            f"- {row['Title']}  [{row['Date'].strftime('%d/%m/%Y')}]"
                        )

                # Add some spacing between date groups
                st.markdown("")
        elif group_by == "Services":
            # Explode the Services list column
            exploded_df = filtered_data.explode("Services")
            # Remove duplicates within each service group
            exploded_df = exploded_df.drop_duplicates(
                subset=["Services", "Title", "Date"]
            )
            grouped_data = exploded_df.groupby("Services")
            # Iterate
            # for service, group in grouped_data:
            for service, group in sorted(grouped_data):
                # Write the service as a header
                st.markdown(f"**{service}**")

                # Get unique entries for this service group
                unique_group = group.drop_duplicates(subset=["Title", "Date"])

                # List all titles for that service
                # for _, row in group.iterrows():
                for _, row in unique_group.sort_values(
                    "Date", ascending=False
                ).iterrows():
                    if show_link:
                        st.markdown(
                            f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}] [Link]({row['Link']})"
                        )
                    else:
                        st.markdown(
                            f"- {row['Title']} [{row['Date'].strftime('%d/%m/%Y')}]"
                        )

                # Add some spacing between service groups
                st.markdown("")
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
            st.markdown("---")
            show_filtered_data_contents(
                sidebar_option, filtered_df, group_by, show_link
            )
        else:  # Last Menu Item
            show_builders_content(sidebar_option)


if __name__ == "__main__":
    # Configure the page layout
    st.set_page_config(layout="wide")
    main()
