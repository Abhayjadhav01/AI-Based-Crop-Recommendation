import streamlit as st
import config
import model
import ui

def main():
    st.set_page_config(page_title="Intelligent Crop Recommender", layout="wide")
    st.title("🌱 Intelligent Crop Recommendation System")
    st.markdown(
        """
        Welcome to the Crop Recommendation System! This app uses a machine learning model
        trained on your provided dataset to suggest the best crop for your land based on
        soil and weather conditions. Features include real weather API integration,
        data visualizations, and AI-powered recommendations.
        """
    )

    # Main mode selection with buttons
    if 'mode' not in st.session_state:
        st.session_state.mode = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🌱 Crop Recommendation", type="primary"):
            st.session_state.mode = "crop"
    with col2:
        if st.button("🌿 Disease Detection", type="primary"):
            st.session_state.mode = "disease"

    if st.session_state.mode == "crop":
        # Option to retrain model
        if st.button("Retrain Model"):
            model.train_and_save_model()
        model_instance = model.load_model()
        st.markdown("---")

        input_method = st.radio(
            "Choose your input method:",
            ("Manual Input", "Fetch from Location"),
            index=0
        )
        if input_method == "Manual Input":
            valid = ui.manual_input()
        else:
            ui.fetch_data()
            valid = True  # Assume valid for location fetch

        if valid:
            ui.display_parameters()
            if st.button("Get Crop Recommendation", type="primary"):
                ui.recommend_crops(model_instance)

        # Model Management and History in expanders
        with st.expander("Model Management"):
            if st.button("Retrain Model Now"):
                model.train_and_save_model()
            st.info("Model is cached and loaded automatically.")

        with st.expander("Recommendation History"):
            ui.show_history()

    elif st.session_state.mode == "disease":
        ui.disease_detection()

if __name__ == "__main__":
    main()
