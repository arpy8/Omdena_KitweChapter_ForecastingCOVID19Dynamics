import pandas as pd
import streamlit as st
import joblib
import os

# Define preprocessing function
def preprocess(main_dataframe, dataframe_with_last_known_value):
    """
    Preprocess the main dataframe by subtracting values from the dataframe_with_last_known_value.

    Parameters:
    main_dataframe (pd.DataFrame): The main dataframe containing 14 features. 
                                   This dataframe is expected to have one row of user input.
    dataframe_with_last_known_value (pd.DataFrame): The dataframe containing 6 features and their known values.
                                                    This dataframe is expected to have one row with known values.

    Returns:
    pd.DataFrame: A new dataframe with the same structure as the main_dataframe, 
                  where the values of the 6 matching features have been subtracted 
                  by their corresponding values in the dataframe_with_last_known_value.
    """
    # Identify the common columns
    common_columns = main_dataframe.columns.intersection(dataframe_with_last_known_value.columns)

    # Subtract the values of the known features
    for column in common_columns:
        main_dataframe[column] = main_dataframe[column] - dataframe_with_last_known_value[column]
        if main_dataframe[column].iloc[0] < 0:
            main_dataframe[column] = 0
    return main_dataframe

@st.cache_resource
def load_model():
    # Load the model
    model_path = 'model/xgb_model_total_imputed_cases.pkl'

    if not os.path.exists(model_path):
        st.error(f" Model file not found at {model_path}. Please check the path and try again.")
        return 
    
    try:
        model = joblib.load(model_path)
    except Exception as e:
        st.error(f"An error occured while loading the model: {e}")
        return 
    return model

# Main function to display the Streamlit app
def main():
    st.title("COVID-19 Case Prediction :mask:")

    st.markdown("""
    ### Enter the required features to predict the total imputed COVID-19 cases.
    Please provide the values for the following features:
    """)
    st.write("**Note:** The minimum values for 'fullyVaccinated', 'partiallyVaccinated' , 'totalVaccinations' and 'totalTests' are the last known values as on 21st April 2024.")

    st.divider()
    
    col1,col2 = st.columns(2)
    feature_list = [
        'fullyVaccinated', 'new_deaths_smoothed', 'new_people_vaccinated_smoothed', 
        'new_vaccinations_smoothed', 'partiallyVaccinated', 'stringency_index', 
        'test24hours', 'totalTests', 'totalVaccinations', 'vaccinated24hours', 
        'rfh', 'r3h', 'month', 'day_of_week'
    ]
    
    with col1:
        fullyVaccinated = st.number_input("**fullyVaccinated**", min_value=9327654, step=1, help="Number of individuals who have completed the full vaccination regimen for COVID-19")
        new_deaths_smoothed = st.number_input("**new_deaths_smoothed**", min_value=0.0, help="New deaths attributed to COVID-19 (7-day smoothed). Counts can include probable deaths, where reported.")
        new_people_vaccinated_smoothed = st.number_input("**new_people_vaccinated_smoothed**", min_value=0.0, help="Daily number of people receiving their first vaccine dose(7-day smoothed)")
        new_vaccinations_smoothed = st.number_input("**new_vaccinations_smoothed**", min_value=0.0, help="New COVID-19 vaccination doses administered (7-day smoothed)")
        partiallyVaccinated = st.number_input("**partiallyVaccinated**", min_value=4663827, step=1, help="Number of individuals who have received at least one dose of a COVID-19 vaccine but have not yet completed the full vaccination regimen.")
        stringency_index = st.number_input("**stringency_index**", min_value=0.0, max_value=100.0, help="Government response composite measure based on 9 response indicators including school/workplace closures,and travel bans, value from 0 to 100(100=strictest)")
        test24hours = st.number_input("**test24hours**", min_value=0.0, help="Number of tests conducted in the last 24 hours")
    with col2:  
        totalTests = st.number_input("**totalTests**", min_value=4166833, help="Total number of tests for COVID-19")
        totalVaccinations = st.number_input("**totalVaccinations**", min_value=9982068, step=1, help="Total number of COVID-19 vaccination doses administered")
        vaccinated24hours = st.number_input("**vaccinated24hours**", min_value=0.0, help="Number of people vaccinated within a 24-hour period")
        rfh = st.number_input("**rfh**", min_value=0.0, step=0.001, help="10 day rainfall in mm")
        r3h = st.number_input("**r3h**", min_value=0.0, step=0.001, help="Rainfall 1-month rolling aggregation long term average in mm")
        month = st.number_input("**month**", min_value=1, max_value=12, help="The month in the year with January=1, December=12")
        day_of_week = st.number_input("**day_of_week**", min_value=0, max_value=6, help="The day of the week with Monday=0, Sunday=6")
        
    st.divider()

    input_df = pd.DataFrame({
            'fullyVaccinated': [fullyVaccinated],
            'new_deaths_smoothed': [new_deaths_smoothed],
            'new_people_vaccinated_smoothed': [new_people_vaccinated_smoothed],
            'new_vaccinations_smoothed': [new_vaccinations_smoothed],
            'partiallyVaccinated': [partiallyVaccinated],
            'stringency_index' : [stringency_index],
            'test24hours': [test24hours],
            'totalTests': [totalTests],
            'totalVaccinations': [totalVaccinations],
            'vaccinated24hours': [vaccinated24hours],
            'rfh': [rfh],
            'r3h': [r3h],
            'month':[month],
            'day_of_week': [day_of_week],
            })
    
    st.markdown("**Note:** The non-stationary features are differenced to make the data stationary.")

    # Preprocess the input data
    differenced_features = {
        'fullyVaccinated': 9327654, 'new_people_vaccinated_smoothed': 959,
        'partiallyVaccinated': 4663827, 'stringency_index': 13.89, 'totalTests': 4166833, 'totalVaccinations': 9982068
    }

    differencing_data = pd.DataFrame([differenced_features])

    preprocessed_data = preprocess(input_df, differencing_data)

    # Make prediction
    if st.button("**Predict**"):
        # Load the pre-trained model for predictions
        model = load_model()
        st.write("**You have submitted the below data.**")
        st.write(input_df)
        try:
            prediction = model.predict(preprocessed_data)
            st.success(f"Predicted Total Imputed Cases: {prediction[0]: .3f}")  #Display the results upto three decimal places
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

