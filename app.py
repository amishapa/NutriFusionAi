import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# Configure Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyCWstlyb7sX06AqWTtyHP0FhhUnJcugT84")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize session state
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        'goals': 'Lose 10 pounds in 3 months\nImprove cardiovascular health',
        'conditions': 'None',
        'routines': '30-min walk 3x/week',
        'preferences': 'Vegetarian\nLow carb',
        'restrictions': 'No dairy\nNo nuts'
    }


# Function to get Gemini response
def get_gemini_response(input_prompt, image_data=None):
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        content = [input_prompt]
        if image_data:
            content.extend(image_data)

        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"


# Function to process uploaded image
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None


# Streamlit UI
st.set_page_config(page_title="AI Health Companion", layout="wide")
st.header("🧑‍⚕️ AI Health Companion")

# Sidebar for health profile
with st.sidebar:
    st.subheader("Your Health Profile")

    health_goals = st.text_area("Health Goals", value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Medical Conditions", value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Fitness Routines", value=st.session_state.health_profile['routines'])
    food_preference = st.text_area("Food Preferences", value=st.session_state.health_profile['preferences'])
    restrictions = st.text_area("Dietary Restrictions", value=st.session_state.health_profile['restrictions'])

    if st.button("Update Profile"):
        st.session_state.health_profile = {
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preference,
            'restrictions': restrictions
        }
        st.success("✅ Profile updated!")


# Tabs for features
tab1, tab2, tab3 = st.tabs(["🍽 Meal Planning", "📷 Food Analysis", "💡 Health Insights"])

# -------- Meal Planning --------
with tab1:
    st.subheader("Personalized Meal Planning")

    col1, col2 = st.columns(2)

    with col1:
        user_input = st.text_area("Describe any specific requirements for your meal plan:",
                                  placeholder="e.g., 'I need quick meals for work days'")

    with col2:
        st.write("### Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalized Meal Plan"):
        if not any(st.session_state.health_profile.values()):
            st.warning("⚠️ Please complete your health profile in the sidebar first.")
        else:
            with st.spinner("Creating your personalized meal plan..."):
                prompt = f"""
                Create a personalized meal plan based on the following health profile:

                Health Goals: {st.session_state.health_profile['goals']}
                Medical Conditions: {st.session_state.health_profile['conditions']}
                Fitness Routines: {st.session_state.health_profile['routines']}
                Food Preferences: {st.session_state.health_profile['preferences']}
                Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                Additional requirements: {user_input if user_input else "None provided"}

                Provide:
                1. A 7-day meal plan with breakfast, lunch, dinner, and snacks
                2. Nutritional breakdown for each day (calories, macros)
                3. Explanations for why each meal was chosen
                4. A categorized shopping list
                """

                response = get_gemini_response(prompt)

                st.subheader("🍱 Your Personalized Meal Plan")
                st.markdown(response)

                st.download_button(
                    label="📥 Download Meal Plan",
                    data=response,
                    file_name="personalized_meal_plan.txt",
                    mime="text/plain"
                )

# -------- Food Analysis --------
with tab2:
    st.subheader("Food Analysis")

    uploaded_file = st.file_uploader("Upload an image of your food", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)

        if st.button("Analyze Food"):
            with st.spinner("Analyzing your food..."):
                image_data = input_image_setup(uploaded_file)

                prompt = """
                You are an expert nutritionist. Analyze this food image.

                Provide detailed information about:
                - Estimated calories
                - Macronutrient breakdown
                - Potential health benefits
                - Any concerns based on common dietary restrictions
                - Suggested portion size

                If multiple items are present, analyze each separately.
                """

                response = get_gemini_response(prompt, image_data)
                st.subheader("🍎 Food Analysis Result")
                st.markdown(response)

# -------- Health Insights --------
with tab3:
    st.subheader("Health Insights")

    health_query = st.text_input("Ask any health question",
                                 placeholder="e.g., 'How can I improve my gut health?'")

    if st.button("Get Expert Insights"):
        if not health_query:
            st.warning("⚠️ Please enter a health question")
        else:
            with st.spinner("Researching your question..."):
                prompt = f"""
                You are a certified nutritionist and health expert.
                Provide detailed, science-based insights about:

                {health_query}

                Include:
                1. Explanation of the science
                2. Practical recommendations
                3. Precautions
                4. References to studies (if available)
                5. Suggested foods/supplements if appropriate

                Use simple language but maintain accuracy.
                """
                response = get_gemini_response(prompt)
                st.subheader("💡 Expert Health Insights")
                st.markdown(response)
