import streamlit as st

from services.database_service import (
    init_db,
    create_complaint,
    get_complaints,
    update_status
)

from services.ai_service import analyze_complaint

from services.voice_service import transcribe_audio

from services.image_service import analyze_image

from services.rag_service import retrieve_knowledge


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Campus AI Assistant",
    page_icon="🎓",
    layout="wide"
)


# --------------------------------------------------
# INITIALIZE DATABASE
# --------------------------------------------------

init_db()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "complaint_text" not in st.session_state:
    st.session_state.complaint_text = ""


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title(
    "🎓 Multimodal AI-Based Campus Troubleshooting, Complaint & Resolution Assistant"
)

st.write(
    "Report campus problems using Text, Voice or Image."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Page",
    [
        "Student Complaint",
        "Complaint Tracking",
        "Admin Dashboard"
    ]
)


# ==================================================
# STUDENT COMPLAINT
# ==================================================

if page == "Student Complaint":

    st.header("📝 Submit Campus Problem")

    student_name = st.text_input(
        "Student Name"
    )

    student_id = st.text_input(
        "Student ID"
    )

    location = st.text_input(
        "Campus Location / Room Number"
    )

    input_type = st.radio(
        "Select Complaint Type",
        [
            "Text",
            "Voice",
            "Image"
        ],
        horizontal=True
    )


    # ------------------------------------------------
    # TEXT INPUT
    # ------------------------------------------------

    if input_type == "Text":

        complaint = st.text_area(
            "Describe your problem",
            height=150
        )

        if st.button(
            "🤖 Analyze Complaint"
        ):

            if not complaint:

                st.warning(
                    "Please enter your problem."
                )

            else:

                with st.spinner(
                    "AI is analyzing your complaint..."
                ):

                    knowledge = retrieve_knowledge(
                        complaint
                    )

                    analysis = analyze_complaint(
                        complaint,
                        knowledge
                    )

                    analysis["location"] = location

                    st.session_state.analysis = analysis

                    st.session_state.complaint_text = complaint


    # ------------------------------------------------
    # VOICE INPUT
    # ------------------------------------------------

    elif input_type == "Voice":

        audio = st.file_uploader(
            "Upload your voice recording",
            type=[
                "wav",
                "mp3",
                "m4a"
            ]
        )

        if st.button(
            "🎤 Transcribe and Analyze"
        ):

            if audio is None:

                st.warning(
                    "Please upload an audio file."
                )

            else:

                with st.spinner(
                    "Converting voice to text..."
                ):

                    text = transcribe_audio(
                        audio
                    )

                st.success(
                    "Voice converted successfully."
                )

                st.write(
                    "### Transcribed Complaint"
                )

                st.write(text)

                with st.spinner(
                    "AI is analyzing the complaint..."
                ):

                    knowledge = retrieve_knowledge(
                        text
                    )

                    analysis = analyze_complaint(
                        text,
                        knowledge
                    )

                    analysis["location"] = location

                    st.session_state.analysis = analysis

                    st.session_state.complaint_text = text


    # ------------------------------------------------
    # IMAGE INPUT
    # ------------------------------------------------

    elif input_type == "Image":

        image = st.file_uploader(
            "Upload an image of the problem",
            type=[
                "jpg",
                "jpeg",
                "png"
            ]
        )

        if image:

            st.image(
                image,
                caption="Uploaded Problem Image",
                width=400
            )

        if st.button(
            "🖼️ Analyze Image"
        ):

            if image is None:

                st.warning(
                    "Please upload an image."
                )

            else:

                with st.spinner(
                    "Vision AI is analyzing the image..."
                ):

                    image_analysis = analyze_image(
                        image
                    )

                    knowledge = retrieve_knowledge(
                        image_analysis
                    )

                    analysis = analyze_complaint(
                        image_analysis,
                        knowledge
                    )

                    analysis["location"] = location

                    st.session_state.analysis = analysis

                    st.session_state.complaint_text = image_analysis


    # ------------------------------------------------
    # DISPLAY AI RESULT
    # ------------------------------------------------

    if st.session_state.analysis:

        result = st.session_state.analysis

        st.divider()

        st.header(
            "🤖 AI Analysis Result"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Category",
                result.get(
                    "category",
                    "Unknown"
                )
            )

        with col2:

            st.metric(
                "Department",
                result.get(
                    "department",
                    "Unknown"
                )
            )

        with col3:

            st.metric(
                "Priority",
                result.get(
                    "priority",
                    "Medium"
                )
            )

        st.subheader(
            "🔎 Identified Problem"
        )

        st.write(
            result.get(
                "problem",
                ""
            )
        )

        st.subheader(
            "🛠️ Suggested Troubleshooting"
        )

        st.info(
            result.get(
                "solution",
                ""
            )
        )


        # --------------------------------------------
        # CREATE TICKET
        # --------------------------------------------

        st.subheader(
            "🎫 Complaint Ticket"
        )

        if st.button(
            "Create Complaint Ticket"
        ):

            ticket_id = create_complaint(

                student_name,

                student_id,

                result.get(
                    "department",
                    "Other"
                ),

                result.get(
                    "category",
                    "Other"
                ),

                location,

                st.session_state.complaint_text,

                result.get(
                    "priority",
                    "Medium"
                ),

                result.get(
                    "solution",
                    ""
                )
            )

            st.success(
                f"Complaint created successfully! Ticket ID: #{ticket_id}"
            )


# ==================================================
# COMPLAINT TRACKING
# ==================================================

elif page == "Complaint Tracking":

    st.header(
        "📋 Complaint Tracking"
    )

    complaints = get_complaints()

    if not complaints:

        st.info(
            "No complaints available."
        )

    else:

        for complaint in complaints:

            (
                ticket_id,
                student_name,
                student_id,
                department,
                category,
                location,
                description,
                priority,
                solution,
                status,
                created_at
            ) = complaint

            with st.expander(
                f"Ticket #{ticket_id} - {status}"
            ):

                st.write(
                    f"**Student:** {student_name}"
                )

                st.write(
                    f"**Student ID:** {student_id}"
                )

                st.write(
                    f"**Department:** {department}"
                )

                st.write(
                    f"**Category:** {category}"
                )

                st.write(
                    f"**Location:** {location}"
                )

                st.write(
                    f"**Priority:** {priority}"
                )

                st.write(
                    f"**Problem:** {description}"
                )

                st.write(
                    f"**Solution:** {solution}"
                )

                st.write(
                    f"**Status:** {status}"
                )

                st.write(
                    f"**Created:** {created_at}"
                )


# ==================================================
# ADMIN DASHBOARD
# ==================================================

elif page == "Admin Dashboard":

    st.header(
        "👨‍💼 Admin Dashboard"
    )

    complaints = get_complaints()

    total = len(complaints)

    pending = sum(
        1 for c in complaints
        if c[9] == "Pending"
    )

    assigned = sum(
        1 for c in complaints
        if c[9] == "Assigned"
    )

    progress = sum(
        1 for c in complaints
        if c[9] == "In Progress"
    )

    resolved = sum(
        1 for c in complaints
        if c[9] == "Resolved"
    )


    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total",
        total
    )

    col2.metric(
        "Pending",
        pending
    )

    col3.metric(
        "Assigned",
        assigned
    )

    col4.metric(
        "In Progress",
        progress
    )

    col5.metric(
        "Resolved",
        resolved
    )


    st.divider()

    for complaint in complaints:

        (
            ticket_id,
            student_name,
            student_id,
            department,
            category,
            location,
            description,
            priority,
            solution,
            status,
            created_at
        ) = complaint

        with st.expander(
            f"Ticket #{ticket_id} | {department} | {priority}"
        ):

            st.write(
                f"**Student:** {student_name}"
            )

            st.write(
                f"**Problem:** {description}"
            )

            st.write(
                f"**Location:** {location}"
            )

            st.write(
                f"**Current Status:** {status}"
            )

            new_status = st.selectbox(

                "Update Status",

                [
                    "Pending",
                    "Assigned",
                    "In Progress",
                    "Resolved"
                ],

                index=[
                    "Pending",
                    "Assigned",
                    "In Progress",
                    "Resolved"
                ].index(status),

                key=f"status_{ticket_id}"
            )

            if st.button(
                "Update",
                key=f"update_{ticket_id}"
            ):

                update_status(
                    ticket_id,
                    new_status
                )

                st.success(
                    "Status updated successfully."
                )

                st.rerun()